"""
Script para generar los stubs de gRPC a partir del archivo .proto

Uso:
    python generate_grpc.py

Requiere:
    pip install grpcio grpcio-tools
"""
import subprocess
import sys
import os

PROTO_DIR = os.path.join(os.path.dirname(__file__), "app", "grpc_service")
PROTO_FILE = os.path.join(PROTO_DIR, "voxia.proto")
OUT_DIR = PROTO_DIR

def main():
    print("🔧 Generando stubs gRPC desde voxia.proto...")
    result = subprocess.run(
        [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--proto_path={PROTO_DIR}",
            f"--python_out={OUT_DIR}",
            f"--grpc_python_out={OUT_DIR}",
            PROTO_FILE,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("❌ Error generando stubs:")
        print(result.stderr)
        sys.exit(1)

    # Crear __init__.py si no existe
    init_path = os.path.join(OUT_DIR, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()

    print("✅ Stubs generados en:", OUT_DIR)
    print("   - voxia_pb2.py")
    print("   - voxia_pb2_grpc.py")

if __name__ == "__main__":
    main()
