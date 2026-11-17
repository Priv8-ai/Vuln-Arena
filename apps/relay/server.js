const express = require('express');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const path = require('path');
const app = express();
app.use(express.json({strict:false}));
app.use(express.urlencoded({extended:true}));
app.use('/assets', express.static(path.join(__dirname, 'public')));

const SECRET = 'relay-hmac-secret';
const users = {
  alice: {pass:'alice', role:'user', id:2},
  admin: {pass:'admin', role:'admin', id:1}
};
const notes = {1: {owner:1, body:'admin note ARENA{relay_note_idor}'}, 2:{owner:2, body:'alice note'}};
const FLAG = {
  jwtnone: 'ARENA{relay_jwt_none}',
  proto: 'ARENA{relay_proto_pollution}',
  gql: 'ARENA{relay_graphql_authz}',
  mass: 'ARENA{relay_mass_assignment}',
  batch: 'ARENA{relay_json_duplicate}',
  debug: 'ARENA{relay_debug_header}',
  xss: 'ARENA{relay_dom_hint}'
};

app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'home.html'));
});

app.post('/auth/login', (req,res)=>{
  const {user, pass} = req.body||{};
  const u = users[user];
  if(!u || u.pass !== pass) return res.status(401).json({error:'no'});
  const token = jwt.sign({sub:u.id, user, role:u.role}, SECRET, {algorithm:'HS256'});
  res.json({token});
});

function parseAuth(req){
  const h = req.headers.authorization||'';
  const t = h.replace(/^Bearer\s+/i,'');
  if(!t) return null;
  try {
    // vulnerable: allows alg=none
    const parts = t.split('.');
    if(parts.length>=2){
      const header = JSON.parse(Buffer.from(parts[0],'base64url').toString());
      if(header.alg === 'none' || header.alg === 'None'){
        const payload = JSON.parse(Buffer.from(parts[1],'base64url').toString());
        payload._none = true;
        return payload;
      }
    }
    return jwt.verify(t, SECRET);
  } catch(e){ return null; }
}

app.get('/api/notes/:id', (req,res)=>{
  const auth = parseAuth(req);
  if(!auth) return res.status(401).json({error:'auth'});
  const n = notes[req.params.id];
  if(!n) return res.status(404).end();
  // IDOR: no owner check
  res.json(n);
});

app.post('/api/profile', (req,res)=>{
  const auth = parseAuth(req);
  if(!auth) return res.status(401).json({error:'auth'});
  // mass assignment
  const profile = Object.assign({user:auth.user, role:auth.role}, req.body||{});
  let flag='';
  if(profile.role === 'admin' && auth.role !== 'admin') flag = FLAG.mass;
  if(auth._none && auth.role==='admin') flag = FLAG.jwtnone;
  res.json({profile, flag});
});

app.post('/api/merge', (req,res)=>{
  // prototype pollution via recursive merge
  function merge(a,b){
    for(const k of Object.keys(b||{})){
      if(b[k] && typeof b[k]==='object'){
        if(!a[k]) a[k]={};
        merge(a[k], b[k]);
      } else a[k]=b[k];
    }
    return a;
  }
  const target = {};
  merge(target, req.body||{});
  let flag='';
  if({}.polluted === 'yes' || target.polluted === 'yes' || Object.prototype.polluted === 'yes'){
    flag = FLAG.proto;
    try{ delete Object.prototype.polluted; }catch(e){}
  }
  res.json({merged:target, flag});
});

app.post('/graphql', (req,res)=>{
  const auth = parseAuth(req);
  const q = (req.body && (req.body.query||req.body)) || '';
  const qs = typeof q === 'string' ? q : JSON.stringify(q);
  // naive graphql
  if(qs.includes('__schema') || qs.includes('Introspection')){
    return res.json({data:{__schema:{types:[{name:'Query'},{name:'SecretMutation'},{name:'User'}]}}});
  }
  if(qs.includes('secretFlag')){
    // authz missing on field
    return res.json({data:{secretFlag: FLAG.gql}});
  }
  if(qs.includes('users')){
    return res.json({data:{users:Object.keys(users).map(u=>({user:u, role:users[u].role}))}});
  }
  res.json({data:null, errors:[{message:'unknown'}]});
});

app.post('/api/batch', (req,res)=>{
  // duplicate JSON key weirdness — body already parsed; simulate via header
  const raw = req.headers['x-raw-json']||'';
  let flag='';
  if(raw.includes('"role":"user"') && raw.includes('"role":"admin"')) flag = FLAG.batch;
  res.json({ok:true, flag});
});

app.get('/health', (req,res)=>{
  if(req.headers['x-relay-debug']==='1'){
    return res.json({ok:true, secret:SECRET, flag:FLAG.debug});
  }
  res.json({ok:true});
});

app.use(express.static(path.join(__dirname, 'pages'), { extensions: ['html'], index: false }));

app.listen(80, ()=>console.log('relay on 80'));
