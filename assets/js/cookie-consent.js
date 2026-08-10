/**
 * HK Energieberatung - Cookie Consent Manager
 * DSGVO (GDPR) + TTDSG konform
 * GA4 Consent Mode v2
 */

(function () {
  'use strict';

  var CONSENT_KEY = 'hk_cookie_consent';

  // --- Consent Mode Helpers ------------------------------------------------

  function grantConsent() {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        analytics_storage: 'granted',
        ad_storage: 'denied'
      });
    }
    localStorage.setItem(CONSENT_KEY, 'granted');
  }

  function denyConsent() {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied'
      });
    }
    localStorage.setItem(CONSENT_KEY, 'denied');
  }

  // --- Banner DOM ----------------------------------------------------------

  function createBanner() {
    var banner = document.createElement('div');
    banner.id = 'hk-cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', 'Cookie-Einwilligung');

    banner.innerHTML =
      '<div class="hk-cookie-inner">' +
      '  <div class="hk-cookie-icon">' +
      '    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '      <circle cx="12" cy="12" r="10"></circle>' +
      '      <circle cx="8.5" cy="10" r="1" fill="currentColor"></circle>' +
      '      <circle cx="14.5" cy="10" r="1" fill="currentColor"></circle>' +
      '      <path d="M9 15a3 3 0 0 0 6 0"></path>' +
      '    </svg>' +
      '  </div>' +
      '  <div class="hk-cookie-text">' +
      '    <p class="hk-cookie-title">Wir verwenden Cookies</p>' +
      '    <p class="hk-cookie-desc">' +
      '      Diese Website verwendet Google Analytics, um die Nutzung zu analysieren und unsere Services zu verbessern.' +
      '      Die Daten werden anonymisiert erhoben. Weitere Informationen finden Sie in unserer' +
      '      <a href="/datenschutz.html" class="hk-cookie-link">Datenschutzerkl&auml;rung</a>.' +
      '    </p>' +
      '  </div>' +
      '  <div class="hk-cookie-actions">' +
      '    <button id="hk-cookie-deny" class="hk-cookie-btn hk-cookie-btn-deny" type="button">Ablehnen</button>' +
      '    <button id="hk-cookie-accept" class="hk-cookie-btn hk-cookie-btn-accept" type="button">Akzeptieren</button>' +
      '  </div>' +
      '</div>';

    return banner;
  }

  function showBanner() {
    var existing = document.getElementById('hk-cookie-banner');
    if (existing) {
      existing.classList.add('hk-cookie-visible');
      return;
    }
    var banner = createBanner();
    document.body.appendChild(banner);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        banner.classList.add('hk-cookie-visible');
      });
    });

    document.getElementById('hk-cookie-accept').addEventListener('click', function () {
      grantConsent();
      hideBanner();
    });

    document.getElementById('hk-cookie-deny').addEventListener('click', function () {
      denyConsent();
      hideBanner();
    });
  }

  function hideBanner() {
    var banner = document.getElementById('hk-cookie-banner');
    if (!banner) return;
    banner.classList.remove('hk-cookie-visible');
    banner.classList.add('hk-cookie-hiding');
    setTimeout(function () {
      if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    }, 350);
  }

  // --- Public API (footer "Einstellungen aendern" link) --------------------

  window.HKCookies = {
    showSettings: function () {
      localStorage.removeItem(CONSENT_KEY);
      showBanner();
    },
    revokeConsent: function () {
      denyConsent();
      localStorage.removeItem(CONSENT_KEY);
      showBanner();
    }
  };

  // --- Init ----------------------------------------------------------------

  function init() {
    var stored = localStorage.getItem(CONSENT_KEY);
    if (stored === 'granted') {
      grantConsent();
    } else if (stored === 'denied') {
      denyConsent();
    } else {
      showBanner();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
