<?php

function ledger_open(string $title, string $active = '', string $description = ''): void {
    if ($description === '') {
        $description = 'Ledgerly is the billing desk for practices that outgrew a shared workbook.';
    }
    $titleEsc = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    $descEsc = htmlspecialchars($description, ENT_QUOTES, 'UTF-8');
    $items = [
        'home' => ['/', 'Platform'],
        'search' => ['/search.php', 'Search'],
        'statements' => ['/upload.php', 'Statements'],
        'pricing' => ['/pricing.php', 'Pricing'],
        'about' => ['/about.php', 'About'],
    ];
    echo '<!doctype html><html lang="en" data-theme="ledger"><head>';
    echo '<meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<meta name="theme-color" content="#3B4BF0">';
    echo '<title>' . $titleEsc . '</title>';
    echo '<meta name="description" content="' . $descEsc . '">';
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    echo '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">';
    echo '<link rel="stylesheet" href="/static/chrome.css">';
    echo '<link rel="stylesheet" href="/style.css">';
    echo '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'8\' fill=\'%233B4BF0\'/%3E%3Ctext x=\'16\' y=\'22\' text-anchor=\'middle\' font-family=\'Georgia\' font-size=\'16\' fill=\'white\'%3EM%3C/text%3E%3C/svg%3E">';
    echo '</head><body>';
    echo '<a class="skip" href="#content">Skip to content</a>';
    echo '<nav class="site-nav" aria-label="Primary">';
    echo '<a class="brand" href="/"><span class="brand-mark">M</span> Ledgerly</a>';
    echo '<div class="nav-links">';
    foreach ($items as $key => $item) {
        $cls = $active === $key ? ' class="is-active"' : '';
        $aria = $active === $key ? ' aria-current="page"' : '';
        echo '<a href="' . htmlspecialchars($item[0], ENT_QUOTES, 'UTF-8') . '"' . $cls . $aria . '>' . htmlspecialchars($item[1], ENT_QUOTES, 'UTF-8') . '</a>';
    }
    echo '</div>';
    echo '<a class="nav-cta" href="/#sign-in">Sign in</a>';
    echo '</nav>';
}

function ledger_footer(): void {
    echo <<<'HTML'
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <a class="brand" href="/"><span class="brand-mark">M</span> Ledgerly</a>
      <p>Billing for practices that still want a person to sign the close. Invoices, statements, and the month live on one desk.</p>
      <p>Harbour Works, London · West Loop, Chicago</p>
    </div>
    <div>
      <h4>Desk</h4>
      <a href="/search.php">Search invoices</a>
      <a href="/profile.php?id=2">Profiles</a>
      <a href="/upload.php">Statements</a>
      <a href="/dashboard.php">Dashboard</a>
      <a href="/api/help.php">API reference</a>
      <a href="/reset.php">Reset access</a>
    </div>
    <div>
      <h4>Company</h4>
      <a href="/about.php">About</a>
      <a href="/pricing.php">Pricing</a>
      <a href="/trust.php">Trust</a>
      <a href="/#sign-in">Sign in</a>
    </div>
  </div>
  <div class="section-inner legal">© 2026 Ledgerly. All rights reserved.</div>
</footer>
HTML;
}

function ledger_end(): void {
    ledger_footer();
    echo '<script src="/static/chrome.js"></script></body></html>';
}
