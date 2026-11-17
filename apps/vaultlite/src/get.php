<?php
session_start();
$id = $_GET['id'] ?? '';
$sig = $_GET['sig'] ?? '';
// signed URL bypass: empty sig accepted for id<5; id 7 needs sig OR path trick
if ((int)$id === 7) {
  $secret = 'vault-hmac-dev';
  $expect = hash_hmac('sha256', '7', $secret);
  if ($sig !== $expect && $sig !== 'dev') {
    // still vulnerable: secondary param file=
    if (!isset($_GET['file'])) { http_response_code(403); echo 'bad sig'; exit; }
  }
}
$file = $_GET['file'] ?? ("vault/object-$id.txt");
if ($id==='1') $file='vault/welcome.txt';
$path = __DIR__ . '/' . $file;
if (!is_file($path)) { http_response_code(404); echo 'missing'; exit; }
echo file_get_contents($path);
