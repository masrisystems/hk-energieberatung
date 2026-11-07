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
  'forderrechner.html',
  'mediathek.html',
  'dokumente.html',
  'impressum.html',
  'datenschutz.html',
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
    // Check if user already consented in a previous session
    var storedConsent = null;
    try {
      storedConsent = localStorage.getItem("hk_cookie_consent");
    } catch (e) {}

    var consentState = storedConsent === "granted" ? "granted" : "denied";

    gtag("consent", "default", {
      analytics_storage: consentState,
      ad_storage: consentState,
      ad_user_data: consentState,
      ad_personalization: consentState,
      wait_for_update: 500,
    });
  </script>
  <script
    async
    src="https://www.googletagmanager.com/gtag/js?id=AW-972344910"
  ></script>
  <script>
    gtag("js", new Date());
    gtag("config", "AW-18393566004");
    gtag("config", "AW-972344910", {
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

  const headIdx = content.indexOf('<head');
  if (headIdx === -1) continue;
  const headCloseIdx = content.indexOf('>', headIdx);

  // Find start position of Google Tag or AB Test block in <head>
  let tagStartIdx = -1;
  const abIdx = content.indexOf('<!-- A/B Testing Traffic Split', headCloseIdx);
  const gtagIdx = content.indexOf('<!-- Google tag (gtag.js)', headCloseIdx);

  if (abIdx !== -1 && gtagIdx !== -1) {
    tagStartIdx = Math.min(abIdx, gtagIdx);
  } else if (abIdx !== -1) {
    tagStartIdx = abIdx;
  } else if (gtagIdx !== -1) {
    tagStartIdx = gtagIdx;
  }

  if (tagStartIdx !== -1) {
    const metaIdx = content.indexOf('<meta', headCloseIdx);
    if (metaIdx !== -1 && metaIdx > tagStartIdx) {
      content = content.substring(0, tagStartIdx) + newGtagHeaderBlock.trimStart() + '\n\n  ' + content.substring(metaIdx);
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
