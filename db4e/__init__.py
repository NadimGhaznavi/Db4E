import sys
from pathlib import Path


pycache_dir = Path.home() / ".db4e" / "pycache"
pycache_dir.mkdir(parents=True, exist_ok=True)

sys.pycache_prefix = str(pycache_dir)