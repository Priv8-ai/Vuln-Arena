<?php
header('Content-Type: application/json');
echo json_encode(['objects'=>[['id'=>1,'name'=>'welcome.txt'],['id'=>7,'name'=>'object-7.txt','note'=>'internal']]]);
