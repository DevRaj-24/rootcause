"""Optional OpenAI-compatible enrichment adapter. Default demo is offline."""
from __future__ import annotations
import json,os,httpx
class OptionalLLM:
 def __init__(self):
  self.url=os.getenv('ROOTCAUSE_LLM_URL','').strip();self.model=os.getenv('ROOTCAUSE_LLM_MODEL','').strip();self.key=os.getenv('ROOTCAUSE_LLM_API_KEY','').strip()
 @property
 def enabled(self): return bool(self.url and self.model and self.key)
 async def normalize(self,query:str):
  if not self.enabled:return None
  p={'model':self.model,'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'Return JSON with normalized_query, intent, entities. Do not invent troubleshooting steps or URLs.'},{'role':'user','content':query}]}
  async with httpx.AsyncClient(timeout=8) as c:
   r=await c.post(self.url,json=p,headers={'Authorization':f'Bearer {self.key}'})
   r.raise_for_status();d=r.json()
  return json.loads(d['choices'][0]['message']['content'])
