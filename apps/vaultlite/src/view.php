<?php
$f = $_GET['f'] ?? 'vault/welcome.txt';
// LFI / include RCE
include $f;
