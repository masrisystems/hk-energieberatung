/**
* Template Name: iLanding
* Template URL: https://bootstrapmade.com/ilanding-bootstrap-landing-page-template/
* Updated: Nov 12 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function () {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader || !selectBody) return;
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle & dropdown handling
   */
  function mobileNavToggle() {
    const selectBody = document.querySelector('body');
    const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
    if (selectBody) selectBody.classList.toggle('mobile-nav-active');
    if (mobileNavToggleBtn) {
      mobileNavToggleBtn.classList.toggle('bi-list');
      mobileNavToggleBtn.classList.toggle('bi-x');
    }
  }

  // Event delegation for mobile nav toggle
  document.addEventListener('click', function (e) {
    const toggleBtn = e.target.closest('.mobile-nav-toggle');
    if (toggleBtn) {
      mobileNavToggle();
    }
  });

  /**
   * Navmenu Links & Dropdowns
   */
  document.addEventListener('click', function (e) {
    const navLink = e.target.closest('#navmenu a');
    if (!navLink) return;

    if (navLink.parentNode.classList.contains('dropdown')) {
      e.preventDefault();
      navLink.classList.toggle('active');
      const dropdownUl = navLink.nextElementSibling || (navLink.querySelector('.toggle-dropdown') && navLink.nextElementSibling);
      if (dropdownUl) {
        dropdownUl.classList.toggle('dropdown-active');
      }
      return;
    }

    if (document.querySelector('.mobile-nav-active')) {
      mobileNavToggle();
    }
  });

  /**
   * Toggle mobile nav dropdowns via chevron icon
   */
  document.addEventListener('click', function (e) {
    const chevron = e.target.closest('.navmenu .toggle-dropdown');
    if (!chevron) return;
    e.preventDefault();
    const parentA = chevron.parentNode;
    if (parentA) {
      parentA.classList.toggle('active');
      if (parentA.nextElementSibling) {
        parentA.nextElementSibling.classList.toggle('dropdown-active');
      }
    }
  });

  /**
   * Scroll top button
   */
  function toggleScrollTop() {
    const scrollTop = document.querySelector('.scroll-top');
    if (scrollTop) {
      if (window.scrollY > 100) {
        scrollTop.classList.add('active');
        document.body.classList.add('scroll-top-visible');
      } else {
        scrollTop.classList.remove('active');
        document.body.classList.remove('scroll-top-visible');
      }
    }
  }

  document.addEventListener('click', function (e) {
    const scrollTopBtn = e.target.closest('.scroll-top');
    if (scrollTopBtn) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  if (typeof GLightbox !== 'undefined') {
    GLightbox({
      selector: '.glightbox'
    });
  }

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    if (typeof Swiper === 'undefined') return;
    document.querySelectorAll(".init-swiper").forEach(function (swiperElement) {
      const configEl = swiperElement.querySelector(".swiper-config");
      if (!configEl) return;
      let config = JSON.parse(configEl.innerHTML.trim());

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Initiate Pure Counter
   */
  if (typeof PureCounter !== 'undefined') {
    new PureCounter();
  }

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function () {
    if (window.location.hash) {
      const section = document.querySelector(window.location.hash);
      if (section) {
        setTimeout(() => {
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop || '0px';
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  function navmenuScrollspy() {
    const navmenulinks = document.querySelectorAll('.navmenu a');
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    });
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

  /**
   * About Section Mobile Card Deck Swap
   */
  const aboutCardsDeck = document.querySelector('.about-cards-deck');
  if (aboutCardsDeck) {
    aboutCardsDeck.addEventListener('click', function () {
      this.classList.toggle('cards-swapped');
    });
  }

})();