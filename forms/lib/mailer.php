<?php

/**
 * Shared helpers for the HK Energieberatung form handlers (contact.php, expressausweis.php):
 * configuration, durable storage of every submission, notification email rendering and delivery.
 *
 * Every submission is written to disk BEFORE any mail is attempted, so a delivery failure can never lose a lead.
 */

date_default_timezone_set('Europe/Berlin');

// === CONFIGURATION ===

function hk_parse_env_file($envPath)
{
    if (! is_file($envPath)) {
        return [];
    }
    $config = [];
    foreach (file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $line = trim($line);
        if ($line === '' || strpos($line, '#') === 0) {
            continue;
        }
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $val = trim($parts[1]);
            if (strlen($val) >= 2 && ($val[0] === '"' || $val[0] === "'") && substr($val, -1) === $val[0]) {
                $val = substr($val, 1, -1);
            }
            $config[trim($parts[0])] = $val;
        }
    }

    return $config;
}

function hk_load_env()
{
    // Production: secrets live outside the web root (Uberspace: /var/www/virtual/<user>/hk-energieberatung.env)
    $config = hk_parse_env_file(dirname(__DIR__, 3).'/hk-energieberatung.env');

    // Local development fallback
    return $config ?: hk_parse_env_file(dirname(__DIR__).'/.env');
}

// === DURABLE STORAGE ===

function hk_submissions_root(array $config)
{
    // Outside the web root by default: /var/www/virtual/<user>/hk-submissions
    return rtrim($config['SUBMISSIONS_DIR'] ?? dirname(__DIR__, 3).'/hk-submissions', '/\\');
}

/**
 * Saves the submission (fields + uploaded files) and returns its folder, or null if nothing could be written.
 */
function hk_store_submission(array $config, $type, array $fields, array $attachments = [])
{
    $root = hk_submissions_root($config);
    $dir = $root.'/'.date('Y-m').'/'.date('Ymd-His').'_'.$type.'_'.bin2hex(random_bytes(3));

    if (! @mkdir($dir, 0700, true)) {
        error_log('hk forms: could not create submission folder '.$dir);

        return null;
    }
    @chmod($root, 0700);

    $files = [];
    foreach ($attachments as $i => $att) {
        $storedAs = sprintf('%02d_', $i + 1).preg_replace('/[^A-Za-z0-9._-]+/', '_', $att['name']);
        $ok = @file_put_contents($dir.'/'.$storedAs, $att['data']) !== false;
        if ($ok) {
            @chmod($dir.'/'.$storedAs, 0600);
        }
        $files[] = ['name' => $att['name'], 'category' => $att['category'] ?? '', 'size' => $att['size'] ?? strlen($att['data']), 'stored_as' => $ok ? $storedAs : null];
    }

    $record = [
        'type' => $type,
        'received_at' => date('c'),
        'page' => $_SERVER['HTTP_REFERER'] ?? '',
        'fields' => $fields,
        'files' => $files,
        'mail' => ['status' => 'pending'],
    ];

    $json = json_encode($record, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    if ($json === false || ! @file_put_contents($dir.'/submission.json', $json)) {
        error_log('hk forms: could not write '.$dir.'/submission.json');

        return null;
    }
    @chmod($dir.'/submission.json', 0600);

    return $dir;
}

function hk_mark_submission($dir, array $mailResult)
{
    if (! $dir || ! is_file($dir.'/submission.json')) {
        return;
    }
    $record = json_decode((string) file_get_contents($dir.'/submission.json'), true) ?: [];
    $record['mail'] = [
        'status' => $mailResult['sent'] ? 'sent' : 'failed',
        'via' => $mailResult['via'],
        'error' => $mailResult['error'],
        'at' => date('c'),
    ];
    @file_put_contents($dir.'/submission.json', json_encode($record, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE));
}

// === EMAIL RENDERING ===

function hk_e($value)
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}

function hk_format_size($bytes)
{
    return $bytes >= 1048576 ? number_format($bytes / 1048576, 1, ',', '.').' MB' : max(1, round($bytes / 1024)).' KB';
}

function hk_received_label()
{
    $days = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];

    return $days[(int) date('w')].', '.date('d.m.Y').' um '.date('H:i').' Uhr';
}

/**
 * Notification email for staff. $s keys:
 *   kind, preheader, title, subtitle, email, phone, reply_subject,
 *   message (optional), sections [[title, [[label, value], ...]], ...], files [[name, category, size]], reference
 */
function hk_render_email_html(array $s)
{
    $navy = '#2d465e';
    $ink = '#1f2d3a';
    $muted = '#5a6878';
    $line = '#e3ece7';
    // Website palette (assets/css/main.css): brand green, mint accent, navy headings
    $green = '#66A66D';
    $mint = '#ABD8C3';
    $mintTint = '#edf7f2';
    $page = '#f3f7f5';
    $sans = "font-family:Roboto,'Segoe UI',Helvetica,Arial,sans-serif;";
    $display = "font-family:Nunito,'Segoe UI',Helvetica,Arial,sans-serif;";

    $phoneHref = preg_replace('/[^0-9+]/', '', (string) ($s['phone'] ?? ''));
    $mailHref = 'mailto:'.rawurlencode($s['email']).'?subject='.rawurlencode($s['reply_subject'] ?? 'Ihre Anfrage bei HK Energieberatung');

    $button = function ($href, $label, $primary) use ($sans, $green, $navy) {
        $style = $primary
            ? 'background:'.$green.';color:#ffffff;border:2px solid '.$green.';'
            : 'background:#ffffff;color:'.$navy.';border:2px solid '.$green.';';

        // Inline-block (not table cells) so the buttons wrap onto a new line on narrow phones
        return '<a href="'.hk_e($href).'" style="'.$style.$sans.'display:inline-block;margin:0 8px 8px 0;font-size:16px;font-weight:700;line-height:20px;text-decoration:none;padding:11px 24px;border-radius:50px;">'.hk_e($label).'</a>';
    };

    $html = '<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>'.hk_e($s['title']).'</title></head>';
    $html .= '<body style="margin:0;padding:0;background:'.$page.';">';
    $html .= '<div style="display:none;max-height:0;overflow:hidden;opacity:0;">'.hk_e($s['preheader']).'</div>';
    $html .= '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:'.$page.';"><tr><td align="center" style="padding:24px 8px;">';
    $html .= '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;">';

    // Header bar
    $html .= '<tr><td style="background:'.$navy.';border-bottom:4px solid '.$green.';padding:16px 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>';
    $html .= '<td style="'.$display.'color:#ffffff;font-size:15px;font-weight:700;">HK Energieberatung</td>';
    $html .= '<td align="right" style="'.$sans.'color:'.$mint.';font-size:13px;font-weight:700;">'.hk_e($s['kind']).'</td>';
    $html .= '</tr></table></td></tr>';

    // Who, what, when + actions
    $html .= '<tr><td style="padding:28px 28px 12px;">';
    $html .= '<h1 style="'.$display.'margin:0 0 6px;color:'.$navy.';font-size:24px;line-height:30px;font-weight:800;">'.hk_e($s['title']).'</h1>';
    $html .= '<p style="'.$sans.'margin:0 0 4px;color:'.$ink.';font-size:16px;line-height:24px;">'.hk_e($s['subtitle']).'</p>';
    $html .= '<p style="'.$sans.'margin:0 0 20px;color:'.$muted.';font-size:13px;line-height:20px;">Eingegangen '.hk_e(hk_received_label()).'</p>';
    $html .= '<div>'.$button($mailHref, 'Antworten', true);
    if ($phoneHref !== '') {
        $html .= $button('tel:'.$phoneHref, 'Anrufen: '.$s['phone'], false);
    }
    $html .= '</div></td></tr>';

    // Message
    if (! empty($s['message'])) {
        $html .= '<tr><td style="padding:12px 28px 4px;">';
        $html .= '<p style="'.$sans.'margin:0 0 8px;color:'.$muted.';font-size:13px;font-weight:600;">Nachricht</p>';
        $html .= '<div style="'.$sans.'background:'.$mintTint.';border-radius:12px;padding:16px 18px;color:'.$ink.';font-size:15px;line-height:23px;">'.nl2br(hk_e($s['message'])).'</div>';
        $html .= '</td></tr>';
    }

    // Detail sections
    foreach ($s['sections'] as [$sectionTitle, $rows]) {
        $rows = array_filter($rows, fn ($r) => trim((string) $r[1]) !== '');
        if (! $rows) {
            continue;
        }
        $html .= '<tr><td style="padding:20px 28px 0;">';
        $html .= '<p style="'.$display.'margin:0;padding-bottom:8px;border-bottom:2px solid '.$green.';color:'.$navy.';font-size:15px;font-weight:700;">'.hk_e($sectionTitle).'</p>';
        $html .= '<table role="presentation" width="100%" cellpadding="0" cellspacing="0">';
        foreach ($rows as [$label, $value]) {
            $html .= '<tr><td width="38%" valign="top" style="'.$sans.'padding:8px 12px 8px 0;border-bottom:1px solid '.$line.';color:'.$muted.';font-size:14px;line-height:20px;">'.hk_e($label).'</td>';
            $html .= '<td valign="top" style="'.$sans.'padding:8px 0;border-bottom:1px solid '.$line.';color:'.$ink.';font-size:14px;line-height:20px;">'.nl2br(hk_e($value)).'</td></tr>';
        }
        $html .= '</table></td></tr>';
    }

    // Uploaded files
    if (isset($s['files'])) {
        $html .= '<tr><td style="padding:20px 28px 0;">';
        $html .= '<p style="'.$display.'margin:0;padding-bottom:8px;border-bottom:2px solid '.$green.';color:'.$navy.';font-size:15px;font-weight:700;">Dokumente ('.count($s['files']).')</p>';
        if (! $s['files']) {
            $html .= '<p style="'.$sans.'margin:8px 0 0;color:'.$muted.';font-size:14px;">Keine Dateien hochgeladen.</p>';
        }
        $html .= '<table role="presentation" width="100%" cellpadding="0" cellspacing="0">';
        foreach ($s['files'] as $f) {
            $html .= '<tr><td style="'.$sans.'padding:8px 12px 8px 0;border-bottom:1px solid '.$line.';color:'.$ink.';font-size:14px;line-height:20px;">'.hk_e($f['name']).'<br><span style="color:'.$muted.';font-size:13px;">'.hk_e($f['category']).'</span></td>';
            $html .= '<td align="right" valign="top" style="'.$sans.'padding:8px 0;border-bottom:1px solid '.$line.';color:'.$muted.';font-size:13px;white-space:nowrap;">'.hk_e(hk_format_size($f['size'])).'</td></tr>';
        }
        $html .= '</table></td></tr>';
    }

    // Footer
    $html .= '<tr><td style="padding:24px 28px 28px;">';
    $html .= '<p style="'.$sans.'margin:0;color:'.$muted.';font-size:12px;line-height:18px;">Über das Formular auf hk-energieberatung.de gesendet. &bdquo;Antworten&ldquo; schreibt direkt an '.hk_e($s['email']).'.';
    if (! empty($s['reference'])) {
        $html .= '<br>Auf dem Server gesichert unter Referenz '.hk_e($s['reference']).'.';
    }
    $html .= '</p></td></tr>';

    $html .= '</table></td></tr></table></body></html>';

    return $html;
}

function hk_render_email_text(array $s)
{
    $text = $s['preheader']."\n\n";
    $text .= strtoupper($s['kind']).': '.$s['title']."\n".$s['subtitle']."\n";
    $text .= 'Eingegangen '.hk_received_label()."\n";
    $text .= 'E-Mail: '.$s['email'].(! empty($s['phone']) ? ' | Telefon: '.$s['phone'] : '')."\n";

    if (! empty($s['message'])) {
        $text .= "\nNACHRICHT\n".str_repeat('-', 60)."\n".$s['message']."\n";
    }
    foreach ($s['sections'] as [$sectionTitle, $rows]) {
        $rows = array_filter($rows, fn ($r) => trim((string) $r[1]) !== '');
        if (! $rows) {
            continue;
        }
        $text .= "\n".strtoupper($sectionTitle)."\n".str_repeat('-', 60)."\n";
        foreach ($rows as [$label, $value]) {
            $text .= str_pad($label.':', 22).$value."\n";
        }
    }
    if (isset($s['files'])) {
        $text .= "\nDOKUMENTE (".count($s['files']).")\n".str_repeat('-', 60)."\n";
        foreach ($s['files'] as $f) {
            $text .= '- '.$f['name'].' ['.$f['category'].', '.hk_format_size($f['size'])."]\n";
        }
    }
    if (! empty($s['reference'])) {
        $text .= "\nAuf dem Server gesichert unter Referenz ".$s['reference']."\n";
    }

    return $text;
}

// === DELIVERY ===

/**
 * Builds a MIME message: multipart/alternative (text + HTML), wrapped in multipart/mixed when files are attached.
 * Returns [headers without To/Subject, body, from address].
 */
function hk_build_mime(array $config, $text, $html, $replyEmail, $replyName, array $attachments)
{
    $fromAddress = $config['MAIL_FROM_ADDRESS'] ?? ($config['MAIL_USERNAME'] ?? 'info@hk-energieberatung.de');
    $fromName = str_replace(['${APP_NAME}', '$APP_NAME'], 'HK Energieberatung', $config['MAIL_FROM_NAME'] ?? 'HK Energieberatung');
    $encode = fn ($v) => '=?UTF-8?B?'.base64_encode($v).'?=';

    $alt = 'alt_'.bin2hex(random_bytes(12));
    $altBody = '--'.$alt."\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n".chunk_split(base64_encode($text))
        .'--'.$alt."\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n".chunk_split(base64_encode($html))
        .'--'.$alt."--\r\n";

    $headers = [
        'Date: '.date('r'),
        'From: '.$encode($fromName).' <'.$fromAddress.'>',
        'Reply-To: '.$encode($replyName).' <'.$replyEmail.'>',
        'Message-ID: <'.bin2hex(random_bytes(16)).'@'.(substr(strrchr($fromAddress, '@'), 1) ?: 'hk-energieberatung.de').'>',
        'X-Mailer: HK-Energieberatung-Forms/2.0',
        'MIME-Version: 1.0',
    ];

    if (! $attachments) {
        $headers[] = 'Content-Type: multipart/alternative; boundary="'.$alt.'"';

        return [$headers, $altBody, $fromAddress];
    }

    $mixed = 'mix_'.bin2hex(random_bytes(12));
    $headers[] = 'Content-Type: multipart/mixed; boundary="'.$mixed.'"';
    $body = '--'.$mixed."\r\nContent-Type: multipart/alternative; boundary=\"".$alt."\"\r\n\r\n".$altBody;
    foreach ($attachments as $att) {
        $name = $encode($att['name']);
        $body .= '--'.$mixed."\r\nContent-Type: ".($att['type'] ?: 'application/octet-stream').'; name="'.$name."\"\r\n"
            ."Content-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename=\"".$name."\"\r\n\r\n"
            .chunk_split(base64_encode($att['data']));
    }
    $body .= '--'.$mixed."--\r\n";

    return [$headers, $body, $fromAddress];
}

function hk_smtp_send(array $config, $to, $subject, array $headers, $body, $fromAddress)
{
    $host = $config['MAIL_HOST'] ?? '';
    $port = (int) ($config['MAIL_PORT'] ?? 465);
    $username = $config['MAIL_USERNAME'] ?? '';
    $password = $config['MAIL_PASSWORD'] ?? '';
    $encryption = strtolower($config['MAIL_ENCRYPTION'] ?? 'ssl');

    if ($host === '' || $username === '') {
        throw new Exception('SMTP-Konfiguration unvollständig.');
    }

    $implicitTls = $encryption === 'ssl' || $port === 465;
    $context = stream_context_create(['ssl' => ['verify_peer' => false, 'verify_peer_name' => false, 'allow_self_signed' => true]]);
    $socket = @stream_socket_client(($implicitTls ? 'ssl://' : '').$host.':'.$port, $errno, $errstr, 25, STREAM_CLIENT_CONNECT, $context);
    if (! $socket) {
        throw new Exception("Verbindung zum Mailserver fehlgeschlagen: $errstr ($errno)");
    }
    stream_set_timeout($socket, 30);

    $read = function ($expected) use ($socket) {
        $response = '';
        while (($line = fgets($socket, 515)) !== false) {
            $response .= $line;
            if (isset($line[3]) && $line[3] === ' ') {
                break;
            }
        }
        if ((int) substr($response, 0, 3) !== $expected) {
            throw new Exception('SMTP-Fehler: '.trim($response));
        }
    };
    $cmd = function ($line, $expected) use ($socket, $read) {
        fwrite($socket, $line."\r\n");
        $read($expected);
    };

    try {
        $read(220);
        $client = $_SERVER['SERVER_NAME'] ?? 'localhost';
        $cmd('EHLO '.$client, 250);
        if (! $implicitTls && ($encryption === 'tls' || $port === 587)) {
            $cmd('STARTTLS', 220);
            if (! stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT)) {
                throw new Exception('TLS-Verschlüsselung fehlgeschlagen.');
            }
            $cmd('EHLO '.$client, 250);
        }
        if ($password !== '') {
            $cmd('AUTH LOGIN', 334);
            $cmd(base64_encode($username), 334);
            $cmd(base64_encode($password), 235);
        }
        $cmd('MAIL FROM:<'.$fromAddress.'>', 250);
        $cmd('RCPT TO:<'.$to.'>', 250);
        $cmd('DATA', 354);

        $data = implode("\r\n", array_merge(['To: <'.$to.'>', 'Subject: =?UTF-8?B?'.base64_encode($subject).'?='], $headers))."\r\n\r\n".$body;
        $data = preg_replace('/^\./m', '..', $data); // dot-stuffing (RFC 5321)
        $cmd(rtrim($data, "\r\n")."\r\n.", 250);
        fwrite($socket, "QUIT\r\n");
    } finally {
        fclose($socket);
    }
}

/**
 * Sends via SMTP, falling back to PHP mail(). Returns ['sent' => bool, 'via' => 'smtp'|'mail'|'', 'error' => string].
 */
function hk_deliver(array $config, $to, $subject, $text, $html, $replyEmail, $replyName, array $attachments = [])
{
    [$headers, $body, $fromAddress] = hk_build_mime($config, $text, $html, $replyEmail, $replyName, $attachments);
    $error = '';

    if (! empty($config['MAIL_HOST'])) {
        try {
            hk_smtp_send($config, $to, $subject, $headers, $body, $fromAddress);

            return ['sent' => true, 'via' => 'smtp', 'error' => ''];
        } catch (Exception $e) {
            $error = $e->getMessage();
            error_log('hk forms: SMTP failed: '.$error);
        }
    }

    if (@mail($to, '=?UTF-8?B?'.base64_encode($subject).'?=', $body, implode("\r\n", $headers), '-f'.$fromAddress)) {
        return ['sent' => true, 'via' => 'mail', 'error' => $error];
    }

    error_log('hk forms: mail() fallback failed too');

    return ['sent' => false, 'via' => '', 'error' => $error ?: 'mail() fehlgeschlagen'];
}
