<?php
declare(strict_types=1);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo 'method_not_allowed';
    exit;
}

function sanitizeLine(string $value, int $maxLength = 500): string
{
    $value = trim($value);
    // Prevent header injection vectors and collapse excessive whitespace.
    $value = str_replace(["\r", "\n"], ' ', $value);
    $value = preg_replace('/\s+/', ' ', $value) ?? '';
    return mb_substr($value, 0, $maxLength);
}

$name = sanitizeLine($_POST['name'] ?? '', 120);
$org = sanitizeLine($_POST['org'] ?? '', 160);
$email = sanitizeLine($_POST['email'] ?? '', 254);
$phone = sanitizeLine($_POST['phone'] ?? '', 60);
$type = sanitizeLine($_POST['type'] ?? '', 120);
$message = trim((string)($_POST['message'] ?? ''));
$message = mb_substr($message, 0, 3000);

if ($name === '' || $email === '' || $message === '') {
    http_response_code(400);
    echo 'missing_required_fields';
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo 'invalid_email';
    exit;
}

$to = 'grandinfo2004@gmail.com';
$subject = 'Website Enquiry from ' . $name;

$lines = [
    'Name: ' . $name,
    'Organisation: ' . ($org !== '' ? $org : 'N/A'),
    'Email: ' . $email,
    'Phone: ' . ($phone !== '' ? $phone : 'N/A'),
    'Enquiry Type: ' . ($type !== '' ? $type : 'N/A'),
    '',
    'Message:',
    $message,
];
$body = implode("\n", $lines);

// Use a fixed from address for better deliverability, and set reply-to to user email.
$headers = [
    'From: GRAND Website <no-reply@grandwarninglights.in>',
    'Reply-To: ' . $email,
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = mail($to, $subject, $body, implode("\r\n", $headers));

if (!$sent) {
    http_response_code(500);
    echo 'mail_failed';
    exit;
}

echo 'success';
?>
