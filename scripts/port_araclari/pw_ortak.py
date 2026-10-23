import json,sys,re
from playwright.sync_api import sync_playwright
SP=sys.argv[1] if len(sys.argv)>1 else "."
CFG=json.load(open(SP+"/uxtest.json"))
import os
BASE=os.environ.get("BASE","http://127.0.0.1:5001")
def baslat(p,tema="light",mobil=False,lang=None):
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":390,"height":844} if mobil else {"width":1366,"height":850},color_scheme=tema,locale="en-US" if lang=="en" else "tr-TR")
    return b,ctx
def giris(page,email):
    page.goto(BASE+"/login"); page.fill('input[name="email"]',email); page.fill('input[name="password"]',CFG["pw"])
    page.click('button[type="submit"]'); page.wait_for_load_state("networkidle")
