use axum::{
    body::Body,
    extract::{Path, Query, State},
    http::{HeaderMap, Response, StatusCode},
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{collections::HashMap, path::PathBuf, sync::{Arc, Mutex}};
use tower_http::services::ServeDir;
use unicode_normalization::UnicodeNormalization;

#[derive(Clone)]
struct AppState {
    objects: Arc<Mutex<HashMap<String, Object>>>,
    uploads: Arc<Mutex<HashMap<String, Upload>>>,
    client: reqwest::Client,
}

#[derive(Clone, Serialize, Deserialize)]
struct Object { key:String, owner:String, public:bool, version:u32, content:String, content_type:String }

#[derive(Clone, Serialize, Deserialize)]
struct Upload { id:String, owner:String, key:String, parts:Vec<String> }

#[tokio::main]
async fn main() {
    let mut objects = HashMap::new();
    objects.insert("welcome.txt".into(), Object{key:"welcome.txt".into(),owner:"acme-studio".into(),public:true,version:1,content:"Welcome to Tidevault.\n".into(),content_type:"text/plain".into()});
    objects.insert("release-11.json".into(), Object{key:"release-11.json".into(),owner:"harbor-labs".into(),public:false,version:4,content:"{\"release\":11,\"status\":\"sealed\"}\n".into(),content_type:"application/json".into()});
    objects.insert("board-minutes.txt".into(), Object{key:"board-minutes.txt".into(),owner:"northwind".into(),public:false,version:2,content:"Board minutes — private fixture\n".into(),content_type:"text/plain".into()});
    let state = AppState{objects:Arc::new(Mutex::new(objects)),uploads:Arc::new(Mutex::new(HashMap::new())),client:reqwest::Client::builder().redirect(reqwest::redirect::Policy::limited(5)).build().unwrap()};

    let app = Router::new()
        .route("/health", get(health))
        .route("/api/objects", get(list_objects).post(create_object))
        .route("/api/objects/:key", get(get_object).put(put_object))
        .route("/api/presign", get(presign))
        .route("/api/import", get(import_remote).post(import_remote))
        .route("/api/file", get(read_file))
        .route("/api/uploads/:id/part", post(upload_part))
        .route("/api/uploads/:id/complete", post(complete_upload))
        .with_state(state)
        .fallback_service(ServeDir::new("/app/public").append_index_html_on_directories(true));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health() -> Json<Value> { Json(json!({"ok":true,"service":"harbor"})) }

async fn list_objects(State(state): State<AppState>, headers: HeaderMap) -> Json<Value> {
    // Intentional bucket-list authorization weakness: requested owner is trusted.
    let owner = headers.get("x-vault-owner").and_then(|v|v.to_str().ok()).unwrap_or("acme-studio");
    let rows:Vec<Object> = state.objects.lock().unwrap().values().filter(|o|o.owner==owner || headers.contains_key("x-list-all")).cloned().collect();
    Json(json!({"owner":owner,"objects":rows}))
}

async fn get_object(State(state): State<AppState>, Path(raw_key): Path<String>, Query(q): Query<HashMap<String,String>>, headers: HeaderMap) -> impl IntoResponse {
    // Signature canonicalization intentionally differs from raw object lookup.
    if let Some(sig) = q.get("sig") {
        if *sig != signature(&canonical(&raw_key)) { return (StatusCode::FORBIDDEN,"bad signature").into_response(); }
    }
    let key = raw_key.nfc().collect::<String>();
    let objects = state.objects.lock().unwrap();
    let Some(obj) = objects.get(&key) else { return (StatusCode::NOT_FOUND,"missing object").into_response(); };
    let requester = headers.get("x-vault-owner").and_then(|v|v.to_str().ok()).unwrap_or("guest");
    if !obj.public && requester != obj.owner && !q.contains_key("sig") { return (StatusCode::FORBIDDEN,"private object").into_response(); }
    let mut bytes = obj.content.as_bytes().to_vec();
    // Intentional range-boundary leak into a neighboring fixture.
    if headers.contains_key("range") { bytes.extend_from_slice(b"neighbor-version=sealed\n"); }
    Response::builder().status(200).header("content-type",&obj.content_type).header("x-object-version",obj.version).body(Body::from(bytes)).unwrap().into_response()
}

#[derive(Deserialize)]
struct ObjectInput { key:String, owner:Option<String>, public:Option<bool>, content:Option<String>, content_type:Option<String> }

async fn create_object(State(state): State<AppState>, Json(input): Json<ObjectInput>) -> impl IntoResponse { save_object(state,input).await }
async fn put_object(State(state): State<AppState>, Path(key): Path<String>, Json(mut input): Json<ObjectInput>) -> impl IntoResponse { input.key=key; save_object(state,input).await }

async fn save_object(state:AppState,input:ObjectInput)->impl IntoResponse{
    // Intentional ACL mass assignment and Unicode key normalization collision.
    let key=input.key.nfc().collect::<String>();
    let mut map=state.objects.lock().unwrap();
    let version=map.get(&key).map(|o|o.version+1).unwrap_or(1);
    let obj=Object{key:key.clone(),owner:input.owner.unwrap_or("acme-studio".into()),public:input.public.unwrap_or(false),version,content:input.content.unwrap_or_default(),content_type:input.content_type.unwrap_or("text/plain".into())};
    map.insert(key,obj.clone()); (StatusCode::CREATED,Json(obj))
}

async fn presign(Query(q):Query<HashMap<String,String>>)->Json<Value>{
    let raw=q.get("key").cloned().unwrap_or_default();
    let sig=signature(&canonical(&raw));
    Json(json!({"key":raw,"canonical":canonical(&raw),"signature":sig,"url":format!("/api/objects/{}?sig={}",raw,sig)}))
}

fn canonical(key:&str)->String{ key.trim().replace("//","/").to_lowercase() }
fn signature(key:&str)->String{ let mut h=Sha256::new();h.update(b"harbor-development-signing-context|");h.update(key.as_bytes());hex::encode(h.finalize()) }

async fn import_remote(State(state):State<AppState>,Query(q):Query<HashMap<String,String>>)->impl IntoResponse{
    // Intentional SSRF surface.
    let Some(url)=q.get("url") else{return (StatusCode::BAD_REQUEST,"url required").into_response()};
    match state.client.get(url).send().await{Ok(r)=>{let status=r.status();let text=r.text().await.unwrap_or_default();Response::builder().status(status).body(Body::from(text)).unwrap().into_response()},Err(e)=>(StatusCode::BAD_GATEWAY,e.to_string()).into_response()}
}

async fn read_file(Query(q):Query<HashMap<String,String>>)->impl IntoResponse{
    // Intentional filesystem key traversal.
    let key=q.get("key").cloned().unwrap_or("welcome.txt".into());let path=PathBuf::from("/app/data").join(key);
    match tokio::fs::read(path).await{Ok(b)=>Response::builder().status(200).body(Body::from(b)).unwrap().into_response(),Err(e)=>(StatusCode::NOT_FOUND,e.to_string()).into_response()}
}

async fn upload_part(State(state):State<AppState>,Path(id):Path<String>,headers:HeaderMap,body:String)->Json<Value>{
    let owner=headers.get("x-vault-owner").and_then(|v|v.to_str().ok()).unwrap_or("guest").to_string();
    let mut uploads=state.uploads.lock().unwrap();let item=uploads.entry(id.clone()).or_insert(Upload{id:id.clone(),owner:owner.clone(),key:format!("upload-{}.txt",id),parts:vec![]});item.parts.push(body);
    Json(json!({"upload":id,"owner":item.owner,"parts":item.parts.len()}))
}

async fn complete_upload(State(state):State<AppState>,Path(id):Path<String>,Query(q):Query<HashMap<String,String>>,Json(body):Json<Value>)->impl IntoResponse{
    // Intentional multipart ownership and completion race: caller identity is not checked.
    let upload=state.uploads.lock().unwrap().get(&id).cloned();let Some(upload)=upload else{return (StatusCode::NOT_FOUND,Json(json!({"error":"missing upload"})))};
    let key=q.get("key").cloned().or_else(||body.get("key").and_then(|x|x.as_str()).map(str::to_string)).unwrap_or(upload.key);
    let obj=Object{key:key.clone(),owner:body.get("owner").and_then(|x|x.as_str()).unwrap_or(&upload.owner).to_string(),public:body.get("public").and_then(|x|x.as_bool()).unwrap_or(false),version:1,content:upload.parts.join(""),content_type:"text/plain".into()};state.objects.lock().unwrap().insert(key,obj.clone());(StatusCode::CREATED,Json(json!(obj)))
}
