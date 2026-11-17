<?php
$key = $_GET['key'] ?? '';
if ($key !== 'ledger-debug-9c2') { http_response_code(403); echo 'forbidden'; exit; }
header('Content-Type: text/plain');
echo "LEDGER DEBUG\n";
echo "FLAG=ARENA{ledger_debug_panel}\n";
echo "DB=/var/www/html/data/ledger.sqlite\n";
