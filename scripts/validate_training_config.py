"""Utility to validate training YAML config using pydantic models."""
import sys
import yaml
from pathlib import Path

# Ensure project root is on sys.path so we can import `src` package
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.training_config import validate_training_config


def main(path: str):
    p = Path(path)
    if not p.exists():
        print(f"Config file not found: {path}")
        sys.exit(2)

    data = yaml.safe_load(p.read_text())
    try:
        cfg = validate_training_config(data)
        print("✅ Training config validated successfully")
        print(cfg.model_dump_json(indent=2))
    except Exception as e:
        print("❌ Validation failed:", e)
        sys.exit(1)


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'deepseek_yaml_20251231_07aa52.yaml'
    main(path)
