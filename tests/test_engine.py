import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.engine import RootCauseEngine
def test_starter_cases():
 e=RootCauseEngine();qs=[x for x in Path('data/input.txt').read_text().splitlines() if x.strip()]
 assert len(qs)==20
 for q in qs:
  o=e.troubleshoot(q).model_dump(mode='json');v=o['meta']['validation']
  assert v['schema_valid'] and v['zero_url_leaks'] and v['catalog_validity']
  assert re.search(r'https?://|www\\.',json.dumps(o)) is None
def test_cache():
 e=RootCauseEngine();q='My screen is laggy and touch inputs are delayed.'
 e.troubleshoot(q);o=e.troubleshoot(q).model_dump(mode='json');assert o['meta']['cache_hit']
