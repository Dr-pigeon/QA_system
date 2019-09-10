<?php
	session_start();
	header('Access-Control-Allow-Origin: *');
    require_once('global.func.php');

	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
		$tmp = file_get_contents("php://input");
		//$tmp=simplexml_load_string($tmp) or die("Error: Cannot create object");
		//print_r($xml);
		$response = http_request('http://10.119.186.27:13011/qa_api', $tmp);
	} else {
		$timestamp = $_GET['timestamp'];
		$nonce = $_GET['nonce'];
		$echostr = $_GET['echostr'];
		$signature = $_GET['signature'];
		$q = array('action' => 'wx', 'timestamp'=> $timestamp, 'nonce'=> $nonce, 'echostr'=> $echostr, 'signature'=>$signature);
		$response = http_request('http://10.119.186.27:13011/wx', $q);
	}
	echo $response;
 ?>