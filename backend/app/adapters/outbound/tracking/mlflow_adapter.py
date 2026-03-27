"""
VoxIA MLflow Adapter — Registro de métricas del pipeline con MLflow
"""
import mlflow
import os
from datetime import datetime

from app.domain.entities.pipeline_metrics import PipelineMetrics
from app.domain.ports.outbound.providers.metrics_provider import IMetricsProvider

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
EXPERIMENT_NAME = "VoxIA - Pipeline de Análisis de Audio"


def _get_or_create_experiment() -> str:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            EXPERIMENT_NAME,
            tags={
                "project": "VoxIA",
                "universidad": "Universidad Autónoma de Occidente",
                "modelos": "Whisper Base + FLAN-T5 Base",
            },
        )
    else:
        experiment_id = experiment.experiment_id
    return experiment_id


class MLflowAdapter(IMetricsProvider):
    def log_run(self, metrics: PipelineMetrics) -> None:
        try:
            experiment_id = _get_or_create_experiment()
            mlflow.set_experiment(EXPERIMENT_NAME)

            with mlflow.start_run(experiment_id=experiment_id):
                mlflow.log_params({
                    "whisper_model": metrics.whisper_model,
                    "flan_t5_model": metrics.flan_model,
                    "language":      metrics.language,
                    "via_grpc":      str(metrics.via_grpc),
                    "file_name":     metrics.file_name,
                    "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                mlflow.log_metrics({
                    "audio_duration_seconds": round(metrics.duration_seconds, 2),
                    "transcription_time_s":   round(metrics.transcription_time, 2),
                    "analysis_time_s":        round(metrics.analysis_time, 2),
                    "total_pipeline_time_s":  round(metrics.total_time, 2),
                })
                mlflow.log_metrics({
                    "transcript_chars": metrics.transcript_length,
                    "summary_chars":    metrics.summary_length,
                    "num_key_points":   metrics.num_key_points,
                    "num_tasks":        metrics.num_tasks,
                    "num_decisions":    metrics.num_decisions,
                })
                if metrics.duration_seconds > 0:
                    rtf = metrics.total_time / metrics.duration_seconds
                    mlflow.log_metric("real_time_factor", round(rtf, 3))

                if metrics.error:
                    mlflow.set_tag("run_status", "error")
                    mlflow.set_tag("error_message", metrics.error[:500])
                else:
                    mlflow.set_tag("run_status", "success")

                print(f"📊 MLflow: run registrado | total={round(metrics.total_time, 1)}s | "
                      f"points={metrics.num_key_points} | tasks={metrics.num_tasks}")

        except Exception as e:
            print(f"⚠️  MLflow tracking no disponible: {e}")

    def log_error(self, file_name: str, language: str, error_message: str) -> None:
        try:
            _get_or_create_experiment()
            mlflow.set_experiment(EXPERIMENT_NAME)
            with mlflow.start_run():
                mlflow.log_params({
                    "file_name": file_name,
                    "language":  language,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                mlflow.set_tag("run_status", "error")
                mlflow.set_tag("error_message", error_message[:500])
        except Exception:
            pass
