const http = require('http');
const {URL} = require('url');

const send = (res, code, body, headers={}) => {
  const data = Buffer.from(typeof body === 'string' ? body : JSON.stringify(body));
  res.writeHead(code, {'Content-Length': data.length, ...headers}); res.end(data);
};

http.createServer((req,res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'origin'}`);
  if (url.pathname === '/health') return send(res,200,{ok:true,service:'cacheline-origin'},{'Content-Type':'application/json'});

  if (url.pathname === '/api/metrics') {
    const region = req.headers['x-region'] || 'LHR';
    return send(res,200,{requests:182940,hitRate:94.7,p95:82,region,updated:'just now'},{'Content-Type':'application/json','Cache-Control':'public, max-age=60','Vary':'X-Region'});
  }
  if (url.pathname === '/api/catalog') {
    const theme = req.headers['x-site-theme'] || 'paper';
    return send(res,200,`<article data-theme="${theme}"><strong>Northwind Journal</strong><p>Cached from the London edge.</p></article>`,{'Content-Type':'text/html','Cache-Control':'public, max-age=60'});
  }
  if (url.pathname === '/api/profile') {
    const cookie = req.headers.cookie || '';
    const user = cookie.includes('EDGE_USER=admin') ? 'admin' : 'guest';
    return send(res,200,{user,email:user==='admin'?'admin@northwind.test':'guest@northwind.test',plan:user==='admin'?'enterprise':'viewer'},{'Content-Type':'application/json','Cache-Control':'public, max-age=60'});
  }
  if (url.pathname === '/api/reset-link') {
    return send(res,200,{link:`https://${req.headers.host}/reset?token=arena-reset-context`},{'Content-Type':'application/json','Cache-Control':'public, max-age=60'});
  }
  if (url.pathname === '/api/headers') {
    return send(res,200,{host:req.headers.host,original:req.headers['x-original-uri'],forwarded:req.headers['x-forwarded-for'],connection:req.headers.connection},{'Content-Type':'application/json'});
  }
  if (url.pathname === '/api/admin') {
    if (req.headers['x-edge-authorized'] === '1' || String(req.headers['x-original-uri']||'').includes('/public/../admin')) return send(res,200,{ok:true,scope:'edge-operator'},{'Content-Type':'application/json'});
    return send(res,403,{error:'edge authorization required'},{'Content-Type':'application/json'});
  }
  if (url.pathname === '/api/redirect') {
    res.writeHead(302,{Location:url.searchParams.get('to') || '/'}); return res.end();
  }
  if (url.pathname === '/api/echo') {
    const value = url.searchParams.get('value') || 'ok';
    const type = url.searchParams.get('type') || 'text/plain';
    return send(res,200,value,{'Content-Type':type,'Cache-Control':'public, max-age=60'});
  }
  return send(res,404,{error:'origin route not found',path:url.pathname,internal:'cacheline-origin:8080'},{'Content-Type':'application/json'});
}).listen(8080,'0.0.0.0',()=>console.log('cacheline origin on 8080'));
