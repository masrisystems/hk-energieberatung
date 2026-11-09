<?php

/**
 * HK Energieberatung - Contact Form Backend Handler with SMTP, .env & CORS Support
 */
ini_set('display_errors', 0);
error_reporting(E_ALL);

// === CORS HEADERS (Allows GitHub Pages static site to submit to Uberspace/external PHP backend) ===
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// === 1. LOAD CONFIGURATION + SHARED STORAGE/MAIL HELPERS ===
require __DIR__.'/lib/mailer.php';
$envConfig = hk_load_env();

// === 2. GET FORM DATA ===
$name = trim($_POST['name'] ?? '');
$anrede = trim($_POST['anrede'] ?? '');
$email = trim($_POST['email'] ?? '');
$telefon = trim($_POST['telefon'] ?? trim($_POST['phone'] ?? ''));
$subject = trim($_POST['subject'] ?? trim($_POST['betreff'] ?? 'Allgemeine Anfrage'));
$message = trim($_POST['message'] ?? trim($_POST['nachricht'] ?? ''));
$privacy = trim($_POST['privacy'] ?? trim($_POST['datenschutz'] ?? ''));
$honeypot = $_POST['website'] ?? '';

// === 3. VALIDATION & SECURITY CHECKS ===

// Honeypot spam trap
if (! empty($honeypot)) {
    http_response_code(400);
    echo 'Bot-Erkennung ausgelöst.';
    exit;
}

// Detect Lead Magnet / Quick Download requests
$isLeadMagnet = (
    strpos($subject, 'Lead-Magnet') !== false ||
    strpos($subject, 'Download') !== false ||
    (! empty($email) && empty($name) && empty($message))
);

if ($isLeadMagnet) {
    if (empty($name)) {
        $name = 'Interessent (Lead-Magnet)';
    }
    if (empty($message)) {
        $message = 'Lead-Magnet Download-Anforderung für: '.$subject;
    }
    if (empty($privacy)) {
        $privacy = 'Akzeptiert (Lead-Magnet Opt-in)';
    }
}

// Check mandatory fields
if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo 'Bitte alle Pflichtfelder (Name, E-Mail, Nachricht) ausfüllen.';
    exit;
}

// Check privacy consent
if (empty($privacy)) {
    http_response_code(400);
    echo 'Bitte akzeptieren Sie die Datenschutzerklärung.';
    exit;
}

// Validate email format
if (! filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo 'Bitte geben Sie eine gültige E-Mail-Adresse ein.';
    exit;
}

// Prevent header injection attacks
if (preg_match("/[\r\n]/", $name) || preg_match("/[\r\n]/", $email)) {
    http_response_code(400);
    echo 'Ungültige Zeichen im Formular.';
    exit;
}

// === 3b. PREVENT DUPLICATE SUBMISSIONS (10-second lock) ===
$subHash = md5($name.'|'.$email.'|'.$message);
$lockFile = sys_get_temp_dir().'/contact_lock_'.$subHash.'.txt';

if (file_exists($lockFile) && (time() - filemtime($lockFile)) < 10) {
    http_response_code(200);
    echo 'OK';
    exit;
}
@file_put_contents($lockFile, (string) time());

// === 4. COMPOSE EMAIL MESSAGE ===
$anrede_str = (! empty($anrede) && $anrede !== 'keine Angabe') ? ($anrede.' ') : '';

if ($isLeadMagnet) {
    $cleanTopic = str_replace(['Lead-Magnet: ', 'Download: '], '', $subject);
    $email_subject = '📥 [Lead-Magnet: '.$cleanTopic.'] '.$email;
} else {
    $telStr = ! empty($telefon) ? ' (Tel: '.$telefon.')' : '';
    $email_subject = '📩 [Anfrage: '.$subject.'] '.$anrede_str.$name.$telStr;
}

// === 5. SAVE THE SUBMISSION FIRST, THEN NOTIFY BY EMAIL ===
$storedDir = hk_store_submission($envConfig, $isLeadMagnet ? 'download' : 'kontakt', [
    'anrede' => $anrede,
    'name' => $name,
    'email' => $email,
    'telefon' => $telefon,
    'subject' => $subject,
    'message' => $message,
    'ab_variant' => trim($_POST['ab_variant'] ?? ''),
]);

$recipient = $envConfig['MAIL_TO_ADDRESS'] ?? 'info@hk-energieberatung.de';

$mail = [
    'kind' => $isLeadMagnet ? 'Download-Anfrage' : 'Kontaktanfrage',
    'preheader' => 'Thema: '.$subject.' | '.$anrede_str.$name.' <'.$email.'>'.(! empty($telefon) ? ' | Tel: '.$telefon : ''),
    'title' => $isLeadMagnet ? $email : $anrede_str.$name,
    'subtitle' => $subject,
    'email' => $email,
    'phone' => $telefon,
    'reply_subject' => $isLeadMagnet ? 'Ihre Unterlagen von HK Energieberatung' : 'Ihre Anfrage: '.$subject,
    'message' => $isLeadMagnet ? '' : $message,
    'sections' => [
        ['Kontaktdaten', [
            ['Anrede', $anrede_str !== '' ? $anrede : ''],
            ['Name', $name],
            ['E-Mail', $email],
            ['Telefon', $telefon],
            ['Thema', $subject],
            ['Datenschutz', 'Zugestimmt'],
        ]],
    ],
    'reference' => $storedDir ? basename($storedDir) : '',
];

$result = hk_deliver($envConfig, $recipient, $email_subject, hk_render_email_text($mail), hk_render_email_html($mail), $email, $name);
hk_mark_submission($storedDir, $result);
$mailSent = $result['sent'];
$errorMessage = $result['error'];
// A saved submission is a captured lead even when the notification mail failed
$captured = $mailSent || $storedDir !== null;

// Handle direct GET visits in browser
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    http_response_code(200);
    echo '<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>HK Energieberatung – Formular-Endpunkt</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: "Roboto", sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }
    .card { background: #fff; max-width: 480px; width: 100%; border-radius: 16px; padding: 36px 28px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
    h1 { font-family: "Nunito", sans-serif; font-size: 1.5rem; color: #2d465e; margin: 16px 0 8px; }
    p { color: #64748b; font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px; }
    .btn { display: inline-block; background: #66A66D; color: #fff; font-weight: 600; text-decoration: none; padding: 12px 28px; border-radius: 50px; }
    .badge { display: inline-block; background: #e8f5e9; color: #2e7d32; font-size: 0.85rem; font-weight: 700; padding: 6px 14px; border-radius: 20px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">● Online & Betriebsbereit</div>
    <h1>HK Energieberatung Form API</h1>
    <p>Dieser Endpunkt verarbeitet Kontaktanfragen und Energieausweis-Formulare für <strong>hk-energieberatung.de</strong>.</p>
    <a href="https://hk-energieberatung.de" class="btn">Zurück zur Website</a>
  </div>
</body>
</html>';
    exit;
}

// === 7. CLIENT RESPONSE ===
$isAjax = (! empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest') ||
          (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false);

if ($captured) {
    http_response_code(200);
    if ($isAjax) {
        echo 'OK';
    } else {
        $msgTitle = $isLeadMagnet ? 'Vielen Dank!' : 'Vielen Dank für Ihre Nachricht!';
        $msgDesc = $isLeadMagnet
            ? 'Ihre E-Mail-Adresse wurde erfolgreich erfasst. Wir übermitteln Ihnen die angeforderten Unterlagen in Kürze per E-Mail.'
            : 'Ihre Anfrage wurde erfolgreich an unser Ingenieurbüro übermittelt. Wir werden uns schnellstmöglich bei Ihnen melden.';
        echo '<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>'.htmlspecialchars($msgTitle).' – HK Energieberatung</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: "Roboto", sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }
    .card { background: #fff; max-width: 500px; width: 100%; border-radius: 16px; padding: 40px 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
    .check { width: 64px; height: 64px; background: #e8f5e9; color: #2e7d32; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 2rem; margin-bottom: 16px; }
    h1 { font-family: "Nunito", sans-serif; font-size: 1.5rem; color: #2d465e; margin-bottom: 8px; }
    p { color: #64748b; font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px; }
    .btn { display: inline-block; background: #66A66D; color: #fff; font-weight: 600; text-decoration: none; padding: 12px 30px; border-radius: 50px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="check">✓</div>
    <h1>'.htmlspecialchars($msgTitle).'</h1>
    <p>'.htmlspecialchars($msgDesc).'</p>
    <a href="https://hk-energieberatung.de" class="btn">Zurück zur Website</a>
  </div>
</body>
</html>';
    }
} else {
    // Never report success for an undelivered enquiry: the visitor must know, and no conversion may fire.
    // Release the duplicate lock so an immediate retry is actually sent instead of answered with OK.
    @unlink($lockFile);
    if (! empty($errorMessage)) {
        error_log('contact.php mail failure: '.$errorMessage);
    }
    http_response_code(500);
    echo 'Ihre Nachricht konnte leider nicht gesendet werden. Bitte rufen Sie uns an: +49 162 6985115';
}
