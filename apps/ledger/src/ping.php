<?php
$host = $_GET['host'] ?? '127.0.0.1';
// Command injection
$out = shell_exec('ping -c 1 '. $host . ' 2>&1');
header('Content-Type: text/plain');
echo $out ?: 'no output';
if (isset($_GET['host']) && str_contains($_GET['host'], ';') || (isset($_GET['host']) && str_contains($_GET['host'], '`'))) {
  // flag dropped when injection likely used — also print if id file read
}
if (is_file('/tmp/arena_ledger_rce')) echo "\nARENA{ledger_cmdi_rce}\n";
