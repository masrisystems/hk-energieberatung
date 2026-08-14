const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');

function cleanAll() {
  const files = [
    'index.html',
    'index-v1.html',
    'about.html',
    'faq.html',
    'energieberatung-bremen.html',
    'energieberatung-aurich.html',
    'expressausweis.html',
    'forderrechner.html',
    'mediathek.html',
    'dokumente.html',
    'impressum.html',
    'datenschutz.html'
  ];

  files.forEach(fileName => {
    const filePath = path.join(ROOT_DIR, fileName);
    if (!fs.existsSync(filePath)) return;
    let html = fs.readFileSync(filePath, 'utf8');

    // 1. Hero & Sublinks
    html = html.replace(/style="color:\s*var\(--default-color\);\s*opacity:\s*0\.9;?"/gi, '');
    html = html.replace(/class="mb-4 fs-5"/g, 'class="mb-4 fs-5 opacity-90"');
    html = html.replace(/class="d-inline-flex align-items-center text-decoration-none fw-bold"[\s\n\r]*style="color:\s*var\(--heading-color\);\s*font-size:\s*0\.95rem;?"/gi, 'class="hero-sublink fw-bold"');
    html = html.replace(/<i class="bi bi-calculator me-2" style="color:\s*#2b7a5a;?"><\/i>/gi, '<i class="bi bi-calculator me-2 hero-sublink-icon"></i>');
    html = html.replace(/<i class="bi bi-calculator me-2"[\s\n\r]*style="color:\s*#2b7a5a;?"[\s\n\r]*><\/i>/gi, '<i class="bi bi-calculator me-2 hero-sublink-icon"></i>');
    html = html.replace(/<i class="bi bi-file-earmark-check me-2" style="color:\s*#2b7a5a;?"><\/i>/gi, '<i class="bi bi-file-earmark-check me-2 hero-sublink-icon"></i>');
    html = html.replace(/<i class="bi bi-file-earmark-check me-2"[\s\n\r]*style="color:\s*#2b7a5a;?"[\s\n\r]*><\/i>/gi, '<i class="bi bi-file-earmark-check me-2 hero-sublink-icon"></i>');

    // 2. Headings & Lead Text
    html = html.replace(/<h1 class="display-5 fw-bold mb-3" style="color:\s*var\(--heading-color\);?">/gi, '<h1 class="display-5 fw-bold mb-3 text-heading">');
    html = html.replace(/<h2 style="font-size:\s*2\.2rem;\s*font-weight:\s*800;\s*color:\s*var\(--heading-color\);?">/gi, '<h2 class="section-title-xl">');
    html = html.replace(/<h2 style="font-family:\s*var\(--heading-font\);\s*color:\s*var\(--heading-color\);\s*font-weight:\s*800;?">/gi, '<h2 class="section-title-xl">');
    html = html.replace(/<p class="lead" style="color:\s*color-mix\(in srgb, var\(--default-color\), transparent 20%\);?">/gi, '<p class="lead lead-text-muted">');
    html = html.replace(/<p class="lead text-muted mb-4" style="line-height:\s*1\.7;\s*font-size:\s*1\.05rem;?">/gi, '<p class="lead text-muted mb-4 lead-text-lg">');
    html = html.replace(/<p class="lead text-muted mt-2 max-w-700 mx-auto" style="font-size:\s*1\.05rem;?">/gi, '<p class="lead text-muted mt-2 max-w-700 mx-auto lead-text-lg">');
    html = html.replace(/style="max-width:\s*750px;\s*color:\s*color-mix\(in srgb,\s*var\(--default-color\),\s*transparent 25%\);?"/gi, 'class="lead-max-w"');

    // 3. Price & Quotes
    html = html.replace(/<h4 class="mb-4" style="color:\s*var\(--accent-color\);\s*font-weight:\s*700;?">/gi, '<h4 class="mb-4 price-highlight">');
    html = html.replace(/<h4\s+class="mb-4"\s+style="color:\s*var\(--accent-color\);\s*font-weight:\s*700"\s*>/gi, '<h4 class="mb-4 price-highlight">');
    html = html.replace(/<div class="p-3 rounded-3 style-box" style="background:\s*color-mix\(in srgb, var\(--accent-color\), transparent 93%\);\s*border-left:\s*4px solid var\(--accent-color\);?">/gi, '<div class="p-3 rounded-3 style-box founder-quote-box">');
    html = html.replace(/<img src="assets\/img\/aurich_map\.jpeg" alt="Aurich Karte" style="mix-blend-mode:\s*multiply;?">/gi, '<img src="assets/img/aurich_map.jpeg" alt="Aurich Karte" class="map-blend-multiply">');

    // 4. Förderrechner Banner
    html = html.replace(/id="foerderrechner-banner" class="expressausweis-banner section" style="padding-top:\s*0;?"/gi, 'id="foerderrechner-banner" class="expressausweis-banner section pt-0"');
    html = html.replace(/id="foerderrechner-banner"[\s\n\r]*class="expressausweis-banner section"[\s\n\r]*style="padding-top:\s*0;?"/gi, 'id="foerderrechner-banner" class="expressausweis-banner section pt-0"');
    html = html.replace(/class="expressausweis-card"[\s\n\r]*style="[\s\n\r]*background:\s*linear-gradient\(135deg,\s*#ffffff\s*0%,\s*#f4faf7\s*100%\);[\s\n\r]*border:\s*2px\s*solid\s*var\(--accent-color\);[\s\n\r]*box-shadow:\s*0\s*10px\s*30px\s*rgba\(45,\s*70,\s*94,\s*0\.08\);[\s\n\r]*"/gi, 'class="expressausweis-card foerderrechner-banner-card"');
    html = html.replace(/class="d-inline-flex align-items-center gap-2 px-3 py-1 mb-3 rounded-pill"[\s\n\r]*style="[\s\n\r]*background:\s*rgba\(171,\s*216,\s*195,\s*0\.3\);[\s\n\r]*color:\s*#1e3d30;[\s\n\r]*font-weight:\s*700;[\s\n\r]*font-size:\s*0\.85rem;?[\s\n\r]*"/gi, 'class="d-inline-flex align-items-center gap-2 px-3 py-1 mb-3 rounded-pill foerderrechner-pill"');
    html = html.replace(/class="banner-title"[\s\n\r]*style="[\s\n\r]*color:\s*var\(--heading-color\);[\s\n\r]*font-weight:\s*800;[\s\n\r]*font-size:\s*2rem;[\s\n\r]*margin-bottom:\s*15px;?[\s\n\r]*"/gi, 'class="banner-title foerderrechner-heading"');
    html = html.replace(/class="banner-note mb-4"[\s\n\r]*style="[\s\n\r]*color:\s*var\(--default-color\);[\s\n\r]*font-size:\s*1\.05rem;[\s\n\r]*line-height:\s*1\.6;?[\s\n\r]*"/gi, 'class="banner-note mb-4 foerderrechner-desc"');
    html = html.replace(/class="p-4 rounded-4"[\s\n\r]*style="[\s\n\r]*background:\s*#ffffff;[\s\n\r]*border:\s*2px\s*solid\s*rgba\(171,\s*216,\s*195,\s*0\.5\);[\s\n\r]*box-shadow:\s*0\s*8px\s*24px\s*rgba\(0,\s*0,\s*0,\s*0\.04\);?[\s\n\r]*"/gi, 'class="p-4 rounded-4 foerderrechner-stat-card"');
    html = html.replace(/style="[\s\n\r]*font-size:\s*2\.75rem;[\s\n\r]*font-weight:\s*900;[\s\n\r]*color:\s*#1e3d30;[\s\n\r]*line-height:\s*1\.1;?[\s\n\r]*"/gi, 'class="foerderrechner-stat-num"');
    html = html.replace(/style="[\s\n\r]*font-weight:\s*700;[\s\n\r]*color:\s*var\(--heading-color\);[\s\n\r]*margin-top:\s*6px;?[\s\n\r]*"/gi, 'class="foerderrechner-stat-title"');
    html = html.replace(/<hr style="margin:\s*14px 0;\s*opacity:\s*0\.15;?"\s*\/?>/gi, '<hr class="foerderrechner-stat-divider" />');
    html = html.replace(/style="font-size:\s*1\.75rem;\s*font-weight:\s*800;\s*color:\s*#2d465e;?"/gi, 'class="foerderrechner-stat-subnum"');
    html = html.replace(/style="font-size:\s*0\.9rem;\s*color:\s*#6c757d;\s*font-weight:\s*500;?"/gi, 'class="foerderrechner-stat-subtitle"');

    // 5. Services calculator card
    html = html.replace(/class="service-card d-flex align-items-center justify-content-between flex-wrap gap-3"[\s\n\r]*style="[\s\n\r]*border-left:\s*4px\s*solid\s*var\(--accent-color\);[\s\n\r]*background:\s*#ffffff;?[\s\n\r]*"/gi, 'class="service-card d-flex align-items-center justify-content-between flex-wrap gap-3 service-card-calculator"');
    html = html.replace(/class="icon flex-shrink-0"[\s\n\r]*style="[\s\n\r]*background:\s*rgba\(171,\s*216,\s*195,\s*0\.25\);[\s\n\r]*color:\s*#1e3d30;[\s\n\r]*width:\s*60px;[\s\n\r]*height:\s*60px;[\s\n\r]*border-radius:\s*12px;[\s\n\r]*display:\s*flex;[\s\n\r]*align-items:\s*center;[\s\n\r]*justify-content:\s*center;[\s\n\r]*font-size:\s*1\.75rem;?[\s\n\r]*"/gi, 'class="icon flex-shrink-0 service-card-calc-icon"');
    html = html.replace(/<h3 class="mb-1" style="font-size:\s*1\.25rem;?">/gi, '<h3 class="mb-1 fs-card-title">');

    // 6. Exit popup & Form hints
    html = html.replace(/<h3 class="mb-3" style="color:\s*var\(--heading-color\);?">/gi, '<h3 class="mb-3 text-heading">');
    html = html.replace(/style="display:\s*none;?"\s+aria-hidden="true"/gi, 'class="d-none" aria-hidden="true"');
    html = html.replace(/style="display:\s*none;?"/gi, 'class="d-none"');
    html = html.replace(/style="max-height:\s*140px;\s*width:\s*auto;?"/gi, 'class="cert-img-badge"');
    html = html.replace(/style="max-width:\s*500px;?"/gi, 'class="lead-form-max-w"');

    // 7. FAQ page
    html = html.replace(/class="container" style="max-width:\s*960px;?"/gi, 'class="container container-faq-max"');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*17%;\s*background:\s*#c7e6d8;?">/gi, '<div class="faq-bar-fill faq-bar-17">');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*25%;\s*background:\s*#c7e6d8;?">/gi, '<div class="faq-bar-fill faq-bar-25">');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*25%;\s*background:\s*#8fc9ae;?">/gi, '<div class="faq-bar-fill faq-bar-25-alt">');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*33%;\s*background:\s*#8fc9ae;?">/gi, '<div class="faq-bar-fill faq-bar-33">');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*50%;\s*background:\s*#6fae91;?">/gi, '<div class="faq-bar-fill faq-bar-50">');
    html = html.replace(/<span class="faq-bar-value d-md-none" style="color:\s*#4a8b6f;?">/gi, '<span class="faq-bar-value d-md-none text-faq-val">');
    html = html.replace(/<div class="faq-bar-fill" style="width:\s*100%;\s*background:\s*#4a8b6f;\s*color:\s*#ffffff;?">/gi, '<div class="faq-bar-fill faq-bar-100">');
    
    html = html.replace(/<div class="faq-scale-seg" style="background:#1a9850;?">/gi, '<div class="faq-scale-seg scale-ap">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#3aa956;?">/gi, '<div class="faq-scale-seg scale-a">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#7dbb50;?">/gi, '<div class="faq-scale-seg scale-b">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#c3d94e;?">/gi, '<div class="faq-scale-seg scale-c">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#f6e93e;\s*color:#5a4a00;?">/gi, '<div class="faq-scale-seg scale-d">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#f9b234;?">/gi, '<div class="faq-scale-seg scale-e">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#f2792a;?">/gi, '<div class="faq-scale-seg scale-f">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#e6432b;?">/gi, '<div class="faq-scale-seg scale-g">');
    html = html.replace(/<div class="faq-scale-seg" style="background:#c1121f;?">/gi, '<div class="faq-scale-seg scale-h">');

    // 8. Fördermittelrechner page
    html = html.replace(/<span id="bar-total-label" class="fw-bold" style="color:\s*#245840;?">/gi, '<span id="bar-total-label" class="fw-bold text-rechner-green">');
    html = html.replace(/<span id="save-pct-label" class="fw-bold" style="color:\s*#245840;?">/gi, '<span id="save-pct-label" class="fw-bold text-rechner-green">');
    html = html.replace(/<div class="sv-bar before" id="sv-before" style="height:\s*10%;?"><\/div>/gi, '<div class="sv-bar before sv-bar-init" id="sv-before"></div>');
    html = html.replace(/<div class="sv-bar after" id="sv-after" style="height:\s*10%;?"><\/div>/gi, '<div class="sv-bar after sv-bar-init" id="sv-after"></div>');
    html = html.replace(/style="cursor:\s*pointer;\s*margin-bottom:\s*0;?"/gi, 'class="cursor-pointer mb-0"');
    html = html.replace(/<div class="bar-track" style="height:\s*10px;?">/gi, '<div class="bar-track bar-track-sm">');

    fs.writeFileSync(filePath, html, 'utf8');
  });
}

cleanAll();
console.log('✅ Deep clean completed!');
