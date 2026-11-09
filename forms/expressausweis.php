<?php

/**
 * HK Energieberatung - Expressausweis Form Handler with Multi-File Attachments & SMTP
 */
ini_set('display_errors', 0);
error_reporting(E_ALL);

// === 1. CORS HEADERS (Allows GitHub Pages static site to submit to Uberspace) ===
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// === 2. LOAD CONFIGURATION + SHARED STORAGE/MAIL HELPERS ===
require __DIR__.'/lib/mailer.php';
$envConfig = hk_load_env();

// Helper to send JSON or Text response
function sendResponse($success, $message, $httpCode = 200)
{
    http_response_code($httpCode);
    if (! empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest' ||
        isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) {
        header('Content-Type: application/json; charset=UTF-8');
        echo json_encode(['success' => $success, 'message' => $message]);
    } else {
        header('Content-Type: text/plain; charset=UTF-8');
        echo $success ? 'OK' : $message;
    }
    exit;
}

// === 3. GET FORM DATA ===
$gebaeudetyp = trim($_POST['gebaeudetyp'] ?? '');
$wohneinheiten = trim($_POST['wohneinheiten'] ?? '');
$strasse = trim($_POST['strasse'] ?? '');
$plz = trim($_POST['plz'] ?? '');
$ort = trim($_POST['ort'] ?? '');
$baujahr = trim($_POST['baujahr'] ?? '');
$baujahr_heizung = trim($_POST['baujahr_heizung'] ?? 'unbekannt');
$wohnflaeche = trim($_POST['wohnflaeche'] ?? '');
$leerstand = trim($_POST['leerstand'] ?? 'nein');
$anlass = trim($_POST['anlass'] ?? '');

$wschv77 = trim($_POST['wschv77'] ?? '');
$fuenf_we = trim($_POST['fuenf_we'] ?? '');

$energietraeger = trim($_POST['energietraeger'] ?? '');
$warmwasser = trim($_POST['warmwasser'] ?? '');

$vorname = trim($_POST['vorname'] ?? '');
$nachname = trim($_POST['nachname'] ?? '');
$eigentuemer = trim($_POST['eigentuemer'] ?? '');
$email = trim($_POST['email'] ?? '');
$telefon = trim($_POST['telefon'] ?? '');
$rechnungsadresse = trim($_POST['rechnungsadresse'] ?? '');

$richtigkeit = trim($_POST['richtigkeit'] ?? '');
$datenschutz = trim($_POST['datenschutz'] ?? '');
$kontakt_ok = trim($_POST['kontakt_ok'] ?? 'nein');
$honeypot = $_POST['website'] ?? '';

// === 4. VALIDATION & SECURITY CHECKS ===

if (! empty($honeypot)) {
    sendResponse(false, 'Bot-Erkennung ausgelöst.', 400);
}

if (empty($strasse) || empty($plz) || empty($ort) || empty($baujahr) || empty($wohnflaeche) ||
    empty($vorname) || empty($nachname) || empty($email) || empty($telefon)) {
    sendResponse(false, 'Bitte füllen Sie alle erforderlichen Pflichtfelder aus.', 400);
}

if (empty($datenschutz) || empty($richtigkeit)) {
    sendResponse(false, 'Bitte bestätigen Sie die Richtigkeit der Angaben und die Datenschutzerklärung.', 400);
}

if (! filter_var($email, FILTER_VALIDATE_EMAIL)) {
    sendResponse(false, 'Bitte geben Sie eine gültige E-Mail-Adresse ein.', 400);
}

// === 4b. PREVENT DUPLICATE SUBMISSIONS (10-second lock) ===
$subHash = md5($email.'|'.$strasse.'|'.$plz.'|'.$ort);
$lockFile = sys_get_temp_dir().'/express_lock_'.$subHash.'.txt';

if (file_exists($lockFile) && (time() - filemtime($lockFile)) < 10) {
    sendResponse(true, 'Ihre Expressausweis-Anfrage wurde bereits erfolgreich empfangen.');
}
@file_put_contents($lockFile, (string) time());

// === 5. PROCESS FILE UPLOADS & ATTACHMENTS ===
$attachments = [];
$totalSize = 0;
$maxTotalSize = 40 * 1024 * 1024; // 40 MB max

$fileCategories = [
    'verbrauchsabrechnungen' => 'Verbrauchsabrechnungen (3 Jahre)',
    'warmwasser_nachweis' => 'Warmwassernachweis',
    'foto_aussenansicht' => 'Foto Außenansicht (Gebäude)',
    'foto_heizung' => 'Foto Heizungsanlage/Typenschild',
    'grundriss' => 'Grundriss / Baupläne',
    'eigentumsnachweis' => 'Eigentumsnachweis',
];

foreach ($fileCategories as $fieldName => $label) {
    if (isset($_FILES[$fieldName])) {
        $files = $_FILES[$fieldName];
        $count = is_array($files['name']) ? count($files['name']) : 1;

        for ($i = 0; $i < $count; $i++) {
            $name = is_array($files['name']) ? $files['name'][$i] : $files['name'];
            $tmpName = is_array($files['tmp_name']) ? $files['tmp_name'][$i] : $files['tmp_name'];
            $error = is_array($files['error']) ? $files['error'][$i] : $files['error'];
            $size = is_array($files['size']) ? $files['size'][$i] : $files['size'];
            $type = is_array($files['type']) ? $files['type'][$i] : $files['type'];

            if ($error === UPLOAD_ERR_OK && is_uploaded_file($tmpName)) {
                $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
                $allowed = ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'heic', 'tif', 'tiff', 'zip'];

                if (in_array($ext, $allowed) && $size <= 25 * 1024 * 1024 && ($totalSize + $size) <= $maxTotalSize) {
                    $totalSize += $size;
                    $content = file_get_contents($tmpName);
                    $attachments[] = [
                        'name' => $name,
                        'category' => $label,
                        'type' => $type ?: 'application/octet-stream',
                        'data' => $content,
                        'size' => $size,
                    ];
                }
            }
        }
    }
}

// === 6. SAVE THE ORDER (INCLUDING FILES) FIRST ===
$fullName = trim($vorname.' '.$nachname);
$adresse = $strasse.', '.$plz.' '.$ort;
$storedDir = hk_store_submission($envConfig, 'express', [
    'gebaeudetyp' => $gebaeudetyp, 'wohneinheiten' => $wohneinheiten, 'strasse' => $strasse, 'plz' => $plz, 'ort' => $ort,
    'baujahr' => $baujahr, 'baujahr_heizung' => $baujahr_heizung, 'wohnflaeche' => $wohnflaeche, 'leerstand' => $leerstand,
    'anlass' => $anlass, 'wschv77' => $wschv77, 'fuenf_we' => $fuenf_we, 'energietraeger' => $energietraeger,
    'warmwasser' => $warmwasser, 'vorname' => $vorname, 'nachname' => $nachname, 'eigentuemer' => $eigentuemer,
    'email' => $email, 'telefon' => $telefon, 'rechnungsadresse' => $rechnungsadresse, 'kontakt_ok' => $kontakt_ok,
], $attachments);

// === 7. NOTIFY BY EMAIL ===
$email_subject = '⚡ [Expressausweis 48h] '.$fullName.' – '.$adresse;
$recipient = $envConfig['MAIL_TO_ADDRESS'] ?? 'info@hk-energieberatung.de';
$nice = fn ($v) => ucfirst((string) $v);

$mail = [
    'kind' => 'Expressausweis 48h',
    'preheader' => 'Expressausweis (48h): '.$fullName.' | '.$adresse.' | '.$wohnflaeche.' m² ('.$gebaeudetyp.')',
    'title' => $fullName,
    'subtitle' => 'Verbrauchsausweis für '.$adresse,
    'email' => $email,
    'phone' => $telefon,
    'reply_subject' => 'Ihr Expressausweis für '.$adresse,
    'sections' => [
        ['Gebäude', [
            ['Gebäudetyp', $nice($gebaeudetyp)],
            ['Wohneinheiten', $wohneinheiten],
            ['Adresse', $adresse],
            ['Baujahr Gebäude', $baujahr],
            ['Baujahr Heizung', $baujahr_heizung],
            ['Wohn-/Nutzfläche', $wohnflaeche.' m²'],
            ['Leerstand', $nice($leerstand)],
            ['Anlass', $anlass],
        ]],
        ['Eignungsprüfung', [
            ['Ab 1977 gebaut / gedämmt', $nice($wschv77)],
            ['Mindestens 5 Wohneinheiten', $nice($fuenf_we)],
        ]],
        ['Heizung', [
            ['Hauptenergieträger', $nice($energietraeger)],
            ['Warmwasser', $nice($warmwasser)],
        ]],
        ['Auftraggeber', [
            ['Name', $fullName],
            ['Eigentümer', $nice($eigentuemer)],
            ['E-Mail', $email],
            ['Telefon', $telefon],
            ['Rechnungsadresse', $rechnungsadresse],
            ['Rückfragen erlaubt', $nice($kontakt_ok)],
        ]],
    ],
    'files' => array_map(fn ($a) => ['name' => $a['name'], 'category' => $a['category'], 'size' => $a['size']], $attachments),
    'reference' => $storedDir ? basename($storedDir) : '',
];

$result = hk_deliver($envConfig, $recipient, $email_subject, hk_render_email_text($mail), hk_render_email_html($mail), $email, $fullName, $attachments);
hk_mark_submission($storedDir, $result);

// === 8. RESPOND: success only when the order was saved or delivered ===
if ($result['sent'] || $storedDir !== null) {
    sendResponse(true, 'Vielen Dank! Ihre Express-Anfrage mit allen Dokumenten wurde erfolgreich übermittelt. Wir erstellen Ihren Energieausweis innerhalb von 48 Stunden.');
}

// Release the duplicate lock so an immediate retry is processed instead of answered with success
@unlink($lockFile);
sendResponse(false, 'Ihre Anfrage konnte leider nicht übermittelt werden. Bitte rufen Sie uns an: +49 162 6985115', 500);
