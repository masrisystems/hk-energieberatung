/**
 * HK Energieberatung - A/B Split Testing Engine
 * Version 1 (Baseline / Commit 81ab66e) vs Version 2 (Optimized / Current HEAD)
 */

(function () {
  'use strict';

  var COOKIE_NAME = 'hk_ab_variant';
  var EXPIRY_DAYS = 30;

  // Helper: Get Cookie
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  // Helper: Set Cookie
  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/; SameSite=Lax';
  }

  // Helper: Get URL Query Parameter
  function getQueryParam(param) {
    var urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }

  // Determine or override variant
  function initVariant() {
    var forcedVariant = getQueryParam('v') || getQueryParam('variant');
    var resetFlag = getQueryParam('reset_ab');

    if (resetFlag === '1' || resetFlag === 'true') {
      try {
        localStorage.removeItem(COOKIE_NAME);
      } catch (e) {}
      setCookie(COOKIE_NAME, '', -1);
    }

    var variant = forcedVariant;

    if (variant !== 'v1' && variant !== 'v2') {
      // Check stored preference
      try {
        variant = localStorage.getItem(COOKIE_NAME);
      } catch (e) {}
      if (!variant) {
        variant = getCookie(COOKIE_NAME);
      }
    }

    // Default to 50/50 split if unassigned
    if (variant !== 'v1' && variant !== 'v2') {
      variant = Math.random() < 0.5 ? 'v1' : 'v2';
    }

    // Persist assigned variant
    try {
      localStorage.setItem(COOKIE_NAME, variant);
    } catch (e) {}
    setCookie(COOKIE_NAME, variant, EXPIRY_DAYS);

    return variant;
  }

  var activeVariant = initVariant();
  window.HK_AB_VARIANT = activeVariant;

  // Perform client-side route split on home page
  var pathname = window.location.pathname.toLowerCase();
  var isIndexRoot = pathname === '/' || pathname.endsWith('/index.html') || pathname.endsWith('/hk%20energieberatung/') || pathname.endsWith('/hk%20energieberatung');
  var isIndexV1 = pathname.indexOf('/index-v1.html') !== -1;

  if (activeVariant === 'v1' && isIndexRoot && !isIndexV1) {
    // Redirect v1 assigned visitors to index-v1.html
    var targetUrl = 'index-v1.html' + window.location.search + window.location.hash;
    window.location.replace(targetUrl);
    return;
  } else if (activeVariant === 'v2' && isIndexV1) {
    // Redirect v2 assigned visitors back to index.html
    var targetUrl = 'index.html' + window.location.search + window.location.hash;
    window.location.replace(targetUrl);
    return;
  }

  // Push GA4 / Google Tag Impression & Tagging
  function sendAnalyticsImpression() {
    window.dataLayer = window.dataLayer || [];
    function gtag() {
      window.dataLayer.push(arguments);
    }

    gtag('event', 'ab_test_impression', {
      experiment_name: 'landing_v1_vs_v2',
      variant: activeVariant,
      page_title: document.title,
      page_path: window.location.pathname
    });

    // Set custom user property in GA4
    gtag('set', 'user_properties', {
      ab_landing_variant: activeVariant
    });

    console.log('[HK A/B Test] Assigned Variant:', activeVariant);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendAnalyticsImpression);
  } else {
    sendAnalyticsImpression();
  }
})();
