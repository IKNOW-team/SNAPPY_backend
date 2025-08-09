from pathlib import Path

def read_bytes(path: str | Path) -> bytes:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(str(p))
    return p.read_bytes()