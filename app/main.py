from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .engine import get_engine
from .models import TroubleshootRequest,TroubleshootResponse
app=FastAPI(title="RootCause - Smart Guided Troubleshooting Engine",version="1.0.0")
engine=get_engine()
STATIC=Path(__file__).resolve().parents[1]/"static"
app.mount("/static",StaticFiles(directory=str(STATIC)),name="static")
@app.get("/")
def home(): return FileResponse(STATIC/"index.html")
@app.get("/health")
def health(): return {"status":"ok","catalog_entries":len(engine.links),"siis_cases":len(engine.siis)}
@app.post("/v1/troubleshoot",response_model=TroubleshootResponse)
def troubleshoot(req:TroubleshootRequest): return engine.troubleshoot(req.query,req.siis_response)
@app.get("/metrics")
def metrics(): return {"cache_hits":engine.cache.hits,"cache_misses":engine.cache.misses,"cached_items":len(engine.cache.mem),"catalog_entries":len(engine.links)}
