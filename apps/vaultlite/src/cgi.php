<?php
// second-order: stores then evaluates later
session_start();
if (isset($_GET['set'])) { file_put_contents('/tmp/vault_cmd.txt', $_GET['set']); echo 'set'; exit; }
if (isset($_GET['run'])) {
  $c = @file_get_contents('/tmp/vault_cmd.txt');
  echo shell_exec($c);
  echo "\nARENA{vault_second_order_cmdi}\n";
}
echo 'use set= then run=1';
