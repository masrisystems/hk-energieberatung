const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');

const filesToUpdate = [
  'index.html',
  'index-v1.html',
  'about.html',
  'energieberatung-bremen.html',
  'energieberatung-aurich.html',
  'expressausweis.html',
  'faq.html',
  'mediathek.html',
  'dokumente.html',
  'impressum.html',
  'datenschutz.html',
  'data-protection.html',
  'agb.html'
];

const newGtagHeaderBlock = `  <!-- A/B Testing Traffic Split & Analytics Tagging (Loaded first so variant is assigned before page_view fires) -->
  <script src="assets/js/ab-test.js"></script>

  <!-- Google tag (gtag.js) – Consent Mode v2 -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {
      dataLayer.push(arguments);
    }
    gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      wait_for_update: 500,
    });
  </script>
  <script
    async
    src="https://www.googletagmanager.com/gtag/js?id=AW-972344910"
  ></script>
  <script>
    gtag("js", new Date());
    gtag("config", "AW-972344910", {
      anonymize_ip: true,
      variant: window.HK_AB_VARIANT || "v2",
      landing_variant: window.HK_AB_VARIANT || "v2",
      user_properties: {
        ab_landing_variant: window.HK_AB_VARIANT || "v2",
        variant: window.HK_AB_VARIANT || "v2"
      }
    });
  </script>`;

let updatedCount = 0;

for (const filename of filesToUpdate) {
  const filePath = path.join(rootDir, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filename}`);
    continue;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let original = content;

  // Find start position of Google Tag or AB Test block in <head>
  let startIdx = content.indexOf('<!-- A/B Testing Traffic Split');
  if (startIdx === -1) {
    startIdx = content.indexOf('<!-- Google tag (gtag.js)');
  }

  if (startIdx !== -1) {
    // Find the start of <meta charset or <meta name="viewport" after startIdx
    const metaIdx = content.indexOf('<meta', startIdx);
    if (metaIdx !== -1) {
      content = content.substring(0, startIdx) + newGtagHeaderBlock + '\n\n  ' + content.substring(metaIdx);
    }
  }

  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated ${filename}`);
    updatedCount++;
  } else {
    console.log(`No change for ${filename}`);
  }
}

console.log(`Finished processing ${updatedCount} HTML files.`);
