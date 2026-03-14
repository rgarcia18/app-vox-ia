"""
Pruebas unitarias — VoxIA AI Service

Cubre:
  - _parse_list: conversión de texto a lista
  - _truncate: truncado inteligente de texto
  - _is_bad_output: detección de salida inválida
  - generate_summary: resumen con mock del modelo
  - extract_key_points: puntos clave con mock
  - extract_tasks: tareas con mock
  - extract_decisions: decisiones con mock
  - process_audio_file: pipeline completo con mock

Ejecutar:
    cd backend
    python -m pytest tests/test_ai_service.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


# ─── Helpers internos ─────────────────────────────────────────────────────────

class TestParseList:
    def test_lista_numerada(self):
        from app.services.ai_service import _parse_list
        raw = "1. Primer punto importante\n2. Segundo punto clave\n3. Tercer aspecto"
        result = _parse_list(raw)
        assert len(result) == 3
        assert result[0] == "Primer punto importante"
        assert result[1] == "Segundo punto clave"

    def test_lista_con_guiones(self):
        from app.services.ai_service import _parse_list
        raw = "- Tarea uno pendiente\n- Tarea dos pendiente\n- Tarea tres pendiente"
        result = _parse_list(raw)
        assert len(result) == 3
        assert result[0] == "Tarea uno pendiente"

    def test_lista_vacia(self):
        from app.services.ai_service import _parse_list
        assert _parse_list("") == []
        assert _parse_list("   \n\n  ") == []

    def test_filtra_items_muy_cortos(self):
        from app.services.ai_service import _parse_list
        raw = "1. Ok\n2. Esta línea sí tiene contenido suficiente"
        result = _parse_list(raw)
        assert len(result) == 1
        assert "Esta línea sí tiene contenido suficiente" in result

    def test_lista_con_bullets(self):
        from app.services.ai_service import _parse_list
        raw = "• Decisión tomada uno\n* Decisión tomada dos"
        result = _parse_list(raw)
        assert len(result) == 2


class TestTruncate:
    def test_texto_corto_no_se_trunca(self):
        from app.services.ai_service import _truncate
        texto = "Texto corto"
        assert _truncate(texto, 100) == texto

    def test_texto_largo_se_trunca(self):
        from app.services.ai_service import _truncate
        texto = "Palabra " * 300  # 2400 chars
        result = _truncate(texto, 100)
        assert len(result) <= 100

    def test_trunca_en_ultimo_punto(self):
        from app.services.ai_service import _truncate
        texto = "Primera oración completa. Segunda oración que no debe aparecer completa aquí."
        result = _truncate(texto, 30)
        assert result.endswith(".")

    def test_texto_exactamente_al_limite(self):
        from app.services.ai_service import _truncate
        texto = "a" * 1200
        assert _truncate(texto, 1200) == texto


class TestIsBadOutput:
    def test_detecta_prompt_repetido_es(self):
        from app.services.ai_service import _is_bad_output
        assert _is_bad_output("Resume este texto en 3 oraciones")
        assert _is_bad_output("Lista 3 puntos importantes")
        assert _is_bad_output("Escribe un resumen ejecutivo")

    def test_detecta_prompt_repetido_en(self):
        from app.services.ai_service import _is_bad_output
        assert _is_bad_output("Summarize this text in 3 sentences")
        assert _is_bad_output("List 3 key points from this text")

    def test_acepta_salida_valida(self):
        from app.services.ai_service import _is_bad_output
        assert not _is_bad_output("La reunión trató sobre el presupuesto del proyecto.")
        assert not _is_bad_output("Se decidió posponer la entrega hasta el viernes.")
        assert not _is_bad_output("El equipo debe entregar el informe el lunes.")


# ─── Funciones de análisis (con mock del modelo) ──────────────────────────────

SAMPLE_TRANSCRIPT_ES = (
    "Buenos días a todos. Hoy vamos a revisar el avance del proyecto VoxIA. "
    "El equipo de backend completó la integración con Whisper. "
    "Se decidió usar FLAN-T5 base por limitaciones de recursos. "
    "Santiago debe entregar el README antes del viernes. "
    "Andrés se encargará de las pruebas unitarias. "
    "Se aprobó el diseño de la interfaz propuesto por David. "
    "La próxima reunión será el lunes a las 10am."
)

SAMPLE_TRANSCRIPT_EN = (
    "Good morning everyone. Today we will review the VoxIA project progress. "
    "The backend team completed the Whisper integration. "
    "It was decided to use FLAN-T5 base due to resource constraints. "
    "Santiago must deliver the README by Friday. "
)


class TestGenerateSummary:
    def test_texto_vacio_devuelve_mensaje(self):
        from app.services.ai_service import generate_summary
        result = generate_summary("", "es")
        assert "corto" in result.lower() or "no" in result.lower()

    def test_texto_muy_corto_devuelve_mensaje(self):
        from app.services.ai_service import generate_summary
        result = generate_summary("Hola.", "es")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("app.services.ai_service._run_flan")
    def test_summary_es_con_mock(self, mock_flan):
        from app.services.ai_service import generate_summary
        mock_flan.return_value = "El proyecto VoxIA avanza bien con integración de Whisper y FLAN-T5."
        result = generate_summary(SAMPLE_TRANSCRIPT_ES, "es")
        assert isinstance(result, str)
        assert len(result) > 10
        mock_flan.assert_called_once()

    @patch("app.services.ai_service._run_flan")
    def test_summary_en_con_mock(self, mock_flan):
        from app.services.ai_service import generate_summary
        mock_flan.return_value = "The VoxIA project is progressing with Whisper integration."
        result = generate_summary(SAMPLE_TRANSCRIPT_EN, "en")
        assert isinstance(result, str)
        assert len(result) > 10

    @patch("app.services.ai_service._run_flan")
    def test_bad_output_devuelve_fallback(self, mock_flan):
        from app.services.ai_service import generate_summary
        mock_flan.return_value = "Resume este texto en 3 oraciones: Buenos días..."
        result = generate_summary(SAMPLE_TRANSCRIPT_ES, "es")
        assert "no se pudo" in result.lower()


class TestExtractKeyPoints:
    def test_texto_vacio_devuelve_lista_vacia(self):
        from app.services.ai_service import extract_key_points
        assert extract_key_points("", "es") == []

    @patch("app.services.ai_service._run_flan")
    def test_key_points_con_mock(self, mock_flan):
        from app.services.ai_service import extract_key_points
        mock_flan.return_value = (
            "Se integró Whisper en el backend\n"
            "Se eligió FLAN-T5 base por recursos\n"
            "Santiago entregará el README el viernes"
        )
        result = extract_key_points(SAMPLE_TRANSCRIPT_ES, "es")
        assert isinstance(result, list)
        assert len(result) <= 5

    @patch("app.services.ai_service._run_flan")
    def test_filtra_bad_output(self, mock_flan):
        from app.services.ai_service import extract_key_points
        mock_flan.return_value = "Lista 3 puntos importantes de este texto:\n"
        result = extract_key_points(SAMPLE_TRANSCRIPT_ES, "es")
        assert result == []


class TestExtractTasks:
    def test_texto_vacio_devuelve_lista_vacia(self):
        from app.services.ai_service import extract_tasks
        assert extract_tasks("", "es") == []

    @patch("app.services.ai_service._run_flan")
    def test_tasks_con_mock(self, mock_flan):
        from app.services.ai_service import extract_tasks
        mock_flan.return_value = (
            "Entregar el README antes del viernes\n"
            "Completar las pruebas unitarias"
        )
        result = extract_tasks(SAMPLE_TRANSCRIPT_ES, "es")
        assert isinstance(result, list)

    @patch("app.services.ai_service._run_flan")
    def test_tasks_en_con_mock(self, mock_flan):
        from app.services.ai_service import extract_tasks
        mock_flan.return_value = "Deliver README by Friday"
        result = extract_tasks(SAMPLE_TRANSCRIPT_EN, "en")
        assert isinstance(result, list)


class TestExtractDecisions:
    def test_texto_vacio_devuelve_lista_vacia(self):
        from app.services.ai_service import extract_decisions
        assert extract_decisions("", "es") == []

    @patch("app.services.ai_service._run_flan")
    def test_decisions_con_mock(self, mock_flan):
        from app.services.ai_service import extract_decisions
        mock_flan.return_value = (
            "Usar FLAN-T5 base por limitaciones de recursos\n"
            "Aprobar el diseño de interfaz propuesto"
        )
        result = extract_decisions(SAMPLE_TRANSCRIPT_ES, "es")
        assert isinstance(result, list)


# ─── Pipeline completo ────────────────────────────────────────────────────────

class TestProcessAudioFile:
    @patch("app.services.ai_service.transcribe_audio")
    @patch("app.services.ai_service.generate_summary")
    @patch("app.services.ai_service.extract_key_points")
    @patch("app.services.ai_service.extract_tasks")
    @patch("app.services.ai_service.extract_decisions")
    def test_pipeline_completo_es(
        self, mock_dec, mock_tasks, mock_kp, mock_summary, mock_transcribe
    ):
        from app.services.ai_service import process_audio_file

        mock_transcribe.return_value = {
            "text": SAMPLE_TRANSCRIPT_ES,
            "language": "es",
            "duration_seconds": 120.0,
            "processing_time_seconds": 5.0,
            "segments": [{"end": 120.0}],
        }
        mock_summary.return_value = "El proyecto VoxIA avanza correctamente."
        mock_kp.return_value = ["Whisper integrado", "FLAN-T5 elegido"]
        mock_tasks.return_value = ["Santiago entrega README el viernes"]
        mock_dec.return_value = ["Se aprobó usar FLAN-T5 base"]

        result = process_audio_file("fake_audio.mp3", "es")

        assert result["transcript"] == SAMPLE_TRANSCRIPT_ES
        assert result["summary"] == "El proyecto VoxIA avanza correctamente."
        assert len(result["key_points"]) == 2
        assert len(result["tasks"]) == 1
        assert len(result["decisions"]) == 1
        assert result["language"] == "es"
        assert result["duration_seconds"] == 120.0
        assert "processing_time_seconds" in result

    @patch("app.services.ai_service.transcribe_audio")
    def test_pipeline_sin_voz(self, mock_transcribe):
        from app.services.ai_service import process_audio_file

        mock_transcribe.return_value = {
            "text": "",
            "language": "es",
            "duration_seconds": 5.0,
            "processing_time_seconds": 1.0,
            "segments": [],
        }

        result = process_audio_file("silencio.mp3", "es")

        assert result["transcript"] == ""
        assert "no se detectó" in result["summary"].lower()
        assert result["key_points"] == []
        assert result["tasks"] == []
        assert result["decisions"] == []
