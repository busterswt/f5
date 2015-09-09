<?php
/*
F5 iControl Proxy for v11.4+

The purpose of this script is to proxy ReST iControl API commands to the F5.
This script will provide the credentials and SSL socket necessary to communicate with the F5.

There are a limited number of allowed commands.

james.denton@rackspace.com
*/

require('proxy_include.ini');

/* Perform simple authentication check to the proxy */

if (isset($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'])) {
        if ( ($_SERVER['PHP_AUTH_USER'] != $proxy_username) || ($_SERVER['PHP_AUTH_PW'] != $proxy_password)) {
                die(http_response_code(401));
        }
} else {
        die(http_response_code(401));
}

/* Check to see OpenStack token was passed by the client and that it was valid */
// Not yet implemented


/* BEGIN URI VALIDATION */

//Initialize variables
$methodAllowed = false;
$uriAllowed = false;

foreach ($allowedMethod as $method) {
	if ( is_numeric (strrpos($_SERVER['REQUEST_METHOD'], $method))) {
		$methodAllowed = true;
		break;
	}
}

if ( !$methodAllowed ) {
	error_log("Request method not allowed - ".$_SERVER['REMOTE_ADDR']." - ".$_SERVER['REQUEST_URI']);
	die(http_response_code(405));
}

foreach ($allowedURI as $uri) {
	error_log ($uri);
	if ( is_numeric(strrpos($_SERVER['REQUEST_URI'], $uri))) {
		$uriAllowed = true;
		break;
	}
}

if ( !$uriAllowed ) {
	error_log("Request URI not allowed - ".$_SERVER['REMOTE_ADDR']." - ".$_SERVER['REQUEST_URI']);
	die(http_response_code(403));
}
/* END URI VALIDATION */

//Implement a fix to populate the $_POST variable.
//$_POST is normally only populated by URL encoded form data
$postdata = file_get_contents("php://input");

//canonical trailing slash
$proxy_base_url_canonical = rtrim($proxy_base_url, '/ ') . '/';

//check if valid
if( strpos($_SERVER['REQUEST_URI'], $proxy_base_url) !== 0 )
{
    die("The config paramter \$prox_base_url \"$proxy_base_url\" that you specified
        does not match the beginning of the request URI: ".
        $_SERVER['REQUEST_URI']);
}

//remove base_url and optional index.php from request_uri
$proxy_request_url = substr($_SERVER['REQUEST_URI'], strlen($proxy_base_url_canonical));

if( strpos($proxy_request_url, 'index.php') === 0 )
{
    $proxy_request_url = ltrim(substr($proxy_request_url, strlen('index.php')), '/');
}

//final proxied request url
$proxy_request_url = "https://". rtrim($dest_host, '/ ') . '/' . $proxy_request_url;

// Procure the OpenStack token from the payload
// and test to make sure its valid

$requestPayload = json_decode($postdata, true);
//if ( isset($requestPayload['token'])) {
//    $openstackToken = $requestPayload['token'];
//} else {
//    error_log("No token specified");
//    header('HTTP/1.1 401 Token Not Specified');
//    die();
//}

/* Init CURL */
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $proxy_request_url);
curl_setopt($ch, CURLOPT_AUTOREFERER, 1);
curl_setopt($ch, CURLOPT_USERPWD, "$f5_username:$f5_password");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_HEADER, 1);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);
curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

$requestMethod = strtoupper($_SERVER['REQUEST_METHOD']);
if ( $requestMethod == ("POST" || "PUT") ) {
    error_log("Request method? ".$_SERVER['REQUEST_METHOD']); // Debug
   
    if( sizeof($postdata) > 0 )	{
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata);
    }
}

curl_setopt($ch, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_0);
$res = curl_exec($ch);
curl_close($ch);

/* Proxy Response */
$proxied_headers = array('Content-Type','Location');
list($headers, $body) = explode("\r\n\r\n", $res, 2);

$headers = explode("\r\n", $headers);
$hs = array();

foreach($headers as $header)
{
    if( false !== strpos($header, ':') )
    {
        list($h, $v) = explode(':', $header);
        $hs[$h][] = $v;
    }
    else
    {
        $header1  = $header;
    }
}

list($proto, $code, $text) = explode(' ', $header1);
header($_SERVER['SERVER_PROTOCOL'] . ' ' . $code . ' ' . $text);

foreach($proxied_headers as $hname)
{
    if( isset($hs[$hname]) )
    {
        foreach( $hs[$hname] as $v )
        {
            header($hname.": " . $v);
        }
    }
}
/* End Response */

die($body);

?>
