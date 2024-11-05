<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

require_once "../services/ServerService.php";
require_once "../services/ValidationService.php";
require_once "../services/DotEnvService.php";
require_once "../database/Session.php";

(new DotEnvService(__DIR__ . "/../.env"))->load();

// Validate API key
$api_key = apache_request_headers()['X-API-Key'] ?? '';
if (!$api_key || $api_key !== getenv("OFFERS_API_KEY")) {
    http_response_code(401);
    echo json_encode([
        "success" => false,
        "error" => "Invalid API key"
    ]);
    exit;
}

$aff_sub4 = ValidationService::affSub4();
$username = ValidationService::username();
$platform = ValidationService::platform();
$followers = ValidationService::followers();

if (!$username || !$platform || !$followers) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "Missing required parameters"
    ]);
    exit;
}

$session = new Session();
$current_session = $session->get(ServerService::getIpAddress(), $aff_sub4);

// Update existing session if parameters have changed
if ($current_session) {
    if ($followers != $current_session["followers"] || 
        $platform != $current_session["platform"] || 
        $username != $current_session["username"]) {
        $session->update(
            ServerService::getIpAddress(), 
            $aff_sub4, 
            $username, 
            $platform, 
            $followers
        );
    }
    echo json_encode([
        "success" => true
    ]);
    exit;
}

// Create new session
$session->create(
    ServerService::getIpAddress(), 
    $aff_sub4, 
    $username, 
    $platform, 
    $followers
);

echo json_encode([
    "success" => true
]);