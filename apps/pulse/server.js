const express = require('express');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');
const app = express();
app.use(express.json());
app.use(express.urlencoded({extended:true}));
app.use('/assets', express.static(path.join(__dirname, 'public')));

const messages = [];
const reports = [];

app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'home.html'));
});

app.get('/history', (_req,res)=>res.json(messages));
app.post('/report', (req,res)=>{
  const body = req.body.body || req.body.message || '';
  reports.push(body);
  // stored XSS for "mod bot" that "views" reports
  res.json({ok:true, id:reports.length-1});
});
app.get('/report', (_req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'report.html'));
});
app.get('/mod', (_req,res)=>{
  // insecure "bot" renders reports as HTML and leaks cookie flag
  const rendered = reports.map(r=>`<div>${r}</div>`).join('');
  res.setHeader('Set-Cookie', 'MOD=ARENA{pulse_xss_chain_cookie}; Path=/');
  const page = fs.readFileSync(path.join(__dirname, 'pages', 'mod.html'), 'utf8');
  res.type('html').send(page.split('__SLOT__').join(`<h1>Mod queue</h1>${rendered}<p>bot cookie set</p>`));
});
app.get('/flag', (req,res)=>{
  const c = req.headers.cookie||'';
  if(c.includes('ARENA{pulse_xss_chain_cookie}')) return res.send('ARENA{pulse_mod_takeover}\n');
  res.status(403).send('mod cookie required');
});
app.get('/attach', (req,res)=>{
  // open redirect + content sniff
  const u = req.query.url||'/';
  res.redirect(u);
});
app.get('/api/echo', (req,res)=>{
  // charset / content-type response manipulation
  const ct = req.query.ct || 'text/plain';
  const msg = req.query.msg || 'ok';
  res.setHeader('Content-Type', ct);
  res.send(msg + (ct.includes('html') ? '<!-- ARENA{pulse_ctype_html} -->' : ''));
});

const server = http.createServer(app);
const wss = new WebSocketServer({server, path:'/ws'});
wss.on('connection', ws=>{
  ws.on('message', buf=>{
    const msg = buf.toString();
    messages.push(msg);
    // broadcast without sanitize — XSS via WS
    wss.clients.forEach(c=>{ if(c.readyState===1) c.send(msg); });
    if(msg.includes('ARENA_PING_RCE')){
      const {execSync}=require('child_process');
      try{ execSync('touch /tmp/pulse_rce'); ws.send('ARENA{pulse_ws_cmd_trigger}'); }catch(e){ ws.send(String(e)); }
    }
  });
});
app.use(express.static(path.join(__dirname, 'pages', 'marketing'), { extensions: ['html'], index: false }));

server.listen(80, ()=>console.log('pulse'));
