const fs = require('fs');
const path = require('path');

const indexHtmlPath = path.join(__dirname, 'index.html');
const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');

function extractAndSave(startMarker, endMarker, targetFile) {
  const regex = new RegExp(`<!-- START: ${startMarker} -->\\s*([\\s\\S]*?)\\s*<!-- END: ${endMarker} -->`);
  const match = indexHtml.match(regex);
  if (match && match[1]) {
    fs.writeFileSync(path.join(__dirname, 'components', targetFile), match[1].trim() + '\n', 'utf8');
    console.log(`Extracted ${targetFile}`);
  } else {
    console.log(`Could not find ${startMarker} in index.html`);
  }
}

extractAndSave('HEADER_COMPONENT', 'HEADER_COMPONENT', 'header.html');
extractAndSave('CONTACT_COMPONENT', 'CONTACT_COMPONENT', 'contact.html');
extractAndSave('FOOTER_COMPONENT', 'FOOTER_COMPONENT', 'footer.html');
