const fs = require('fs');
const path = require('path');
const { createIco } = require('./ico-builder');

const imgDir = path.join(__dirname, '..', 'assets', 'img');
const rootDir = path.join(__dirname, '..');

const p16 = fs.readFileSync(path.join(imgDir, 'favicon-16x16.png'));
const p32 = fs.readFileSync(path.join(imgDir, 'favicon-32x32.png'));
const p48 = fs.readFileSync(path.join(imgDir, 'favicon-48x48.png'));

const icoBuffer = createIco([
  { width: 16, height: 16, buffer: p16 },
  { width: 32, height: 32, buffer: p32 },
  { width: 48, height: 48, buffer: p48 }
]);

fs.writeFileSync(path.join(rootDir, 'favicon.ico'), icoBuffer);
fs.writeFileSync(path.join(imgDir, 'favicon.ico'), icoBuffer);

console.log('favicon.ico successfully created in root and assets/img!');
