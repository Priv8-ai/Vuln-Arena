<?php
require __DIR__.'/init_db.php';
session_start();
$email = $_POST['email'] ?? '';
$pass = $_POST['password'] ?? '';
// Vulnerable: SQL injection in login
$sql = "SELECT * FROM users WHERE email='$email' AND password='$pass' LIMIT 1";
try {
  $row = db()->query($sql)->fetch(PDO::FETCH_ASSOC);
} catch (Throwable $e) {
  http_response_code(500);
  echo "DB error: ".$e->getMessage();
  exit;
}
if ($row) {
  $_SESSION['uid']=$row['id']; $_SESSION['role']=$row['role']; $_SESSION['email']=$row['email'];
  header('Location: /dashboard.php'); exit;
}
echo "Login failed. <a href='/'>Back</a>";
