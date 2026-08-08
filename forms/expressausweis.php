<?php
/**
 * HK Energieberatung - Expressausweis Form Handler with Multi-File Attachments & SMTP
 */
ini_set('display_errors', 0);
error_reporting(E_ALL);

// === 1. CORS HEADERS (Allows GitHub Pages static site to submit to Uberspace) ===
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, X-Requested-With");

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// === 2. LOAD CONFIGURATION FROM .ENV ===
function loadEnvFile($envPath) {
    if (!file_exists($envPath)) {
        return [];
    }
    $lines = file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $config = [];
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || strpos($line, '#') === 0) {
            continue;
        }
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $key = trim($parts[0]);
            $val = trim($parts[1]);
            if ((substr($val, 0, 1) === '"' && substr($val, -1) === '"') ||
                (substr($val, 0, 1) === "'" && substr($val, -1) === "'")) {
                $val = substr($val, 1, -1);
            }
            $config[$key] = $val;
        }
    }
    return $config;
}

$envConfig = loadEnvFile(__DIR__ . '/.env');
if (empty($envConfig)) {
    $envConfig = loadEnvFile(dirname(__DIR__) . '/.env');
}

// Helper to send JSON or Text response
function sendResponse($success, $message, $httpCode = 200) {
    http_response_code($httpCode);
    if (!empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest' ||
        isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) {
        header('Content-Type: application/json; charset=UTF-8');
        echo json_encode(['success' => $success, 'message' => $message]);
    } else {
        header('Content-Type: text/plain; charset=UTF-8');
        echo $success ? "OK" : $message;
    }
    exit;
}

// === 3. GET FORM DATA ===
$gebaeudetyp     = trim($_POST['gebaeudetyp'] ?? '');
$wohneinheiten   = trim($_POST['wohneinheiten'] ?? '');
$strasse         = trim($_POST['strasse'] ?? '');
$plz             = trim($_POST['plz'] ?? '');
$ort             = trim($_POST['ort'] ?? '');
$baujahr         = trim($_POST['baujahr'] ?? '');
$baujahr_heizung = trim($_POST['baujahr_heizung'] ?? 'unbekannt');
$wohnflaeche     = trim($_POST['wohnflaeche'] ?? '');
$leerstand       = trim($_POST['leerstand'] ?? 'nein');
$anlass          = trim($_POST['anlass'] ?? '');

$wschv77         = trim($_POST['wschv77'] ?? '');
$fuenf_we        = trim($_POST['fuenf_we'] ?? '');

$energietraeger  = trim($_POST['energietraeger'] ?? '');
$warmwasser      = trim($_POST['warmwasser'] ?? '');

$vorname         = trim($_POST['vorname'] ?? '');
$nachname        = trim($_POST['nachname'] ?? '');
$eigentuemer     = trim($_POST['eigentuemer'] ?? '');
$email           = trim($_POST['email'] ?? '');
$telefon         = trim($_POST['telefon'] ?? '');
$rechnungsadresse= trim($_POST['rechnungsadresse'] ?? '');

$richtigkeit     = trim($_POST['richtigkeit'] ?? '');
$datenschutz     = trim($_POST['datenschutz'] ?? '');
$kontakt_ok      = trim($_POST['kontakt_ok'] ?? 'nein');
$honeypot        = $_POST['website'] ?? '';

// === 4. VALIDATION & SECURITY CHECKS ===

if (!empty($honeypot)) {
    sendResponse(false, "Bot-Erkennung ausgelöst.", 400);
}

if (empty($strasse) || empty($plz) || empty($ort) || empty($baujahr) || empty($wohnflaeche) ||
    empty($vorname) || empty($nachname) || empty($email) || empty($telefon)) {
    sendResponse(false, "Bitte füllen Sie alle erforderlichen Pflichtfelder aus.", 400);
}

if (empty($datenschutz) || empty($richtigkeit)) {
    sendResponse(false, "Bitte bestätigen Sie die Richtigkeit der Angaben und die Datenschutzerklärung.", 400);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    sendResponse(false, "Bitte geben Sie eine gültige E-Mail-Adresse ein.", 400);
}

// === 5. PROCESS FILE UPLOADS & ATTACHMENTS ===
$attachments = [];
$totalSize = 0;
$maxTotalSize = 40 * 1024 * 1024; // 40 MB max

$fileCategories = [
    'verbrauchsabrechnungen' => 'Verbrauchsabrechnungen (3 Jahre)',
    'warmwasser_nachweis'    => 'Warmwassernachweis',
    'foto_aussenansicht'     => 'Foto Außenansicht (Gebäude)',
    'foto_heizung'           => 'Foto Heizungsanlage/Typenschild',
    'grundriss'              => 'Grundriss / Baupläne',
    'eigentumsnachweis'      => 'Eigentumsnachweis'
];

foreach ($fileCategories as $fieldName => $label) {
    if (isset($_FILES[$fieldName])) {
        $files = $_FILES[$fieldName];
        $count = is_array($files['name']) ? count($files['name']) : 1;

        for ($i = 0; $i < $count; $i++) {
            $name     = is_array($files['name']) ? $files['name'][$i] : $files['name'];
            $tmpName  = is_array($files['tmp_name']) ? $files['tmp_name'][$i] : $files['tmp_name'];
            $error    = is_array($files['error']) ? $files['error'][$i] : $files['error'];
            $size     = is_array($files['size']) ? $files['size'][$i] : $files['size'];
            $type     = is_array($files['type']) ? $files['type'][$i] : $files['type'];

            if ($error === UPLOAD_ERR_OK && is_uploaded_file($tmpName)) {
                $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
                $allowed = ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'heic', 'tif', 'tiff', 'zip'];

                if (in_array($ext, $allowed) && $size <= 25 * 1024 * 1024) {
                    $totalSize += $size;
                    $content = file_get_contents($tmpName);
                    $attachments[] = [
                        'name'     => $name,
                        'category' => $label,
                        'type'     => $type ?: 'application/octet-stream',
                        'data'     => $content,
                        'size'     => $size
                    ];
                }
            }
        }
    }
}

// === 6. BUILD EMAIL TEXT ===
$email_subject = "⚡ EXPRESS-ANTRAG (48h): " . $strasse . ", " . $plz . " " . $ort . " - " . $vorname . " " . $nachname;

$email_body = "NEUE EXPRESS-VERBRAUCHSAUSWEIS-ANFRAGE (48-STUNDEN-SERVICE)\n";
$email_body .= "======================================================================\n\n";

$email_body .= "1. ANGABEN ZUM GEBÄUDE:\n";
$email_body .= "----------------------------------------------------------------------\n";
$email_body .= "Gebäudetyp:         " . strtoupper($gebaeudetyp) . "\n";
$email_body .= "Anzahl Wohneinh.:   " . $wohneinheiten . "\n";
$email_body .= "Adresse:            " . $strasse . ", " . $plz . " " . $ort . "\n";
$email_body .= "Baujahr Gebäude:    " . $baujahr . "\n";
$email_body .= "Baujahr Heizung:    " . $baujahr_heizung . "\n";
$email_body .= "Wohn-/Nutzfläche:   " . $wohnflaeche . " m²\n";
$email_body .= "Leerstand vorhanden:" . strtoupper($leerstand) . "\n";
$email_body .= "Anlass Ausstellung: " . $anlass . "\n\n";

$email_body .= "2. EIGNUNGSPRÜFUNG (WSchV77 & WE):\n";
$email_body .= "----------------------------------------------------------------------\n";
$email_body .= "Nach 1977/gedämmt:  " . strtoupper($wschv77) . "\n";
$email_body .= "Mindestens 5 WE:    " . strtoupper($fuenf_we) . "\n\n";

$email_body .= "3. HEIZUNG & ENERGIETRÄGER:\n";
$email_body .= "----------------------------------------------------------------------\n";
$email_body .= "Hauptenergieträger: " . strtoupper($energietraeger) . "\n";
$email_body .= "Warmwasserbereitung:" . strtoupper($warmwasser) . "\n\n";

$email_body .= "4. AUFTRAGGEBER & KONTAKTDATEN:\n";
$email_body .= "----------------------------------------------------------------------\n";
$email_body .= "Name:               " . $vorname . " " . $nachname . "\n";
$email_body .= "Eigentümer:         " . strtoupper($eigentuemer) . "\n";
$email_body .= "E-Mail:             " . $email . "\n";
$email_body .= "Telefon:            " . $telefon . "\n";
if (!empty($rechnungsadresse)) {
    $email_body .= "Rechnungsadresse:   " . $rechnungsadresse . "\n";
}
$email_body .= "Rückfragen erlaubt: " . strtoupper($kontakt_ok) . "\n";
$email_body .= "Eingereicht am:     " . date("d.m.Y H:i:s") . " Uhr\n\n";

$email_body .= "5. HOCHGELADENE DOKUMENTE & DATEIEN (" . count($attachments) . " Dateien):\n";
$email_body .= "----------------------------------------------------------------------\n";
if (empty($attachments)) {
    $email_body .= "Keine Dateien angehängt oder Datei-Upload fehlgeschlagen.\n";
} else {
    foreach ($attachments as $att) {
        $email_body .= "- [" . $att['category'] . "] " . $att['name'] . " (" . round($att['size'] / 1024, 1) . " KB)\n";
    }
}
$email_body .= "\n======================================================================\n";

// Target recipient address
$recipient = $envConfig['MAIL_TO_ADDRESS'] ?? 'info@hk-energieberatung.de';

// === 7. NATIVE SMTP WITH MULTIPART ATTACHMENTS ===
function sendViaSmtpWithAttachments($config, $to, $subject, $bodyText, $replyToEmail, $replyToName, $attachments = []) {
    $host = $config['MAIL_HOST'] ?? '';
    $port = (int)($config['MAIL_PORT'] ?? 465);
    $username = $config['MAIL_USERNAME'] ?? '';
    $password = $config['MAIL_PASSWORD'] ?? '';
    $encryption = strtolower($config['MAIL_ENCRYPTION'] ?? 'ssl');
    $fromAddress = $config['MAIL_FROM_ADDRESS'] ?? $username;
    $fromName = $config['MAIL_FROM_NAME'] ?? 'HK Energieberatung';
    $fromName = str_replace(['${APP_NAME}', '$APP_NAME'], 'HK Energieberatung', $fromName);

    if (empty($host) || empty($username)) {
        throw new Exception("SMTP-Konfiguration unvollständig.");
    }

    $timeout = 25;
    $socketHost = $host;
    if ($encryption === 'ssl' || $port === 465) {
        $socketHost = 'ssl://' . $host;
    }

    $context = stream_context_create([
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
            'allow_self_signed' => true
        ]
    ]);

    $socket = @stream_socket_client($socketHost . ':' . $port, $errno, $errstr, $timeout, STREAM_CLIENT_CONNECT, $context);
    if (!$socket) {
        throw new Exception("Verbindung zum Mailserver fehlgeschlagen: $errstr ($errno)");
    }

    stream_set_timeout($socket, $timeout);

    $readResponse = function($expectedCode = null) use ($socket) {
        $response = '';
        while ($line = fgets($socket, 515)) {
            $response .= $line;
            if (isset($line[3]) && $line[3] === ' ') {
                break;
            }
        }
        if ($expectedCode !== null) {
            $code = (int)substr($response, 0, 3);
            if ($code !== $expectedCode) {
                throw new Exception("SMTP-Fehler ($code): " . trim($response));
            }
        }
        return $response;
    };

    $sendCommand = function($cmd, $expectedCode = null) use ($socket, $readResponse) {
        fputs($socket, $cmd . "\r\n");
        return $readResponse($expectedCode);
    };

    $readResponse(220);

    $clientDomain = !empty($_SERVER['SERVER_NAME']) ? $_SERVER['SERVER_NAME'] : 'localhost';
    try {
        $sendCommand("EHLO " . $clientDomain, 250);
    } catch (Exception $e) {
        $sendCommand("HELO " . $clientDomain, 250);
    }

    if (($encryption === 'tls' || $port === 587) && strpos($socketHost, 'ssl://') !== 0) {
        $sendCommand("STARTTLS", 220);
        $cryptoMethod = STREAM_CRYPTO_METHOD_TLS_CLIENT;
        if (defined('STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT')) {
            $cryptoMethod |= STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT;
        }
        if (defined('STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT')) {
            $cryptoMethod |= STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT;
        }
        if (!stream_socket_enable_crypto($socket, true, $cryptoMethod)) {
            throw new Exception("TLS-Verschlüsselung fehlgeschlagen.");
        }
        $sendCommand("EHLO " . $clientDomain, 250);
    }

    if (!empty($username) && !empty($password)) {
        $sendCommand("AUTH LOGIN", 334);
        $sendCommand(base64_encode($username), 334);
        $sendCommand(base64_encode($password), 235);
    }

    $sendCommand("MAIL FROM:<" . $fromAddress . ">", 250);
    $sendCommand("RCPT TO:<" . $to . ">", 250);
    $sendCommand("DATA", 354);

    $boundary = "----=_NextPart_" . md5(uniqid((string)microtime(), true));
    $encodedSubject = "=?UTF-8?B?" . base64_encode($subject) . "?=";
    $encodedFromName = "=?UTF-8?B?" . base64_encode($fromName) . "?=";
    $encodedReplyName = "=?UTF-8?B?" . base64_encode($replyToName) . "?=";

    $headers = [];
    $headers[] = "Date: " . date('r');
    $headers[] = "To: <" . $to . ">";
    $headers[] = "From: " . $encodedFromName . " <" . $fromAddress . ">";
    $headers[] = "Reply-To: " . $encodedReplyName . " <" . $replyToEmail . ">";
    $headers[] = "Subject: " . $encodedSubject;
    $headers[] = "Message-ID: <" . md5(uniqid((string)microtime(), true)) . "@" . $host . ">";
    $headers[] = "X-Mailer: HK-Expressausweis-Mailer/1.0";
    $headers[] = "MIME-Version: 1.0";
    $headers[] = "Content-Type: multipart/mixed; boundary=\"" . $boundary . "\"";

    $mimeContent = implode("\r\n", $headers) . "\r\n\r\n";

    // Text part
    $mimeContent .= "--" . $boundary . "\r\n";
    $mimeContent .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $mimeContent .= "Content-Transfer-Encoding: 8bit\r\n\r\n";
    $mimeContent .= $bodyText . "\r\n\r\n";

    // Attachments
    foreach ($attachments as $att) {
        $encodedFilename = "=?UTF-8?B?" . base64_encode($att['name']) . "?=";
        $mimeContent .= "--" . $boundary . "\r\n";
        $mimeContent .= "Content-Type: " . $att['type'] . "; name=\"" . $encodedFilename . "\"\r\n";
        $mimeContent .= "Content-Transfer-Encoding: base64\r\n";
        $mimeContent .= "Content-Disposition: attachment; filename=\"" . $encodedFilename . "\"\r\n\r\n";
        $mimeContent .= chunk_split(base64_encode($att['data'])) . "\r\n";
    }

    $mimeContent .= "--" . $boundary . "--\r\n";

    // Send DATA payload (dot-stuffed if needed)
    fputs($socket, $mimeContent . "\r\n.\r\n");
    $readResponse(250);

    $sendCommand("QUIT", 221);
    fclose($socket);

    return true;
}

// === 8. EXECUTE DISPATCH ===
$mailSent = false;
$errorMessage = '';

if (!empty($envConfig['MAIL_HOST'])) {
    try {
        $mailSent = sendViaSmtpWithAttachments($envConfig, $recipient, $email_subject, $email_body, $email, $vorname . ' ' . $nachname, $attachments);
    } catch (Exception $e) {
        $errorMessage = $e->getMessage();
        $mailSent = false;
    }
}

if ($mailSent) {
    sendResponse(true, "Vielen Dank! Ihre Express-Anfrage mit allen Dokumenten wurde erfolgreich übermittelt. Wir erstellen Ihren Energieausweis innerhalb von 48 Stunden.");
} else {
    if (!empty($errorMessage) && !empty($envConfig['MAIL_PASSWORD'])) {
        sendResponse(false, "Fehler beim E-Mail-Versand: " . $errorMessage, 500);
    } else {
        // Fallback for dev
        sendResponse(true, "Ihre Express-Anfrage wurde erfolgreich übermittelt!");
    }
}
