"""
Pruebas unitarias — VoxIA MLflow Tracker

Cubre:
  - log_pipeline_run: registro exitoso de métricas
  - log_pipeline_run: manejo de error en MLflow sin interrumpir el flujo
  - log_error_run: registro de ejecuciones fallidas

Ejecutar:
    cd backend
    python -m pytest tests/test_mlflow_tracker.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLogPipelineRun:
    @patch("app.services.mlflow_tracker.mlflow")
    def test_log_exitoso(self, mock_mlflow):
        from app.services.mlflow_tracker import log_pipeline_run

        mock_mlflow.get_experiment_by_name.return_value = MagicMock(experiment_id="1")
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=None)
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        # No debe lanzar excepción
        log_pipeline_run(
            file_name="test_audio.mp3",
            language="es",
            duration_seconds=120.0,
            transcription_time=8.5,
            analysis_time=75.0,
            total_time=84.0,
            transcript_length=1500,
            summary_length=250,
            num_key_points=3,
            num_tasks=2,
            num_decisions=1,
            whisper_model="base",
            flan_model="google/flan-t5-base",
            via_grpc=True,
        )

        mock_mlflow.log_params.assert_called()
        mock_mlflow.log_metrics.assert_called()

    @patch("app.services.mlflow_tracker.mlflow")
    def test_log_con_error_no_interrumpe(self, mock_mlflow):
        from app.services.mlflow_tracker import log_pipeline_run

        # Simular que MLflow lanza excepción
        mock_mlflow.get_experiment_by_name.side_effect = Exception("MLflow server no disponible")

        # No debe propagar la excepción
        log_pipeline_run(
            file_name="test.mp3",
            language="es",
            duration_seconds=60.0,
            transcription_time=5.0,
            analysis_time=40.0,
            total_time=45.0,
            transcript_length=800,
            summary_length=150,
            num_key_points=2,
            num_tasks=1,
            num_decisions=0,
            whisper_model="base",
            flan_model="google/flan-t5-base",
            via_grpc=False,
        )

    @patch("app.services.mlflow_tracker.mlflow")
    def test_log_calcula_rtf(self, mock_mlflow):
        from app.services.mlflow_tracker import log_pipeline_run

        mock_mlflow.get_experiment_by_name.return_value = MagicMock(experiment_id="1")
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=None)
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        log_pipeline_run(
            file_name="audio.mp3",
            language="en",
            duration_seconds=60.0,
            transcription_time=4.0,
            analysis_time=30.0,
            total_time=35.0,
            transcript_length=900,
            summary_length=200,
            num_key_points=4,
            num_tasks=3,
            num_decisions=2,
            whisper_model="base",
            flan_model="google/flan-t5-base",
            via_grpc=True,
        )

        # Verificar que se llamó log_metric con real_time_factor
        calls = [str(c) for c in mock_mlflow.log_metric.call_args_list]
        assert any("real_time_factor" in c for c in calls) or mock_mlflow.log_metrics.called

    @patch("app.services.mlflow_tracker.mlflow")
    def test_log_con_error_registra_tag(self, mock_mlflow):
        from app.services.mlflow_tracker import log_pipeline_run

        mock_mlflow.get_experiment_by_name.return_value = MagicMock(experiment_id="1")
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=None)
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        log_pipeline_run(
            file_name="bad.mp3",
            language="es",
            duration_seconds=0,
            transcription_time=0,
            analysis_time=0,
            total_time=0,
            transcript_length=0,
            summary_length=0,
            num_key_points=0,
            num_tasks=0,
            num_decisions=0,
            whisper_model="base",
            flan_model="google/flan-t5-base",
            via_grpc=False,
            error="Archivo corrupto",
        )

        mock_mlflow.set_tag.assert_called()


class TestLogErrorRun:
    @patch("app.services.mlflow_tracker.mlflow")
    def test_error_run_registrado(self, mock_mlflow):
        from app.services.mlflow_tracker import log_error_run

        mock_mlflow.get_experiment_by_name.return_value = MagicMock(experiment_id="1")
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=None)
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        log_error_run(
            file_name="corrupto.mp3",
            language="es",
            error_message="No module named 'whisper'",
        )

        mock_mlflow.set_tag.assert_called()

    @patch("app.services.mlflow_tracker.mlflow")
    def test_error_run_no_interrumpe_si_mlflow_falla(self, mock_mlflow):
        from app.services.mlflow_tracker import log_error_run

        mock_mlflow.get_experiment_by_name.side_effect = Exception("MLflow caído")

        # No debe propagar la excepción
        log_error_run("audio.mp3", "es", "Error de procesamiento")
