"""
VoxIA gRPC Client

Cliente que usa FastAPI para llamar al servidor gRPC de análisis.
Si el servidor gRPC no está disponible, cae en modo fallback
usando las funciones directamente (sin gRPC).
"""

import grpc
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.grpc_service import voxia_pb2, voxia_pb2_grpc

GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
GRPC_TIMEOUT = 300  # 5 minutos


def analyze_text_via_grpc(transcript: str, language: str = "es") -> dict:
    """
    Llama al servidor gRPC para analizar el texto transcrito.
    Si falla, usa fallback directo (sin gRPC).

    Returns:
        dict con keys: summary, key_points, tasks, decisions, via_grpc
    """
    try:
        channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        stub = voxia_pb2_grpc.VoxIAServiceStub(channel)

        request = voxia_pb2.AnalyzeRequest(
            transcript=transcript,
            language=language,
        )

        response = stub.AnalyzeText(request, timeout=GRPC_TIMEOUT)
        channel.close()

        if response.success:
            print("✅ Análisis completado vía gRPC")
            return {
                "summary": response.summary,
                "key_points": list(response.key_points),
                "tasks": list(response.tasks),
                "decisions": list(response.decisions),
                "via_grpc": True,
            }
        else:
            print(f"⚠️  gRPC respondió con error: {response.error_message} — usando fallback")
            return _fallback(transcript, language)

    except grpc.RpcError as e:
        print(f"⚠️  gRPC no disponible — usando fallback directo")
        return _fallback(transcript, language)
    except Exception as e:
        print(f"⚠️  Error inesperado en gRPC ({e}) — usando fallback directo")
        return _fallback(transcript, language)


def _fallback(transcript: str, language: str) -> dict:
    """Fallback: llama a las funciones de análisis directamente sin gRPC."""
    from app.services.ai_service import (
        generate_summary,
        extract_key_points,
        extract_tasks,
        extract_decisions,
    )
    return {
        "summary": generate_summary(transcript, language),
        "key_points": extract_key_points(transcript, language),
        "tasks": extract_tasks(transcript, language),
        "decisions": extract_decisions(transcript, language),
        "via_grpc": False,
    }


def health_check_grpc() -> bool:
    """Verifica si el servidor gRPC está operativo."""
    try:
        channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        stub = voxia_pb2_grpc.VoxIAServiceStub(channel)
        response = stub.HealthCheck(voxia_pb2.HealthRequest(), timeout=5)
        channel.close()
        return response.status == "ok"
    except Exception:
        return False
