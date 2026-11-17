<?php
// LFI
$page = $_GET['page'] ?? 'help.txt';
$path = __DIR__.'/pages/'.$page;
echo "<pre>";
include $path; // also allows php wrappers if page=....
echo "</pre>";
