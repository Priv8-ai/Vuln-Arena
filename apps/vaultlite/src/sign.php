<?php
$id = $_GET['id'] ?? '7';
$secret = 'vault-hmac-dev'; // also leaked in JS
echo hash_hmac('sha256', $id, $secret);
