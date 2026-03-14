"""
VoxIA gRPC Server

Expone el servicio de análisis de texto (resumen, puntos clave, tareas, decisiones)
a través de gRPC en el puerto 50051.

Uso:
    python grpc_server.py

El servidor FastAPI (puerto 8000) llama a este servidor internamente
cuando necesita analizar texto transcrito.
"""

import grpc
import sys
import os
from concurrent import futures

# Asegurar que el directorio raíz del backend esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.grpc_service import voxia_pb2, voxia_pb2_grpc
from app.services.ai_service import (
    generate_summary,
    extract_key_points,
    extract_tasks,
    extract_decisions,
)

GRPC_PORT = 50051
MAX_WORKERS = 4


class VoxIAServicer(voxia_pb2_grpc.VoxIAServiceServicer):
    """
    Implementación del servicio gRPC de VoxIA.
    Recibe texto transcrito y devuelve el análisis completo.
    """

    def AnalyzeText(self, request, context):
        transcript = request.transcript.strip()
        language = request.language or "es"

        print(f"📨 gRPC AnalyzeText recibido | lang={language} | chars={len(transcript)}")

        if not transcript:
            return voxia_pb2.AnalyzeResponse(
                summary="No se proporcionó texto para analizar.",
                key_points=[],
                tasks=[],
                decisions=[],
                success=False,
                error_message="El transcript está vacío.",
            )

        try:
            summary    = generate_summary(transcript, language)
            key_points = extract_key_points(transcript, language)
            tasks      = extract_tasks(transcript, language)
            decisions  = extract_decisions(transcript, language)

            print(f"✅ gRPC AnalyzeText completado | summary={len(summary)} chars")

            return voxia_pb2.AnalyzeResponse(
                summary=summary,
                key_points=key_points,
                tasks=tasks,
                decisions=decisions,
                success=True,
                error_message="",
            )

        except Exception as e:
            print(f"❌ gRPC AnalyzeText error: {e}")
            return voxia_pb2.AnalyzeResponse(
                summary="",
                key_points=[],
                tasks=[],
                decisions=[],
                success=False,
                error_message=str(e),
            )

    def HealthCheck(self, request, context):
        return voxia_pb2.HealthResponse(
            status="ok",
            message="VoxIA gRPC Server operativo",
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    voxia_pb2_grpc.add_VoxIAServiceServicer_to_server(VoxIAServicer(), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    print(f"🚀 VoxIA gRPC Server iniciado en puerto {GRPC_PORT}")
    print("   Servicio: VoxIAService")
    print("   Métodos:  AnalyzeText | HealthCheck")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("🛑 gRPC Server detenido")
        server.stop(0)


if __name__ == "__main__":
    serve()
