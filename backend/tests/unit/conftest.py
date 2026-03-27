# tests/conftest.py
# Configuración global de pytest para VoxIA

import sys
import os

# Asegurar que el directorio backend esté en el path para los imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
