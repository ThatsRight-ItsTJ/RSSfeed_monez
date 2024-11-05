<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

require_once "../services/ServerService.php";
require_once "../services/ValidationService.php";
require_once "../services/ConversionService.php";
require_once "../services/DotEnvService.php";
require_once "../database/Session.php";
require_once "../database/Click.php";

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

// Get the current session
$session = new Session();
$current_session = $session->get(ServerService::getIpAddress(), $aff_sub4);
if (!$current_session) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "The current session doesn't exist"
    ]);
    exit;
}

$conversions_required = ConversionService::followersToConversions($current_session["followers"]);

$click = new Click();
$clicks = $click->getAll($current_session["id"]);

// Check if required number of offers are completed
if (count($clicks) >= $conversions_required) {
    echo json_encode([
        "success" => true
    ]);
    exit;
}

echo json_encode([
    "success" => false
]);