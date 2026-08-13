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
  <link rel="icon" type="image/x-icon" href="/favicon.ico" />
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png" />
  <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
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

// Copy downloaded/generated favicons between root and assets/img for full compatibility
const imgDir = path.join(rootDir, 'assets', 'img');
const allFaviconFiles = [
  'favicon.ico',
  'favicon.png',
  'favicon.svg',
  'favicon-16x16.png',
  'favicon-32x32.png',
  'favicon-48x48.png',
  'favicon-96x96.png',
  'favicon-192x192.png',
  'favicon-512x512.png',
  'apple-touch-icon.png',
  'web-app-manifest-192x192.png',
  'web-app-manifest-512x512.png'
];

for (const f of allFaviconFiles) {
  const rootFile = path.join(rootDir, f);
  const imgFile = path.join(imgDir, f);
  if (fs.existsSync(imgFile) && !fs.existsSync(rootFile)) {
    fs.copyFileSync(imgFile, rootFile);
    console.log(`Copied ${f} to root directory`);
  } else if (fs.existsSync(rootFile) && !fs.existsSync(imgFile)) {
    fs.copyFileSync(rootFile, imgFile);
    console.log(`Copied ${f} to assets/img directory`);
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
