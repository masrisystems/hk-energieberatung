const https = require('https');
const fs = require('fs');
const path = require('path');

const baseUrl = 'https://realfavicongenerator.net/files/9f062198-a12b-48b7-8b06-03f831f9dcef/';
const files = [
  'favicon.svg',
  'favicon-96x96.png',
  'favicon.ico',
  'apple-touch-icon.png',
  'web-app-manifest-192x192.png',
  'web-app-manifest-512x512.png',
  'site.webmanifest'
];

const publicDir = path.resolve(__dirname, '..');

function download(file) {
  return new Promise((resolve, reject) => {
    const url = baseUrl + file;
    const dest = path.join(publicDir, file);
    const fileStream = fs.createWriteStream(dest);

    https.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // Handle redirect
        https.get(res.headers.location, (redirectRes) => {
          redirectRes.pipe(fileStream);
          fileStream.on('finish', () => {
            fileStream.close();
            const stats = fs.statSync(dest);
            console.log(`Downloaded ${file} (${stats.size} bytes)`);
            resolve();
          });
        }).on('error', reject);
        return;
      }

      if (res.statusCode !== 200) {
        reject(new Error(`Failed to download ${file}: HTTP ${res.statusCode}`));
        return;
      }

      res.pipe(fileStream);
      fileStream.on('finish', () => {
        fileStream.close();
        const stats = fs.statSync(dest);
        console.log(`Downloaded ${file} (${stats.size} bytes)`);
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function run() {
  console.log(`Downloading favicons to ${publicDir}...`);
  for (const file of files) {
    try {
      await download(file);
    } catch (e) {
      console.error(`Error downloading ${file}:`, e.message);
      process.exit(1);
    }
  }
  console.log('All favicon files downloaded successfully!');
}

run();
