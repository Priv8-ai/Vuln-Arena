from fastapi import FastAPI, Request, Header
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import httpx, os, subprocess, time
from jinja2 import Environment

app = FastAPI(title="Forge Webhooks")
ROOT = Path(__file__).resolve().parent
ENV = Environment()
JOBS = {}

def _page(name: str) -> HTMLResponse:
    return HTMLResponse((ROOT / "pages" / f"{name}.html").read_text(encoding="utf-8"))

@app.get("/", response_class=HTMLResponse)
def home():
    return _page("home")

@app.post("/hooks/test")
async def hooks(request: Request):
    data = await request.json()
    url = data.get("url","")
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=5.0)
    return PlainTextResponse(r.text[:4000])

@app.get("/internal/token")
def token():
    return {"token":"forge-internal-token","flag":"ARENA{forge_internal_token}"}

@app.get("/internal/admin")
def iadmin(x_forge_token: str | None = Header(default=None)):
    if x_forge_token != "forge-internal-token":
        return PlainTextResponse("no", status_code=403)
    return PlainTextResponse("ARENA{forge_token_chain}\n")

@app.post("/jobs")
async def create_job(request: Request):
    data = await request.json()
    # race-friendly status flip
    jid = str(int(time.time()*1000) % 100000)
    JOBS[jid] = {"status":"pending", "cmd": data.get("cmd","echo hi"), "owner": data.get("owner","guest")}
    return {"id": jid}

@app.get("/jobs/{jid}")
def get_job(jid: str, finalize: int = 0):
    job = JOBS.get(jid)
    if not job: return JSONResponse({"error":"no"}, status_code=404)
    if finalize and job["status"]=="pending":
        # TOCTOU: finalize can race with mutate endpoint
        out = subprocess.getoutput(job["cmd"])
        job["status"]="done"
        job["out"]=out
        if "flag" in out.lower() or os.path.exists("/tmp/forge_rce"):
            job["flag"]="ARENA{forge_job_rce}"
    return job

@app.post("/jobs/{jid}/mutate")
async def mutate(jid: str, request: Request):
    data = await request.json()
    job = JOBS.get(jid)
    if not job: return JSONResponse({"error":"no"}, status_code=404)
    # can change cmd while pending
    if "cmd" in data: job["cmd"]=data["cmd"]
    if "status" in data: job["status"]=data["status"]
    return job

@app.get("/template")
def template(name: str = "world"):
    # SSTI
    try:
        return PlainTextResponse(ENV.from_string("Hello " + name).render())
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

@app.get("/download")
def download(f: str = "private.env"):
    path = os.path.join("/app/jobs", f)
    with open(path, "r", errors="ignore") as fh:
        return PlainTextResponse(fh.read())

@app.get("/redirect")
def redir(next: str = "/"):
    return RedirectResponse(next)

@app.get("/headers")
def headers(request: Request):
    # response manipulation via hop-by-hop-ish custom
    weird = request.headers.get("x-output-mode","plain")
    body = "pong"
    if weird == "jsonp":
        cb = request.query_params.get("cb","cb")
        return PlainTextResponse(f"{cb}({{\"flag\":\"ARENA{{forge_jsonp}}\"}})", media_type="application/javascript")
    return PlainTextResponse(body)

@app.get("/product", response_class=HTMLResponse, include_in_schema=False)
def page_product():
    return _page("product")

@app.get("/pricing", response_class=HTMLResponse, include_in_schema=False)
def page_pricing():
    return _page("pricing")

@app.get("/customers", response_class=HTMLResponse, include_in_schema=False)
def page_customers():
    return _page("customers")

@app.get("/guide", response_class=HTMLResponse, include_in_schema=False)
def page_guide():
    return _page("docs")

@app.get("/changelog", response_class=HTMLResponse, include_in_schema=False)
def page_changelog():
    return _page("changelog")

app.mount("/assets", StaticFiles(directory=str(ROOT / "static")), name="assets")
