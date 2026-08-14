/**
 * Static HTML Component Pre-Renderer & Synchronizer for HK Energieberatung
 * Bakes master templates into HTML files for 100% pre-rendered SEO & 0ms performance.
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const COMPONENTS_DIR = path.join(ROOT_DIR, 'components');

const TARGET_FILES = [
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

// Helper to read component HTML
function getComponent(filename) {
  const filePath = path.join(COMPONENTS_DIR, filename);
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, 'utf8');
  }
  return null;
}

// Adjust active links for specific target page
function customizeHeader(headerHtml, targetPage) {
  let customized = headerHtml;

  // Clear existing active classes
  customized = customized.replace(/\sclass="active"/g, '');

  if (targetPage === 'index.html' || targetPage === 'index-v1.html') {
    customized = customized.replace('data-page="index.html#hero"', 'data-page="index.html#hero" class="active"');
  } else if (targetPage === 'about.html') {
    customized = customized.replace('data-page="about.html"', 'data-page="about.html" class="active"');
    customized = customized.replace('data-page="index.html#about"', 'data-page="index.html#about" class="active"');
  } else if (targetPage === 'faq.html') {
    customized = customized.replace('data-page="infothek"', 'data-page="infothek" class="active"');
    customized = customized.replace('data-page="faq.html"', 'data-page="faq.html" class="active"');
  } else if (targetPage === 'energieberatung-bremen.html') {
    customized = customized.replace('data-page="standorte"', 'data-page="standorte" class="active"');
    customized = customized.replace('data-page="energieberatung-bremen.html"', 'data-page="energieberatung-bremen.html" class="active"');
  } else if (targetPage === 'energieberatung-aurich.html') {
    customized = customized.replace('data-page="standorte"', 'data-page="standorte" class="active"');
    customized = customized.replace('data-page="energieberatung-aurich.html"', 'data-page="energieberatung-aurich.html" class="active"');
  } else if (targetPage === 'expressausweis.html') {
    customized = customized.replace('data-page="expressausweis.html"', 'data-page="expressausweis.html" class="active"');
  } else if (targetPage === 'forderrechner.html') {
    customized = customized.replace('data-page="forderrechner.html"', 'data-page="forderrechner.html" class="active"');
  } else if (targetPage === 'mediathek.html') {
    customized = customized.replace('data-page="infothek"', 'data-page="infothek" class="active"');
    customized = customized.replace('data-page="mediathek.html"', 'data-page="mediathek.html" class="active"');
  } else if (targetPage === 'dokumente.html') {
    customized = customized.replace('data-page="infothek"', 'data-page="infothek" class="active"');
    customized = customized.replace('data-page="dokumente.html"', 'data-page="dokumente.html" class="active"');
  }

  return customized;
}

// Main sync function
function syncComponents() {
  console.log('🔄 Syncing static HTML components...');

  const rawHeader = getComponent('header.html');
  const footer = getComponent('footer.html');
  const contact = getComponent('contact.html');

  if (!rawHeader || !footer) {
    console.error('❌ Missing header.html or footer.html in components directory.');
    process.exit(1);
  }

  TARGET_FILES.forEach(filename => {
    const filePath = path.join(ROOT_DIR, filename);
    if (!fs.existsSync(filePath)) return;

    let content = fs.readFileSync(filePath, 'utf8');
    const header = customizeHeader(rawHeader, filename);

    // Replace Header
    const headerRegex = /<!-- START: HEADER_COMPONENT -->[\s\S]*?<!-- END: HEADER_COMPONENT -->/g;
    if (headerRegex.test(content)) {
      content = content.replace(headerRegex, `<!-- START: HEADER_COMPONENT -->\n${header}\n<!-- END: HEADER_COMPONENT -->`);
    } else {
      content = content.replace(/<div id="header-component"><\/div>/g, `<!-- START: HEADER_COMPONENT -->\n${header}\n<!-- END: HEADER_COMPONENT -->`);
    }

    // Replace Footer
    const footerRegex = /<!-- START: FOOTER_COMPONENT -->[\s\S]*?<!-- END: FOOTER_COMPONENT -->/g;
    if (footerRegex.test(content)) {
      content = content.replace(footerRegex, `<!-- START: FOOTER_COMPONENT -->\n${footer}\n<!-- END: FOOTER_COMPONENT -->`);
    } else {
      content = content.replace(/<div id="footer-component"><\/div>/g, `<!-- START: FOOTER_COMPONENT -->\n${footer}\n<!-- END: FOOTER_COMPONENT -->`);
    }

    // Replace Contact (if container present or marker present)
    if (contact) {
      const contactRegex = /<!-- START: CONTACT_COMPONENT -->[\s\S]*?<!-- END: CONTACT_COMPONENT -->/g;
      if (contactRegex.test(content)) {
        content = content.replace(contactRegex, `<!-- START: CONTACT_COMPONENT -->\n${contact}\n<!-- END: CONTACT_COMPONENT -->`);
      } else if (content.includes('<div id="contact-component"></div>')) {
        content = content.replace(/<div id="contact-component"><\/div>/g, `<!-- START: CONTACT_COMPONENT -->\n${contact}\n<!-- END: CONTACT_COMPONENT -->`);
      }
    }

    // Safe write with retry for Windows file lock resilience
    let written = false;
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        fs.writeFileSync(filePath, content, 'utf8');
        written = true;
        break;
      } catch (err) {
        if (attempt === 4) throw err;
        const start = Date.now();
        while (Date.now() - start < 100) {}
      }
    }
    if (written) {
      console.log(`  ✅ Synced: ${filename}`);
    }
  });

  console.log('✨ All HTML components pre-rendered and synchronized successfully!');
}

syncComponents();
