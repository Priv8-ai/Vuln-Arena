<?php
require __DIR__.'/init_db.php';
session_start();
if (empty($_SESSION['uid'])) { header('Location: /'); exit; }
// IDOR: trusts user_id query param
$uid = $_GET['user_id'] ?? $_SESSION['uid'];
$rows = db()->query("SELECT id,user_id,amount,note,secret_flag FROM invoices WHERE user_id=".(int)$uid)->fetchAll(PDO::FETCH_ASSOC);
header('Content-Type: application/json');
echo json_encode(['invoices'=>$rows], JSON_PRETTY_PRINT);
