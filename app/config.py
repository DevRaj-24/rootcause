from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=ROOT/"data"
SIIS_PATH=DATA_DIR/"siis_responses.json"
DEEPLINK_PATH=DATA_DIR/"deeplinks.json"
CACHE_PATH=DATA_DIR/"semantic_cache.json"
