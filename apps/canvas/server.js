const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
app.set('view engine', 'ejs');
app.set('views', __dirname + '/public');
app.use(express.json({strict:false}));
app.use('/static', express.static(__dirname + '/public'));

let config = { theme:'light', title:'Kiteboard' };

function deepMerge(a,b){
  for (const k in b){
    if (b[k] && typeof b[k]==='object'){
      if (!a[k]) a[k] = {};
      deepMerge(a[k], b[k]);
    } else a[k]=b[k];
  }
  return a;
}

app.get('/', (req,res)=>{
  const html = fs.readFileSync(path.join(__dirname, 'pages', 'home.html'), 'utf8')
    .split('__CANVAS_TITLE__').join(config.title);
  res.type('html').send(html);
});

app.post('/api/settings', (req,res)=>{
  deepMerge(config, req.body||{});
  let flag='';
  if (Object.prototype.isAdmin === true || config.isAdmin === true){
    flag='ARENA{canvas_proto_admin}';
    try{ delete Object.prototype.isAdmin; }catch(e){}
  }
  res.json({config, flag});
});

app.get('/render', (req,res)=>{
  // SSTI-like ejs
  const tpl = req.query.tpl || 'Hello';
  try {
    const ejs = require('ejs');
    const out = ejs.render(tpl, {config});
    res.send(out);
  } catch(e){ res.status(500).send(String(e)); }
});

app.get('/pick', (req,res)=>{
  const file = req.query.file || 'readme.txt';
  const fs = require('fs');
  try { res.type('text').send(fs.readFileSync(__dirname+'/public/'+file,'utf8')); }
  catch(e){ res.status(404).send(String(e)); }
});

app.post('/api/import', (req,res)=>{
  // parser differential: body as array vs object
  const body = req.body;
  if (Array.isArray(body) && body[0] && body[0].role==='admin'){
    return res.json({flag:'ARENA{canvas_json_array_admin}'});
  }
  res.json({ok:true});
});

app.get('/redir', (req,res)=>{
  const t = req.query.to || '/';
  // filter bypass: //evil passes startsWith('/')
  if (t.startsWith('/') || t.startsWith('https://canvas.local')){
    return res.redirect(t);
  }
  res.status(400).send('blocked');
});

app.use(express.static(path.join(__dirname, 'pages', 'marketing'), { extensions: ['html'], index: false }));

app.listen(80, ()=>console.log('canvas'));
