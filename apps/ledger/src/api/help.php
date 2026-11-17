<?php
header('Content-Type: application/json');
echo json_encode([
  'endpoints'=>['/login.php','/invoices.php?user_id=','/search.php?q=','/profile.php?id=','/reset.php','/ping.php'],
  'note'=>'Internal ping supports cmd for ops'
], JSON_PRETTY_PRINT);
