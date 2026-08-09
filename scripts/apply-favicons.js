const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');

const filesToUpdate = [
  'index.html',
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
  'agb.html',
  'old.html'
];

const newFaviconMarkup = `  <!-- Favicons -->
  <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />`;

// Regex pattern to match existing favicon blocks (with comments or without)
const faviconRegex = /([ \t]*(?:<!--\s*Favicons\s*-->\r?\n)?)(?:[ \t]*<link[^>]+(?:rel="(?:icon|shortcut icon|apple-touch-icon|manifest)"|href="[^"]*(?:favicon|apple-touch-icon|site\.webmanifest)[^"]*")[^>]*>\r?\n?)+/gi;

let updatedCount = 0;

for (const filename of filesToUpdate) {
  const filePath = path.join(rootDir, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filename}`);
    continue;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let original = content;

  if (faviconRegex.test(content)) {
    faviconRegex.lastIndex = 0;
    content = content.replace(faviconRegex, newFaviconMarkup + '\n');
  } else {
    // If no existing favicon tag found, insert right after <head>
    content = content.replace(/<head>/i, '<head>\n' + newFaviconMarkup);
  }

  if (content !== original) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated ${filename}`);
    updatedCount++;
  } else {
    console.log(`No changes for ${filename}`);
  }
}

// Copy downloaded favicons to assets/img for backwards compatibility
const imgDir = path.join(rootDir, 'assets', 'img');
const downloadedFiles = [
  'favicon.svg',
  'favicon-96x96.png',
  'favicon.ico',
  'apple-touch-icon.png',
  'web-app-manifest-192x192.png',
  'web-app-manifest-512x512.png'
];

for (const f of downloadedFiles) {
  const src = path.join(rootDir, f);
  const dest = path.join(imgDir, f);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
  }
}

// Also customize site.webmanifest name
const manifestPath = path.join(rootDir, 'site.webmanifest');
if (fs.existsSync(manifestPath)) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  manifest.name = "HK Energieberatung";
  manifest.short_name = "HK Energie";
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');
  console.log('Updated site.webmanifest name and short_name');
}

console.log(`Done! Successfully processed ${updatedCount} HTML files.`);
