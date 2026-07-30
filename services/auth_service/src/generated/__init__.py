import sys
from pathlib import Path

generated_dir = str(Path(__file__).parent)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir)