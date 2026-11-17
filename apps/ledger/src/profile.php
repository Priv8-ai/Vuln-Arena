<?php
require __DIR__.'/init_db.php';
$id = $_GET['id'] ?? '1';
// SQLi + info disclosure
$sql = "SELECT id,email,role,reset_token FROM users WHERE id=$id";
try {
  $u = db()->query($sql)->fetch(PDO::FETCH_ASSOC);
} catch (Throwable $e) {
  die($e->getMessage());
}
header('Content-Type: application/json');
echo json_encode($u);
