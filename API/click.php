<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

require_once "../services/ServerService.php";
require_once "../services/ValidationService.php";
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

$session = new Session();
$current_session = $session->get(ServerService::getIpAddress(), $aff_sub4);

if (!$current_session) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "Failed to get the current session"
    ]);
    exit;
}

if (!isset($_GET["offer_id"]) || !isset($_GET["link"])) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "Missing required parameters"
    ]);
    exit;
}

$click = new Click();
$click->create((int)$_GET["offer_id"], $current_session["id"]);

echo json_encode([
    "success" => true,
    "redirect_url" => urldecode($_GET["link"])
]);