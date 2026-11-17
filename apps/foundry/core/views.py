from __future__ import annotations
import base64, json, os, pickle, subprocess, time
from pathlib import Path
import redis, requests
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt

BUILDS = {
    7201:{"id":7201,"org":"acme-studio","repo":"northwind/web","ref":"main","state":"passed","minutes":4.2,"visibility":"private","owner":"acme-studio"},
    7202:{"id":7202,"org":"harbor-labs","repo":"harbor/console","ref":"release/11","state":"running","minutes":2.7,"visibility":"private","owner":"harbor-labs"},
    7203:{"id":7203,"org":"acme-studio","repo":"northwind/worker","ref":"fix/archive","state":"queued","minutes":0,"visibility":"private","owner":"acme-studio"},
}
LOGS = ["Runner 03 connected", "Restored dependency cache", "Waiting for release approval"]
CREDITS = {7203: 1}

def home(request: HttpRequest):
    return render(request, "index.html", {"builds": sorted(BUILDS.values(), key=lambda b:b["id"], reverse=True)})

def health(request: HttpRequest): return JsonResponse({"ok":True,"service":"foundry"})

@csrf_exempt
def builds(request: HttpRequest):
    if request.method == "GET": return JsonResponse({"builds":list(BUILDS.values())})
    data = json.loads(request.body or b"{}")
    build_id = max(BUILDS) + 1
    # Intentional benchmark mass assignment.
    BUILDS[build_id] = {"id":build_id,"org":data.get("org","acme-studio"),"repo":data.get("repo","demo/app"),"ref":data.get("ref","main"),"state":"queued","minutes":0,"visibility":data.get("visibility","private"),"owner":data.get("owner",data.get("org","acme-studio"))}
    CREDITS[build_id] = 1
    return JsonResponse(BUILDS[build_id], status=201)

def build_detail(request: HttpRequest, build_id: int):
    # Intentional object authorization failure.
    item = BUILDS.get(build_id)
    return JsonResponse(item) if item else JsonResponse({"error":"missing"}, status=404)

@csrf_exempt
def consume_credit(request: HttpRequest, build_id: int):
    # Intentional check/use race.
    available = CREDITS.get(build_id, 0); time.sleep(.08)
    if available < 1: return JsonResponse({"error":"no credit"}, status=409)
    CREDITS[build_id] = available - 1
    return JsonResponse({"started":True,"build":build_id,"remaining":CREDITS[build_id]})

def webhook_test(request: HttpRequest):
    # Intentional SSRF surface.
    url = request.GET.get("url", "")
    if not url: return JsonResponse({"error":"url required"}, status=400)
    try:
        response = requests.get(url, timeout=4, allow_redirects=True)
        return HttpResponse(response.content[:4000], content_type=response.headers.get("content-type","text/plain"), status=response.status_code)
    except Exception as exc: return JsonResponse({"error":str(exc)}, status=502)

def render_name(request: HttpRequest):
    # Intentional server-side template construction.
    value = request.GET.get("name", "release")
    try: return HttpResponse(Template("<strong>Build label</strong><p>" + value + "</p>").render(Context({})))
    except Exception as exc: return HttpResponse(str(exc), status=500)

def export_file(request: HttpRequest):
    # Intentional traversal surface.
    path = Path("/app/exports") / request.GET.get("path", "sample.log")
    try: return HttpResponse(path.read_text(errors="ignore"), content_type="text/plain")
    except Exception as exc: return HttpResponse(str(exc), status=404)

@csrf_exempt
def import_task(request: HttpRequest):
    # Intentional unsafe deserialization in the isolated lab.
    try:
        obj = pickle.loads(base64.b64decode(request.body.strip()))
        return JsonResponse({"loaded_type":type(obj).__name__,"value":repr(obj)[:500]})
    except Exception as exc: return JsonResponse({"error":str(exc)}, status=400)

@csrf_exempt
def queue_task(request: HttpRequest):
    task = request.POST.get("task") or request.body.decode(errors="ignore") or "build:noop"
    try:
        client = redis.Redis(host=os.getenv("REDIS_HOST","foundry-redis"), port=6379, socket_timeout=1)
        client.lpush("celery", task)
        return JsonResponse({"queued":True,"task":task})
    except Exception as exc: return JsonResponse({"queued":False,"error":str(exc)}, status=502)

def run_ref(request: HttpRequest):
    # Intentional shell injection surface, bounded by the container.
    output = subprocess.getoutput("printf 'checking '; " + request.GET.get("ref","main"))
    return HttpResponse(output, content_type="text/plain")

@csrf_exempt
def logs(request: HttpRequest):
    if request.method == "POST": LOGS.append(request.POST.get("line") or request.body.decode(errors="ignore"))
    rows = "".join(f"<li>{line}</li>" for line in LOGS)
    return HttpResponse(f"<html><head><link rel='stylesheet' href='/assets/chrome.css'><link rel='stylesheet' href='/assets/app.css'></head><body><main class='page'><h1>Build log</h1><ul class='build-log'>{rows}</ul><form method=post><input name=line><button>Add line</button></form></main></body></html>")
