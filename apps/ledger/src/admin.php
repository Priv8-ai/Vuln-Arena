<?php
session_start();
if (($_SESSION['role'] ?? '') !== 'admin') { http_response_code(403); echo 'admin only'; exit; }
echo "Admin OK. ARENA{ledger_admin_panel}\n";
