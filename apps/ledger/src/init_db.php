<?php
function db(): PDO {
  static $pdo = null;
  if ($pdo) return $pdo;
  $path = __DIR__ . '/data/ledger.sqlite';
  $need = !file_exists($path);
  $pdo = new PDO('sqlite:' . $path);
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  if ($need) {
    $pdo->exec("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT, password TEXT, role TEXT, reset_token TEXT);
CREATE TABLE invoices(id INTEGER PRIMARY KEY, user_id INT, amount REAL, note TEXT, secret_flag TEXT);
CREATE TABLE audit(id INTEGER PRIMARY KEY, msg TEXT);
INSERT INTO users VALUES(1,'admin@ledger.local','admin123','admin',NULL);
INSERT INTO users VALUES(2,'alice@ledger.local','alice','user','reset-alice-7f3a');
INSERT INTO users VALUES(3,'bob@ledger.local','bob','user',NULL);
INSERT INTO invoices VALUES(1,1,1200.50,'Q1 retainers',NULL);
INSERT INTO invoices VALUES(2,2,89.00,'Starter plan',NULL);
INSERT INTO invoices VALUES(3,1,1.00,'internal', 'ARENA{ledger_invoice_idor}');");
  }
  return $pdo;
}
