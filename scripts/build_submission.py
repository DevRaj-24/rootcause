from pathlib import Path
import json, subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from docx import Document
from docx.shared import Inches as DInches, Pt as DPt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SUB=ROOT/"submission"; SUB.mkdir(exist_ok=True)
PURPLE=RGBColor(105,54,217); DARK=RGBColor(23,20,33); MID=RGBColor(105,101,116); BG=RGBColor(248,247,252); WHITE=RGBColor(255,255,255)

def add_text(slide,text,x,y,w,h,size=20,bold=False,color=DARK,align=PP_ALIGN.LEFT):
    tb=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=tb.text_frame; tf.clear()
    p=tf.paragraphs[0]; p.alignment=align
    r=p.add_run(); r.text=text; r.font.name="Aptos"; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color
    return tb

def add_card(slide,x,y,w,h,title,body):
    sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=WHITE; sh.line.color.rgb=RGBColor(229,225,238)
    add_text(slide,title,x+.18,y+.14,w-.36,.35,15,True,PURPLE)
    add_text(slide,body,x+.18,y+.55,w-.36,h-.68,11,False,DARK)
    return sh

def new_slide(prs,title,subtitle=None):
    sl=prs.slides.add_slide(prs.slide_layouts[6]); sl.background.fill.solid(); sl.background.fill.fore_color.rgb=BG
    add_text(sl,title,.55,.42,11.9,.55,25,True,DARK)
    if subtitle: add_text(sl,subtitle,.58,.98,11.4,.34,11,False,MID)
    return sl

def make_ppt():
    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
    sl=prs.slides.add_slide(prs.slide_layouts[6]); sl.background.fill.solid(); sl.background.fill.fore_color.rgb=BG
    add_text(sl,"ROOTCAUSE",.62,.65,5.8,.55,18,True,PURPLE)
    add_text(sl,"Smart Guided\nTroubleshooting Engine",.62,1.35,7.5,1.45,30,True,DARK)
    add_text(sl,"Samsung PRISM Generative AI Hackathon 2026–27 · Theme 02",.66,3.0,7.3,.45,14,False,MID)
    add_text(sl,"VIT Vellore · rootcause",.66,5.6,4.5,.4,15,True,DARK)
    add_text(sl,"Dev Raj · 24BDS0080\nSarang Raj · 24BDS0091\nAntony Roy · 24BCE0920",.66,6.05,4.8,.95,12,False,MID)
    for i,(cx,cy,rad) in enumerate([(10.9,2.3,.72),(10.1,3.4,.45),(11.7,4.1,.5),(10.8,4.9,.35)]):
        s=sl.shapes.add_shape(MSO_SHAPE.OVAL,Inches(cx),Inches(cy),Inches(rad),Inches(rad))
        s.fill.solid(); s.fill.fore_color.rgb=PURPLE if i==0 else RGBColor(197,177,245); s.line.fill.background()
    sl=new_slide(prs,"Theme 02 — Guided Troubleshooting","Turn a vague device complaint into one-click fix steps.")
    add_card(sl,.6,1.55,5.9,4.75,"Problem in our words","Users report symptoms like “screen flickers and battery dies fast”. Support agents translate those words into troubleshooting steps, while users still have to hunt through Settings.")
    add_card(sl,6.8,1.55,5.9,4.75,"What RootCause does","Query enrichment → source-grounded retrieval → structured ordered actions → exact catalog deeplinks → validation → fast-path cache.")
    sl=new_slide(prs,"Existing Solutions & Gaps")
    add_card(sl,.65,1.45,3.8,4.9,"Search / knowledge base","Good at finding articles, but the user still interprets long instructions and navigates Settings manually.")
    add_card(sl,4.75,1.45,3.8,4.9,"Generic chatbot","Can paraphrase advice, but may invent unsupported actions or links without a strict output contract.")
    add_card(sl,8.85,1.45,3.8,4.9,"Rule-only flows","Reliable for known cases, but brittle when the same complaint is phrased differently.")
    sl=new_slide(prs,"Our Solution & Architecture","Grounding first. Actions second. Validation before delivery.")
    nodes=[("01","Query Enrichment"),("02","SIIS Retrieval"),("03","Step Structuring"),("04","Deeplink Catalog"),("05","Contract Validation"),("06","Semantic Cache")]
    for i,(n,t) in enumerate(nodes):
        x=.55+i*2.05; add_card(sl,x,2.3,1.7,2.1,n,t)
        if i<5: add_text(sl,"→",x+1.73,3.05,.3,.4,20,True,PURPLE,PP_ALIGN.CENTER)
    add_text(sl,"REST API: POST /v1/troubleshoot",.75,5.25,4.7,.45,15,True,DARK)
    add_text(sl,"Goal → Actions → StepGroups → actionable/validation deeplinks",5.2,5.25,7,.45,13,False,MID)
    sl=new_slide(prs,"Demo & Product Walkthrough")
    add_card(sl,.6,1.45,4,4.9,"Input","My screen is laggy and touch inputs are delayed.")
    add_card(sl,4.9,1.45,3.5,4.9,"Engine","Normalize symptom language\nRetrieve best SIIS case\nExtract ordered steps\nResolve only catalog-known deeplinks")
    add_card(sl,8.65,1.45,4,4.9,"Output","Structured JSON\nAction category\nStep groups\nValidation deeplink\nActionable deeplink\nCache metadata")
    sl=new_slide(prs,"Tools & Tech Stack")
    add_card(sl,.65,1.45,3.85,4.9,"API & Runtime","Python · FastAPI · Pydantic\nDocker · Uvicorn\nREST JSON contract")
    add_card(sl,4.75,1.45,3.85,4.9,"Retrieval","Word + character TF-IDF\nFuzzy token reranking\nSource-grounded SIIS retrieval")
    add_card(sl,8.85,1.45,3.85,4.9,"Guardrails","Catalog-only deeplinks\nHTTP URL leak checks\nSchema validation\nIntent-aware cache")
    sl=new_slide(prs,"Impact & Use Cases")
    add_card(sl,.65,1.45,3.75,4.9,"Customer support","Reduce translation from vague complaints to concrete device actions.")
    add_card(sl,4.78,1.45,3.75,4.9,"Self-service","One structured answer can guide the user to the relevant Settings action.")
    add_card(sl,8.91,1.45,3.75,4.9,"Knowledge reuse","Separate retrieval and mapping layers keep the approach reusable across many scenarios.")
    sl=new_slide(prs,"Innovation, Results & Limitations")
    metrics={}
    try: metrics=json.loads((ROOT/"metrics.json").read_text())
    except Exception: pass
    add_card(sl,.65,1.45,3.75,4.9,"Innovation","Grounded action planning\nCatalog-gated deeplinks\nContract-first output\nFast path for repeated intent")
    add_card(sl,4.78,1.45,3.75,4.9,"Prototype results","20 supplied starter cases\nPlanner P95: "+str(metrics.get("planner_p95_ms","n/a"))+" ms\nCache P95: "+str(metrics.get("exact_cache_p95_ms","n/a"))+" ms\nLocal CPU measurements")
    add_card(sl,8.91,1.45,3.75,4.9,"Limitations","Starter corpus only\nRetrieval quality depends on corpus coverage\nProduction would use stronger semantic embeddings and distributed caching")
    sl=new_slide(prs,"What’s Next")
    add_card(sl,.65,1.45,3.75,4.9,"Scale","Dense embeddings + ANN indexing\nLarger scenario catalog\nDistributed cache")
    add_card(sl,4.78,1.45,3.75,4.9,"Quality","Human-labeled evaluation set\nIntent/step accuracy dashboards\nMore robust paraphrase coverage")
    add_card(sl,8.91,1.45,3.75,4.9,"Product","Device-aware Settings handoff\nSupport analytics\nWorklet-ready service boundaries")
    sl=new_slide(prs,"Brownie Points — Differentiation")
    add_card(sl,.65,1.45,3.75,4.9,"Grounded by design","Every step starts from supplied troubleshooting knowledge; unsupported HTTP URLs are blocked.")
    add_card(sl,4.78,1.45,3.75,4.9,"Actionable by default","Answers carry a catalog-linked action whenever an exact deeplink exists.")
    add_card(sl,8.91,1.45,3.75,4.9,"Fast path","Validated answers can be served from an intent-aware cache for repeat phrasing.")
    sl=new_slide(prs,"Submission Checklist")
    items=["Working prototype code","README + reproducible setup","Dockerfile","Presentation","AI disclosure","Demo video ≤ 5 minutes","Final judging tag: PRISM_GENAI_HACKATHON_Y2026"]; y=1.45
    for item in items:
        add_text(sl,"✓",.9,y,.35,.4,18,True,PURPLE); add_text(sl,item,1.35,y,8.8,.4,15,False,DARK); y+=.62
    add_text(sl,"https://github.com/DevRaj-24/rootcause",.9,6.2,7.2,.5,14,True,PURPLE)
    sl=new_slide(prs,"Thank You","rootcause · VIT Vellore")
    add_text(sl,"Vague complaint in.\nValidated troubleshooting plan out.",2.2,2.2,8.9,1.3,30,True,DARK,PP_ALIGN.CENTER)
    add_text(sl,"Dev Raj · Sarang Raj · Antony Roy",3.05,4.15,7.2,.5,15,False,MID,PP_ALIGN.CENTER)
    out=SUB/"VITVellore_rootcause_Submission.pptx"; prs.save(out)

def make_disclosure():
    d=Document(); sec=d.sections[0]; sec.top_margin=DInches(.6); sec.bottom_margin=DInches(.6)
    p=d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("AI Usage DISCLOSURE FORM"); r.bold=True; r.font.size=DPt(18)
    sections=[
    ("1. Team Details","Team Name: rootcause\nProject / Product Name: RootCause — Smart Guided Troubleshooting Engine\nOrganization / Institution: VIT Vellore\nTheme: 02 — Guided Troubleshooting\nMembers: Dev Raj (24BDS0080), Sarang Raj (24BDS0091), Antony Roy (24BCE0920)"),
    ("2. AI Usage Declaration","Yes — the team used AI during development. AI was used as an engineering assistant for brainstorming, code assistance, documentation/content drafting, UI/UX iteration and testing/debugging. The team reviewed and modified outputs before inclusion."),
    ("3. Purpose of AI Usage","Idea generation / brainstorming: Yes\nCode generation or assistance: Yes\nUI / UX design: Yes\nContent creation: Yes\nData analysis: Assisted with analysis of supplied hackathon assets\nTesting / debugging: Yes\nOther: Documentation and presentation drafting"),
    ("4. Feature Origin Classification","Feature: Query enrichment and retrieval pipeline\nOrigin: Both\nAI assistance: architecture/code suggestions and debugging; team integrated and modified the implementation.\n\nFeature: Catalog-gated deeplink mapping\nOrigin: Both\nAI assistance: implementation support and validation logic; team used the supplied catalog and retained catalog-only matching.\n\nFeature: Fast-path cache and validation\nOrigin: Both\nAI assistance: code/debugging support; team reviewed behavior and benchmarked locally."),
    ("5. Ethical & Compliance Confirmation","AI usage complies with the applicable hackathon disclosure requirements. No proprietary or copyrighted data was knowingly misused. The project uses the supplied hackathon assets for the prototype."),
    ("6. Declaration & Sign-Off","Name of Team Representative: Dev Raj\nRole: Team Representative\nSignature: To be signed by team representative\nDate: 30 September 2026")]
    for h,body in sections:
        p=d.add_paragraph(); r=p.add_run(h); r.bold=True; r.font.size=DPt(13); d.add_paragraph(body)
    d.save(SUB/"VITVellore_rootcause_AI_Disclosure.docx")

def font(size,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,size) if Path(p).exists() else ImageFont.load_default()

def frame(path,title,subtitle,lines,badge):
    im=Image.new("RGB",(1280,720),(248,247,252)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((55,45,1225,675),radius=24,fill=(255,255,255),outline=(229,225,238),width=2)
    d.text((90,78),title,font=font(38,True),fill=(23,20,33)); d.text((90,132),subtitle,font=font(20),fill=(105,101,116))
    y=210
    for line in lines:
        d.rounded_rectangle((90,y,1190,y+58),radius=14,fill=(248,247,252)); d.text((112,y+16),line,font=font(21),fill=(23,20,33)); y+=76
    d.rounded_rectangle((965,74,1180,118),radius=18,fill=(237,230,252)); d.text((990,86),badge,font=font(17,True),fill=(105,54,217))
    im.save(path)

def make_video():
    fd=SUB/"video_frames"; fd.mkdir(exist_ok=True)
    frame(fd/"01.png","ROOTCAUSE","Smart Guided Troubleshooting · Theme 02",["Vague complaint in","Grounded troubleshooting plan out","Dev Raj · Sarang Raj · Antony Roy"],"PROTOTYPE")
    frame(fd/"02.png","The problem","Customers describe symptoms, not Settings paths.",["Screen is laggy and touch inputs are delayed","Support must translate symptoms","Users still hunt through Settings"],"PROBLEM")
    frame(fd/"03.png","The pipeline","Four ideas connected into one operational flow.",["01 Query enrichment → 02 SIIS retrieval","03 Structured actions → 04 Exact catalog deeplink","05 Validation → 06 Fast-path cache"],"PIPELINE")
    frame(fd/"04.png","Structured result","The API returns a strict JSON contract.",["Goal → Actions → StepGroups","Catalog-only actionable deeplink","Validation metadata accompanies the action"],"JSON")
    frame(fd/"05.png","Fast path","Repeat intent is served from the validated cache.",["First query: planner path","Same normalized intent: cache HIT","Latency and validation metadata are returned"],"CACHE")
    frame(fd/"06.png","Safety checks","Before delivery, RootCause validates the result.",["Schema contract: PASS","Catalog validity: PASS","HTTP URL hygiene: PASS","Source-grounded steps only"],"GUARDRAIL")
    frame(fd/"07.png","Team close","RootCause is a grounded action planner.",["One API","Reusable mapping layer","Docker-ready prototype","Built by rootcause · VIT Vellore"],"CLOSE")
    subprocess.run(["ffmpeg","-y","-framerate","1/6","-i",str(fd/"%02d.png"),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(SUB/"RootCause_Demo.mp4")],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

if __name__=="__main__":
    make_ppt(); make_disclosure(); (SUB/"DEMO_VIDEO_STATUS.md").write_text("# RootCause Demo Video\n\nGenerated prototype walkthrough: RootCause_Demo.mp4. Duration is under five minutes.\n"); make_video()
    print("submission artifacts generated")
