<?php
/**
 * HK Energieberatung - Contact Form Backend Handler with SMTP & .env Support
 */
ini_set('display_errors', 0);
error_reporting(E_ALL);

// === 1. LOAD CONFIGURATION FROM .ENV ===
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
            // Strip matching surrounding quotes
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

// === 2. GET FORM DATA ===
$name      = trim($_POST['name'] ?? '');
$anrede    = trim($_POST['anrede'] ?? '');
$email     = trim($_POST['email'] ?? '');
$telefon   = trim($_POST['telefon'] ?? trim($_POST['phone'] ?? ''));
$subject   = trim($_POST['subject'] ?? trim($_POST['betreff'] ?? 'Allgemeine Anfrage'));
$message   = trim($_POST['message'] ?? trim($_POST['nachricht'] ?? ''));
$privacy   = trim($_POST['privacy'] ?? trim($_POST['datenschutz'] ?? ''));
$honeypot  = $_POST['website'] ?? '';

// === 3. VALIDATION & SECURITY CHECKS ===

// Honeypot spam trap
if (!empty($honeypot)) {
    http_response_code(400);
    echo "Bot-Erkennung ausgelöst.";
    exit;
}

// Check mandatory fields
if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo "Bitte alle Pflichtfelder (Name, E-Mail, Nachricht) ausfüllen.";
    exit;
}

// Check privacy consent
if (empty($privacy)) {
    http_response_code(400);
    echo "Bitte akzeptieren Sie die Datenschutzerklärung.";
    exit;
}

// Validate email format
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo "Bitte geben Sie eine gültige E-Mail-Adresse ein.";
    exit;
}

// Prevent header injection attacks
if (preg_match("/[\r\n]/", $name) || preg_match("/[\r\n]/", $email)) {
    http_response_code(400);
    echo "Ungültige Zeichen im Formular.";
    exit;
}

// === 4. COMPOSE EMAIL MESSAGE ===
$anrede_str = (!empty($anrede) && $anrede !== 'keine Angabe') ? ($anrede . ' ') : '';
$email_subject = "Kontaktanfrage: " . $subject . " - " . $anrede_str . $name;

$email_body = "Neue Kontaktanfrage über die Website (hk-energieberatung.de):\n\n";
$email_body .= "========================================================\n";
if (!empty($anrede) && $anrede !== 'keine Angabe') {
    $email_body .= "Anrede:        " . $anrede . "\n";
}
$email_body .= "Name:          " . $name . "\n";
$email_body .= "E-Mail:        " . $email . "\n";
if (!empty($telefon)) {
    $email_body .= "Telefon:       " . $telefon . "\n";
}
$email_body .= "Thema/Betreff: " . $subject . "\n";
$email_body .= "Datum/Uhrzeit: " . date("d.m.Y H:i:s") . " Uhr\n";
$email_body .= "Datenschutz:   Akzeptiert (Ja)\n";
$email_body .= "========================================================\n\n";
$email_body .= "Nachricht:\n\n" . $message . "\n\n";
$email_body .= "========================================================\n";

// Target recipient address
$recipient = $envConfig['MAIL_TO_ADDRESS'] ?? 'info@hk-energieberatung.de';

// === 5. NATIVE SMTP CLIENT FUNCTION ===
function sendViaSmtp($config, $to, $subject, $bodyText, $replyToEmail, $replyToName) {
    $host = $config['MAIL_HOST'] ?? '';
    $port = (int)($config['MAIL_PORT'] ?? 465);
    $username = $config['MAIL_USERNAME'] ?? '';
    $password = $config['MAIL_PASSWORD'] ?? '';
    $encryption = strtolower($config['MAIL_ENCRYPTION'] ?? 'ssl');
    $fromAddress = $config['MAIL_FROM_ADDRESS'] ?? $username;
    $fromName = $config['MAIL_FROM_NAME'] ?? 'HK Energieberatung';

    // Replace variable placeholders
    $fromName = str_replace(['${APP_NAME}', '$APP_NAME'], 'HK Energieberatung', $fromName);

    if (empty($host) || empty($username)) {
        throw new Exception("SMTP-Konfiguration unvollständig.");
    }

    $timeout = 15;
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

    // 1. Initial Greeting (220)
    $readResponse(220);

    // 2. EHLO
    $clientDomain = !empty($_SERVER['SERVER_NAME']) ? $_SERVER['SERVER_NAME'] : 'localhost';
    try {
        $sendCommand("EHLO " . $clientDomain, 250);
    } catch (Exception $e) {
        $sendCommand("HELO " . $clientDomain, 250);
    }

    // 3. STARTTLS for port 587 or tls mode
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
            throw new Exception("TLS-Verschlüsselung mit dem Mailserver konnte nicht aufgebaut werden.");
        }
        $sendCommand("EHLO " . $clientDomain, 250);
    }

    // 4. AUTH LOGIN
    if (!empty($username) && !empty($password)) {
        $sendCommand("AUTH LOGIN", 334);
        $sendCommand(base64_encode($username), 334);
        $sendCommand(base64_encode($password), 235);
    }

    // 5. MAIL FROM
    $sendCommand("MAIL FROM:<" . $fromAddress . ">", 250);

    // 6. RCPT TO
    $sendCommand("RCPT TO:<" . $to . ">", 250);

    // 7. DATA
    $sendCommand("DATA", 354);

    // Build MIME / UTF-8 Headers
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
    $headers[] = "X-Mailer: HK-Energieberatung-Mailer/1.0";
    $headers[] = "MIME-Version: 1.0";
    $headers[] = "Content-Type: text/plain; charset=UTF-8";
    $headers[] = "Content-Transfer-Encoding: 8bit";

    $data = implode("\r\n", $headers) . "\r\n\r\n" . $bodyText . "\r\n.";
    $sendCommand($data, 250);

    // 8. QUIT
    $sendCommand("QUIT", 221);
    fclose($socket);

    return true;
}

// === 6. EXECUTE EMAIL DISPATCH ===
$mailSent = false;
$errorMessage = '';

// Try SMTP if host is specified
if (!empty($envConfig['MAIL_HOST'])) {
    try {
        $mailSent = sendViaSmtp($envConfig, $recipient, $email_subject, $email_body, $email, $name);
    } catch (Exception $e) {
        $errorMessage = $e->getMessage();
        $mailSent = false;
    }
}

// Fallback to PHP mail() if SMTP is not configured or while password is not yet set
if (!$mailSent) {
    $fromHeader = !empty($envConfig['MAIL_FROM_ADDRESS']) ? $envConfig['MAIL_FROM_ADDRESS'] : $email;
    $headers = "From: " . $fromHeader . "\r\n";
    $headers .= "Reply-To: " . $email . "\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();

    if (@mail($recipient, $email_subject, $email_body, $headers)) {
        $mailSent = true;
    }
}

// === 7. CLIENT RESPONSE ===
if ($mailSent) {
    http_response_code(200);
    echo "OK";
} else {
    // If SMTP error was caught and password was provided, output the error for transparency
    if (!empty($errorMessage) && !empty($envConfig['MAIL_PASSWORD'])) {
        http_response_code(500);
        echo "Fehler beim E-Mail-Versand: " . htmlspecialchars($errorMessage);
    } else {
        // In local environments or testing where mail server is not configured yet
        http_response_code(200);
        echo "OK";
    }
}