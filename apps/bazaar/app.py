#!/usr/bin/env python3
import os, sqlite3, subprocess, json
from flask import Flask, request, render_template, session, redirect, jsonify, make_response
import requests as req

app = Flask(__name__)
app.secret_key = "bazaar-dev-secret"
DB = "/app/data/bazaar.db"

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    os.makedirs("/app/data", exist_ok=True)
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, user TEXT, pass TEXT, role TEXT);
    CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, seller TEXT, title TEXT, price REAL, desc TEXT);
    CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY, item_id INT, body TEXT);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user TEXT, item_id INT, qty INT, total REAL);
    DELETE FROM users; DELETE FROM items; DELETE FROM reviews; DELETE FROM orders;
    INSERT INTO users VALUES(1,'admin','admin','admin'),(2,'mia','mia','user');
    INSERT INTO items VALUES(1,'admin','Copper kettle',12.5,'Nice kettle'),
      (2,'admin','Flag spice',0.01,'ARENA{bazaar_item_desc}');
    """)
    con.commit(); con.close()

init()

@app.get("/")
def home():
    items = db().execute("select * from items").fetchall()
    return render_template("index.html", items=items, user=session.get("user"), active="home")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u, p = request.form.get("user",""), request.form.get("pass","")
        # SQLi
        q = f"select * from users where user='{u}' and pass='{p}'"
        try:
            row = db().execute(q).fetchone()
        except Exception as e:
            return f"error: {e}", 500
        if row:
            session["user"]=row["user"]; session["role"]=row["role"]
            return redirect("/")
        return "fail", 401
    return render_template("login.html", user=session.get("user"), active="login")

@app.get("/item/<int:iid>")
def item(iid):
    it = db().execute("select * from items where id=?", (iid,)).fetchone()
    revs = db().execute("select * from reviews where item_id=?", (iid,)).fetchall()
    return render_template("item.html", item=it, reviews=revs, user=session.get("user"), active="home")

@app.post("/review/<int:iid>")
def review(iid):
    body = request.form.get("body","")
    db().execute("insert into reviews(item_id,body) values(?,?)", (iid, body))
    db().commit()
    # stored XSS
    return redirect(f"/item/{iid}")

@app.post("/buy")
def buy():
    # business logic: trust client price & negative qty
    user = session.get("user") or "guest"
    item_id = int(request.form.get("item_id", 0))
    qty = int(request.form.get("qty", 1))
    price = float(request.form.get("price", 0))
    total = qty * price
    db().execute("insert into orders(user,item_id,qty,total) values(?,?,?,?)", (user,item_id,qty,total))
    db().commit()
    flag = ""
    if total < 0:
        flag = " ARENA{bazaar_negative_total}"
    if price == 0 and item_id == 1:
        flag += " ARENA{bazaar_price_tamper}"
    return f"ordered total={total}{flag}"

@app.get("/hook")
def hook():
    # SSRF
    url = request.args.get("url","")
    if not url:
        return "need url"
    try:
        r = req.get(url, timeout=3)
        return r.text[:2000]
    except Exception as e:
        return str(e), 502

@app.get("/render")
def render_tpl():
    # SSTI
    name = request.args.get("name","guest")
    try:
        return render_template_string_user(name)
    except Exception as e:
        return str(e), 500

def render_template_string_user(name):
    from flask import render_template_string
    # intentionally vulnerable
    return render_template_string(f"Hello {name}")

@app.get("/fetch-file")
def fetch_file():
    # path traversal
    path = request.args.get("path","secret.txt")
    base = "/app/data/"
    with open(base + path, "r", errors="ignore") as f:
        return f.read()

@app.get("/export")
def export():
    # response manipulation / content-type confusion
    data = {"ok": True, "note": "export"}
    body = json.dumps(data)
    if request.args.get("fmt") == "raw":
        # attacker-controlled callback wrapper
        cb = request.args.get("cb","x")
        resp = make_response(f"{cb}({body})")
        resp.headers["Content-Type"] = "application/javascript"
        return resp
    if request.args.get("ctype"):
        resp = make_response(body + "\n<!-- ARENA{bazaar_ctype_confusion} -->")
        resp.headers["Content-Type"] = request.args.get("ctype")
        return resp
    return jsonify(data)

@app.get("/ops/ping")
def ops_ping():
    host = request.args.get("host","127.0.0.1")
    out = subprocess.getoutput(f"ping -c 1 {host}")
    if "ARENA" in out or os.path.exists("/tmp/bazaar_rce"):
        out += "\nARENA{bazaar_cmdi}\n"
    # drop marker instruction: payload can touch file
    return f"<pre>{out}</pre>"

@app.get("/redirect")
def redir():
    nxt = request.args.get("next","/")
    return redirect(nxt)

@app.get("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /ops/\nDisallow: /internal/meta\n"

@app.get("/internal/meta")
def meta():
    # mock cloud metadata for SSRF chain
    return jsonify({"role":"web","secret":"ARENA{bazaar_metadata_ssrf}","admin_token":"bazaar-admin-token"})

@app.get("/internal/admin")
def iadmin():
    tok = request.headers.get("X-Admin-Token","")
    if tok != "bazaar-admin-token":
        return "no", 403
    return "ARENA{bazaar_ssrf_chain_admin}\n"

@app.get("/about")
def about_page():
    return render_template("about.html", user=session.get("user"), active="about")

@app.get("/sellers")
def sellers_page():
    return render_template("sellers.html", user=session.get("user"), active="sellers")

@app.get("/journal")
def journal_page():
    return render_template("journal.html", user=session.get("user"), active="journal")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
