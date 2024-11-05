<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

require_once "../services/OffersService.php";
require_once "../services/ValidationService.php";
require_once "../services/DotEnvService.php";

(new DotEnvService(__DIR__ . "/../.env"))->load();

$api_key = getenv("OFFERS_API_KEY");
if (!$api_key) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "error" => "API key not configured"
    ]);
    exit;
}

$aff_sub4 = ValidationService::affSub4();
$offers_limit = (int)getenv("OFFERS_LIMIT");
$offers_service = new OffersService($api_key, $aff_sub4);

try {
    $offers = $offers_service->get();
    
    if (!$offers) {
        throw new Exception("No offers available");
    }

    // Process and sanitize offers
    $processed_offers = array_map(function($offer) {
        return [
            'id' => (int)$offer['id'],
            'name' => htmlspecialchars($offer['name']),
            'description' => htmlspecialchars($offer['description']),
            'type' => htmlspecialchars($offer['type']),
            'payout' => htmlspecialchars($offer['payout']),
            'url' => filter_var($offer['url'], FILTER_SANITIZE_URL),
            'icon' => filter_var($offer['icon'], FILTER_SANITIZE_URL)
        ];
    }, $offers);

    // Limit the offers based on OFFERS_LIMIT
    if ($offers_limit > 0) {
        $processed_offers = array_slice($processed_offers, 0, $offers_limit);
    }

    echo json_encode([
        "success" => true,
        "data" => $processed_offers
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "error" => "Failed to fetch offers: " . $e->getMessage()
    ]);
    exit;
}