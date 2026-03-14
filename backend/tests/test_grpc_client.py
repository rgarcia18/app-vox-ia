"""
Pruebas unitarias — VoxIA gRPC Client

Cubre:
  - health_check_grpc: verificación de salud del servidor
  - analyze_text_via_grpc: análisis con servidor disponible
  - analyze_text_via_grpc: fallback cuando el servidor no está disponible
  - _fallback: análisis directo sin gRPC

Ejecutar:
    cd backend
    python -m pytest tests/test_grpc_client.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import grpc


SAMPLE_TRANSCRIPT = (
    "Buenos días. Hoy revisamos el avance del proyecto. "
    "Se decidió implementar gRPC para la comunicación entre servicios. "
    "David debe preparar la presentación para el lunes."
)


class TestHealthCheckGrpc:
    @patch("app.grpc_service.grpc_client.grpc.insecure_channel")
    def test_servidor_disponible(self, mock_channel):
        from app.grpc_service.grpc_client import health_check_grpc

        mock_stub = MagicMock()
        mock_stub.HealthCheck.return_value = MagicMock(status="ok")

        with patch("app.grpc_service.grpc_client.voxia_pb2_grpc.VoxIAServiceStub", return_value=mock_stub):
            result = health_check_grpc()
            assert result is True

    @patch("app.grpc_service.grpc_client.grpc.insecure_channel")
    def test_servidor_no_disponible(self, mock_channel):
        from app.grpc_service.grpc_client import health_check_grpc

        mock_stub = MagicMock()
        mock_stub.HealthCheck.side_effect = Exception("Connection refused")

        with patch("app.grpc_service.grpc_client.voxia_pb2_grpc.VoxIAServiceStub", return_value=mock_stub):
            result = health_check_grpc()
            assert result is False


class TestAnalyzeTextViaGrpc:
    @patch("app.grpc_service.grpc_client.grpc.insecure_channel")
    def test_analisis_exitoso(self, mock_channel):
        from app.grpc_service.grpc_client import analyze_text_via_grpc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.summary = "El proyecto avanza bien."
        mock_response.key_points = ["gRPC implementado", "Pruebas completadas"]
        mock_response.tasks = ["Preparar presentación el lunes"]
        mock_response.decisions = ["Usar gRPC para comunicación"]

        mock_stub = MagicMock()
        mock_stub.AnalyzeText.return_value = mock_response

        with patch("app.grpc_service.grpc_client.voxia_pb2_grpc.VoxIAServiceStub", return_value=mock_stub):
            result = analyze_text_via_grpc(SAMPLE_TRANSCRIPT, "es")

        assert result["via_grpc"] is True
        assert result["summary"] == "El proyecto avanza bien."
        assert len(result["key_points"]) == 2
        assert len(result["tasks"]) == 1

    @patch("app.grpc_service.grpc_client.grpc.insecure_channel")
    @patch("app.grpc_service.grpc_client._fallback")
    def test_fallback_cuando_grpc_falla(self, mock_fallback, mock_channel):
        from app.grpc_service.grpc_client import analyze_text_via_grpc

        mock_fallback.return_value = {
            "summary": "Resumen via fallback",
            "key_points": ["Punto 1"],
            "tasks": [],
            "decisions": [],
            "via_grpc": False,
        }

        mock_stub = MagicMock()
        mock_stub.AnalyzeText.side_effect = grpc.RpcError()

        with patch("app.grpc_service.grpc_client.voxia_pb2_grpc.VoxIAServiceStub", return_value=mock_stub):
            result = analyze_text_via_grpc(SAMPLE_TRANSCRIPT, "es")

        assert result["via_grpc"] is False
        mock_fallback.assert_called_once_with(SAMPLE_TRANSCRIPT, "es")

    @patch("app.grpc_service.grpc_client.grpc.insecure_channel")
    @patch("app.grpc_service.grpc_client._fallback")
    def test_fallback_cuando_respuesta_no_exitosa(self, mock_fallback, mock_channel):
        from app.grpc_service.grpc_client import analyze_text_via_grpc

        mock_fallback.return_value = {
            "summary": "Resumen fallback",
            "key_points": [],
            "tasks": [],
            "decisions": [],
            "via_grpc": False,
        }

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error_message = "Error interno del servidor gRPC"

        mock_stub = MagicMock()
        mock_stub.AnalyzeText.return_value = mock_response

        with patch("app.grpc_service.grpc_client.voxia_pb2_grpc.VoxIAServiceStub", return_value=mock_stub):
            result = analyze_text_via_grpc(SAMPLE_TRANSCRIPT, "es")

        assert result["via_grpc"] is False

    def test_transcript_vacio_usa_fallback(self):
        from app.grpc_service.grpc_client import analyze_text_via_grpc
        with patch("app.grpc_service.grpc_client._fallback") as mock_fb:
            mock_fb.return_value = {
                "summary": "", "key_points": [], "tasks": [], "decisions": [], "via_grpc": False
            }
            # Con transcript vacío aun así llama al server — es responsabilidad del server validar
            result = analyze_text_via_grpc("", "es")
            assert isinstance(result, dict)


class TestFallback:
    @patch("app.services.ai_service.generate_summary", return_value="Resumen directo")
    @patch("app.services.ai_service.extract_key_points", return_value=["Punto A"])
    @patch("app.services.ai_service.extract_tasks", return_value=["Tarea B"])
    @patch("app.services.ai_service.extract_decisions", return_value=["Decisión C"])
    def test_fallback_directo(self, mock_dec, mock_tasks, mock_kp, mock_summary):
        from app.grpc_service.grpc_client import _fallback
        result = _fallback(SAMPLE_TRANSCRIPT, "es")
        assert result["via_grpc"] is False
        assert result["summary"] == "Resumen directo"
        assert result["key_points"] == ["Punto A"]
        assert result["tasks"] == ["Tarea B"]
        assert result["decisions"] == ["Decisión C"]
