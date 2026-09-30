from __future__ import annotations
import json,re,time
from pathlib import Path
from collections import OrderedDict
from typing import Any
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from .config import SIIS_PATH, DEEPLINK_PATH, CACHE_PATH
from .models import Action,ActionCategory,Condition,Deeplink,Goal,ResponseBody,ResultTypes,StepGroup,TroubleshootResponse,ValidationDeepLink

STOP={"the","a","an","and","or","to","for","of","on","in","my","your","with","this","that","it","is","are","was","be","can","i","when","then","from","device","phone","tablet","smartphone","nexa","techcorp"}
SYN={"flickers":"flicker","flickering":"flicker","flashes":"flicker","flashing":"flicker","blank":"black","dark":"black","white":"black","laggy":"latency","delayed":"latency","responsiveness":"touch","cracked":"damage","crack":"damage","broken":"damage","distorted":"artifact","stopped":"fail","won't":"not","cant":"not","doesnt":"not","isnt":"not","unable":"not"}

ALIASES={
 "navigation gestures":"voiceassist://masked/act/d5c6ddcc45",
 "full screen gesture":"voiceassist://masked/act/d5c6ddcc45",
 "touch sensitivity":"voiceassist://masked/act/1b0d34e9b4",
 "enable touch sensitivity":"voiceassist://masked/act/14eb42b895",
 "factory data reset":"voiceassist://masked/act/635e6add5d",
 "auto rotate":"voiceassist://masked/act/7c340914be",
 "screen rotation":"voiceassist://masked/act/7c340914be",
 "quick access panel":"voiceassist://masked/act/a739f217be",
 "quick access panels":"voiceassist://masked/act/a739f217be",
 "multi window":"voiceassist://masked/act/4d10b03627",
 "wifi":"voiceassist://masked/act/cb03ac7425",
 "wi fi":"voiceassist://masked/act/cb03ac7425",
 "performance profile":"voiceassist://masked/act/ea0b799b4f",
 "diagnostic":"voiceassist://masked/act/7db5280233",
 "diagnostic data":"voiceassist://masked/act/7db5280233",
 "screen timeout":"voiceassist://masked/act/1d2dedbadc",
}

def norm(s:str)->str:
 s=s.lower().replace("’","'")
 s=re.sub(r"https?://\S+|www\.\S+"," ",s)
 s=re.sub(r"[^a-z0-9\s]"," ",s)
 return " ".join(SYN.get(t,t) for t in re.findall(r"[a-z0-9]+",s) if t not in STOP and len(t)>1)

def title_for(h:str)->str:
 l=h.lower()
 mapping=[("factory data reset","Factory data reset"),("touch sensitivity","Touch sensitivity"),("navigation gesture","Navigation gestures"),("screen rotation","Screen rotation"),("wifi","Wi-Fi connection"),("diagnostic","Diagnostic check"),("data transfer","Data transfer"),("email","Email access"),("safe mode","Safe mode"),("restart","Device restart"),("charger","Charger check"),("charging","Charge device"),("physical damage","Physical damage"),("liquid","Liquid damage"),("screen","Screen display"),("screen damage","Screen damage"),("cracked","Screen damage"),("multi window","Multi window"),("quick access","Quick access")]
 for k,v in mapping:
  if k in l:return v
 raw=re.sub(r"^\s*(?:step\s*\d+[:.)]?|\d+[.)])\s*","",h,flags=re.I).strip()
 words=[x for x in raw.split() if x.lower() not in {"the","a","an","your","device","smartphone","tablet","on","or","and","for","to","in"}][:3]
 return " ".join(words).strip().title() or "Device issue"

def goal_for(title:str)->str:return f"Follow these steps to perform this {title} Troubleshooting"

def desc_for(text:str)->str:
 l=text.lower()
 if "touch sensitivity" in l:return "It will adjust touch sensitivity safely"
 if "navigation gesture" in l or "full screen gesture" in l:return "It will open navigation settings quickly"
 if "factory data reset" in l or "reset" in l:return "It will open reset options carefully"
 if "safe mode" in l:return "It will isolate third party issues"
 if "restart" in l:return "It will restart the device safely"
 if "wifi" in l:return "It will open Wi-Fi settings quickly"
 if "diagnostic" in l:return "It will open diagnostic settings quickly"
 if "repair" in l or "service center" in l or "support" in l:return "It will guide the repair process"
 if "charge" in l or "charger" in l:return "It will check the charging path"
 return "It will guide the next troubleshooting step"

class Index:
 def __init__(self,docs):
  self.w=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True)
  self.c=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),sublinear_tf=True,max_features=20000)
  self.wm=self.w.fit_transform(docs);self.cm=self.c.fit_transform(docs)
 def top(self,q,k=5):
  a=(self.w.transform([q])@self.wm.T).toarray()[0]
  b=(self.c.transform([q])@self.cm.T).toarray()[0]
  s=.65*a+.35*b
  return [(int(i),float(s[i])) for i in s.argsort()[::-1][:k]]

class Cache:
 def __init__(self,p:Path,max_items=256):
  self.p=p;self.mem=OrderedDict();self.hits=self.misses=0
  if p.exists():
   try:self.mem.update(json.loads(p.read_text()))
   except Exception:pass
 def get(self,k):
  if k in self.mem:self.hits+=1;self.mem.move_to_end(k);return self.mem[k]
  self.misses+=1;return None
 def set(self,k,v):
  self.mem[k]=v;self.mem.move_to_end(k)
  while len(self.mem)>256:self.mem.popitem(last=False)
  self.p.write_text(json.dumps(dict(self.mem),indent=2))

class RootCauseEngine:
 def __init__(self):
  self.siis=json.loads(SIIS_PATH.read_text())["responses"]
  self.links=json.loads(DEEPLINK_PATH.read_text())["deeplinks"]
  self.link_by_uri={x["deeplink"]:x for x in self.links}
  for x in self.links:
   v=x.get("validation") or {}
   if v.get("deeplink"):self.link_by_uri[v["deeplink"]]=x
  self.cache=Cache(CACHE_PATH)
  self.siis_docs=[norm(r["original_query"]+" "+r["siis_response"]["title"]+" "+r["siis_response"]["content"][:6000]) for r in self.siis]
  self.siis_index=Index(self.siis_docs)
  self.link_docs=[norm(" ".join(str(x.get(k) or "") for k in ("description","message","qna_description","originalType"))) for x in self.links]
  self.link_index=Index(self.link_docs)

 def enrich_query(self,q):
  n=norm(q);low=n
  features={x:any(y in low.split() for y in words) for x,words in {
   "black_screen":{"black","screen"},"flicker":{"flicker"},"touch":{"touch","latency"},
   "damage":{"damage","artifact"},"charging":{"charge","charging","charger"},"rotation":{"rotate","orientation"},
   "wifi":{"wifi"},"email":{"email"},"data_transfer":{"transfer"},"multi_window":{"window"},"diagnostic":{"diagnostic"}
  }.items()}
  family="screen"
  for k,v in features.items():
   if v:family=k;break
  return {"normalized_query":n,"cache_key":f"{family}|{n}","features":features}

 def retrieve(self,q,override=None):
  if override:
   try:
    x=json.loads(override) if isinstance(override,str) else override
    return {"siis_response":x},1.0,"provided"
   except Exception:pass
  tops=self.siis_index.top(norm(q),5);best=None
  for i,s in tops:
   row=self.siis[i];fields=row["original_query"]+" "+row["siis_response"]["title"]
   score=.55*s+.45*fuzz.token_set_ratio(q,fields)/100
   if best is None or score>best[1]:best=(row,score)
  return best[0],float(best[1]),"retrieval"

 def link_hit(self,text):
  low=text.lower()
  for phrase,uri in sorted(ALIASES.items(),key=lambda x:-len(x[0])):
   if phrase in low and uri in self.link_by_uri:return self.link_by_uri[uri]
  tops=self.link_index.top(norm(text),8);best=None
  for i,s in tops:
   x=self.links[i];fields=" ".join(str(x.get(k) or "") for k in ("description","message","qna_description"))
   score=.55*s+.45*fuzz.token_set_ratio(text,fields)/100
   if best is None or score>best[1]:best=(x,score)
  return best[0] if best and best[1]>=.72 else None

 def validation(self,x):
  v=x.get("validation") or {}
  if not v.get("deeplink") or not v.get("key"):return None
  rt=v.get("resultType");cond=v.get("condition")
  return ValidationDeepLink(deeplink=v["deeplink"],key=v["key"],
   resultType=ResultTypes(rt) if rt in [e.value for e in ResultTypes] else None,
   condition=Condition(cond) if cond in [e.value for e in Condition] else None,
   value=str(v["value"]) if v.get("value") is not None else None)

 def extract(self,row):
  content=row["siis_response"]["content"]
  chunks=re.split(r"(?m)^#{1,4}\s*Step\s*\d+\s*[:.-]?\s*|(?m)^#{1,4}\s+",content)
  out=[]
  for chunk in chunks:
   lines=[re.sub(r"\s+"," ",x).strip() for x in chunk.splitlines() if x.strip()]
   ops=[x for x in lines if len(x)>=12 and not x.startswith("*")]
   if ops:out.append((lines[0][:80] if lines else "Troubleshooting",ops[:8]))
  return out or [("Troubleshooting",[x.strip() for x in re.split(r"(?<=[.!?])\s+",content) if len(x.strip())>20][:8])]

 def plan(self,row,score):
  acts=[]
  for heading,steps in self.extract(row):
   txt=heading+" "+" ".join(steps);link=self.link_hit(txt)
   low=txt.lower()
   if link:cat=ActionCategory.auto
   elif any(t in low for t in ("contact customer support","service center","authorized")):cat=ActionCategory.manual
   elif any(t in low for t in ("factory data reset","safe mode","force a restart","restart your device")):cat=ActionCategory.critical
   else:cat=ActionCategory.manual
   sg=StepGroup(steps=list(dict.fromkeys(steps))[:8])
   if link:
    sg.actionableDeeplink=Deeplink(deeplink=link["deeplink"],description=link.get("description",""),message=link.get("message",""),classes=link.get("classes"),originalType=link.get("originalType"))
    sg.validationDeeplink=self.validation(link)
   acts.append(Action(actionName=title_for(heading),description=desc_for(txt),stepGroups=[sg],category=cat))
  seen=set();unique=[]
  for a in acts:
   uri=a.stepGroups[0].actionableDeeplink.deeplink if a.stepGroups[0].actionableDeeplink else ""
   k=a.actionName+"|"+uri
   if k not in seen:seen.add(k);unique.append(a)
  unique.sort(key=lambda a:{ActionCategory.auto:0,ActionCategory.manual:1,ActionCategory.critical:2}[a.category])
  title=title_for(row["siis_response"]["title"])
  return Goal(goal=goal_for(title),title=title,actions=unique,score=round(.55+.4*max(0,min(1,score)),2))

 def validate(self,payload):
  urls=[];bad=[]
  def walk(x):
   if isinstance(x,dict):
    for k,v in x.items():
     if isinstance(v,str) and re.search(r"https?://|www\.|\[[^\]]+\]\(",v):urls.append(v)
     if k=="deeplink" and isinstance(v,str) and v not in self.link_by_uri and v!="voiceassist://dummy_positive":bad.append(v)
     walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  walk(payload);schema=True;errors=[]
  try:ResponseBody.model_validate(payload["response"])
  except Exception as e:schema=False;errors=[str(e)[:300]]
  return {"schema_valid":schema,"zero_url_leaks":not urls,"catalog_validity":not bad,"action_count":sum(len(c.get("actions",[])) for c in payload["response"].get("contexts",[])),"invalid_deeplinks":bad,"url_leaks":urls,"schema_errors":errors}

 def troubleshoot(self,q,siis_response=None):
  start=time.perf_counter();en=self.enrich_query(q)
  cached=None if siis_response else self.cache.get(en["cache_key"]);hit=cached is not None
  if cached:payload=cached
  else:
   row,score,_=self.retrieve(q,siis_response);g=self.plan(row,score)
   payload={"query":q,"response":ResponseBody(contexts=[g]).model_dump(mode="json"),"query_variations":[q,en["normalized_query"],"troubleshoot "+en["normalized_query"],"how to fix "+en["normalized_query"]]}
   self.cache.set(en["cache_key"],payload)
  payload["meta"]={"latency_ms":round((time.perf_counter()-start)*1000,2),"cache_hit":hit,"model":"source-grounded-local","cost_usd":0.0,"validation":self.validate(payload),"normalized_query":en["normalized_query"]}
  return TroubleshootResponse(**payload)

_ENGINE=None
def get_engine():
 global _ENGINE
 if _ENGINE is None:_ENGINE=RootCauseEngine()
 return _ENGINE
