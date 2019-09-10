<?php
	session_start();
	header('Access-Control-Allow-Origin: *');
	require_once('global.func.php');

	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
		$tmp = file_get_contents("php://input");
		$response = http_request('http://10.119.186.27:13011/applet', $tmp);
	}

	echo $response;
?>