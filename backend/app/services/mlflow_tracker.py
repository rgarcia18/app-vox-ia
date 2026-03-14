"""
VoxIA MLflow Tracker

Registra métricas de cada ejecución del pipeline en MLflow:
- Duración del audio
- Tiempo de transcripción
- Tiempo de análisis NLP
- Tiempo total del pipeline
- Idioma detectado
- Longitud del transcript
- Longitud del resumen
- Número de puntos clave, tareas y decisiones encontradas
- Modelo Whisper y FLAN-T5 usados
- Si se usó gRPC o fallback directo
"""

import mlflow
import os
import time
from datetime import datetime

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


def log_pipeline_run(
    file_name: str,
    language: str,
    duration_seconds: float,
    transcription_time: float,
    analysis_time: float,
    total_time: float,
    transcript_length: int,
    summary_length: int,
    num_key_points: int,
    num_tasks: int,
    num_decisions: int,
    whisper_model: str,
    flan_model: str,
    via_grpc: bool = False,
    error: str = None,
):
    """
    Registra una ejecución completa del pipeline en MLflow.
    Si MLflow no está disponible, lo ignora silenciosamente.
    """
    try:
        experiment_id = _get_or_create_experiment()
        mlflow.set_experiment(EXPERIMENT_NAME)

        with mlflow.start_run(experiment_id=experiment_id):

            # ── Parámetros del experimento ─────────────────────────────────────
            mlflow.log_params({
                "whisper_model":   whisper_model,
                "flan_t5_model":   flan_model,
                "language":        language,
                "via_grpc":        str(via_grpc),
                "file_name":       file_name,
                "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            # ── Métricas de rendimiento ────────────────────────────────────────
            mlflow.log_metrics({
                "audio_duration_seconds":   round(duration_seconds, 2),
                "transcription_time_s":     round(transcription_time, 2),
                "analysis_time_s":          round(analysis_time, 2),
                "total_pipeline_time_s":    round(total_time, 2),
            })

            # ── Métricas de calidad de salida ──────────────────────────────────
            mlflow.log_metrics({
                "transcript_chars":   transcript_length,
                "summary_chars":      summary_length,
                "num_key_points":     num_key_points,
                "num_tasks":          num_tasks,
                "num_decisions":      num_decisions,
            })

            # ── Métricas derivadas ─────────────────────────────────────────────
            if duration_seconds > 0:
                rtf = total_time / duration_seconds  # Real-Time Factor
                mlflow.log_metric("real_time_factor", round(rtf, 3))

            # ── Estado de la ejecución ─────────────────────────────────────────
            if error:
                mlflow.set_tag("run_status", "error")
                mlflow.set_tag("error_message", error[:500])
            else:
                mlflow.set_tag("run_status", "success")

            print(f"📊 MLflow: run registrado | total={round(total_time, 1)}s | "
                  f"points={num_key_points} | tasks={num_tasks}")

    except Exception as e:
        # MLflow no interrumpe el pipeline si falla
        print(f"⚠️  MLflow tracking no disponible: {e}")


def log_error_run(file_name: str, language: str, error_message: str):
    """Registra una ejecución fallida en MLflow."""
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
