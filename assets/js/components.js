/**
 * Centralized Component Loader for HK Energieberatung
 * Header, Footer, Contact Section, and Map Components
 */

(function () {
  "use strict";

  const path = window.location.pathname;
  const page = path.split("/").pop() || "index.html";

  function isPage(target) {
    if (target === "index.html" && (page === "" || page === "index.html")) return true;
    return page === target;
  }

  // 1. HEADER COMPONENT
  function renderHeader() {
    const el = document.getElementById("header-component");
    if (!el) return;

    el.innerHTML = `
      <header id="header" class="header d-flex align-items-center fixed-top">
        <div class="header-container container-fluid container-xl position-relative d-flex align-items-center justify-content-between">
          <a href="index.html" class="logo d-flex align-items-center me-auto me-xl-0">
            <h1 class="sitename"><img src="assets/img/logo.jpeg" alt="HK Energieberatung Logo" class="img-fluid"></h1>
          </a>

          <nav id="navmenu" class="navmenu">
            <ul>
              <li><a href="${isPage('about.html') ? 'about.html' : isPage('index.html') ? '#about' : 'index.html#about'}" class="${isPage('about.html') ? 'active' : ''}">ÜBER UNS</a></li>
              <li class="dropdown"><a href="${isPage('index.html') ? '#services' : 'index.html#services'}"><span>LEISTUNGEN</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
                <ul>
                  <li><a href="expressausweis.html" class="${isPage('expressausweis.html') ? 'active' : ''}">Express Verbrauchsausweis (48h)</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">Energieausweise</a></li>
                  <li><a href="${isPage('index.html') ? '#features' : 'index.html#features'}">BAFA & KfW Förderungen</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">Hydraulischer Abgleich</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">KfW Kreditanträge</a></li>
                </ul>
              </li>
              <li class="dropdown"><a href="#" class="${isPage('energieberatung-aurich.html') ? 'active' : ''}"><span>STANDORTE</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
                <ul>
                  <li><a href="${isPage('index.html') ? '#contact' : 'index.html#contact'}">Standort Bremen</a></li>
                  <li><a href="energieberatung-aurich.html" class="${isPage('energieberatung-aurich.html') ? 'active' : ''}">Standort Aurich</a></li>
                </ul>
              </li>
              <li class="dropdown"><a href="#" class="${isPage('mediathek.html') || isPage('dokumente.html') || isPage('faq.html') ? 'active' : ''}"><span>INFOTHEK</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
                <ul>
                  <li><a href="mediathek.html" class="${isPage('mediathek.html') ? 'active' : ''}">Erklärvideos (Mediathek)</a></li>
                  <li><a href="dokumente.html" class="${isPage('dokumente.html') ? 'active' : ''}">Formulare & Downloads</a></li>
                  <li><a href="faq.html" class="${isPage('faq.html') ? 'active' : ''}">Häufige Fragen (FAQ)</a></li>
                </ul>
              </li>
              <li><a href="${isPage('index.html') ? '#contact' : 'index.html#contact'}">KONTAKT</a></li>
            </ul>
            <i class="mobile-nav-toggle d-xl-none bi bi-list"></i>
          </nav>

          <a class="btn-getstarted" href="${isPage('index.html') ? '#contact' : 'index.html#contact'}">Jetzt Starten</a>
        </div>
      </header>
    `;

    initNavEvents();
  }

  // Helper to bind nav events for dynamically injected header
  function initNavEvents() {
    const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

    function toggleMobileNav() {
      document.querySelector('body').classList.toggle('mobile-nav-active');
      if (mobileNavToggleBtn) {
        mobileNavToggleBtn.classList.toggle('bi-list');
        mobileNavToggleBtn.classList.toggle('bi-x');
      }
    }

    if (mobileNavToggleBtn) {
      mobileNavToggleBtn.addEventListener('click', toggleMobileNav);
    }

    document.querySelectorAll('#navmenu a').forEach(navLink => {
      navLink.addEventListener('click', function (e) {
        if (this.parentNode.classList.contains('dropdown')) {
          e.preventDefault();
          this.classList.toggle('active');
          const dropdownUl = this.nextElementSibling;
          if (dropdownUl) {
            dropdownUl.classList.toggle('dropdown-active');
          }
          e.stopImmediatePropagation();
          return;
        }

        if (document.querySelector('.mobile-nav-active')) {
          toggleMobileNav();
        }
      });
    });

    document.querySelectorAll('.navmenu .toggle-dropdown').forEach(chevron => {
      chevron.addEventListener('click', function (e) {
        e.preventDefault();
        const parentA = this.parentNode;
        parentA.classList.toggle('active');
        if (parentA.nextElementSibling) {
          parentA.nextElementSibling.classList.toggle('dropdown-active');
        }
        e.stopImmediatePropagation();
      });
    });
  }

  // 2. FOOTER COMPONENT
  function renderFooter() {
    const el = document.getElementById("footer-component");
    if (!el) return;

    el.innerHTML = `
      <footer id="footer" class="footer">
        <div class="container footer-top">
          <div class="row gy-4">
            <div class="col-lg-4 col-md-6 footer-about">
              <a href="index.html" class="logo d-flex align-items-center" aria-label="Startseite">
                <img src="assets/img/logo.jpeg" alt="HK Energieberatung Logo" class="img-fluid">
              </a>
              <address class="footer-contact pt-3">
                <p>
                  <a href="https://maps.app.goo.gl/Pd6vkvJnU2HgLyDv5" target="_blank" rel="noopener noreferrer" aria-label="Adresse auf Google Maps">
                    Industriestraße 34<br>
                    28199 Bremen - Deutschland
                  </a>
                </p>
                <p>
                  <strong>Telefon:</strong>
                  <a href="tel:+491626985115" aria-label="Rufen Sie uns an unter +49 162 6985115">+49 162 6985115</a>
                </p>
                <p>
                  <strong>E-Mail:</strong>
                  <a href="mailto:info@hk-energieberatung.de" aria-label="Schreiben Sie uns eine E-Mail an info@hk-energieberatung.de">info@hk-energieberatung.de</a>
                </p>
              </address>
              <div class="social-links d-flex mt-4">
                <a href="https://www.instagram.com/hk_energieberatung/" target="_blank" aria-label="Instagram"><i class="bi bi-instagram"></i></a>
                <a href="https://de.linkedin.com/in/hussein-khashab-54985334a" target="_blank" aria-label="LinkedIn"><i class="bi bi-linkedin"></i></a>
              </div>
            </div>

            <nav class="col-lg-3 col-md-3 footer-links">
              <h4>Navigation & Menü</h4>
              <ul class="list-unstyled">
                <li><a href="index.html#hero">Startseite</a></li>
                <li><a href="about.html">Über uns</a></li>
                <li><a href="energieberatung-bremen.html">Standort Bremen</a></li>
                <li><a href="energieberatung-aurich.html">Standort Aurich</a></li>
                <li><a href="mediathek.html">Mediathek</a></li>
                <li><a href="dokumente.html">Dokumente & Downloads</a></li>
                <li><a href="faq.html">Häufige Fragen (FAQ)</a></li>
                <li><a href="index.html#contact">Kontakt</a></li>
              </ul>
            </nav>

            <nav class="col-lg-3 col-md-3 footer-links">
              <h4>Unsere Dienstleistungen</h4>
              <ul class="list-unstyled">
                <li><a href="expressausweis.html">Express Verbrauchsausweis (48h)</a></li>
                <li><a href="index.html#services">Energieausweise</a></li>
                <li><a href="index.html#features">BAFA & KfW Förderungen</a></li>
                <li><a href="index.html#services">Hydraulischer Abgleich</a></li>
                <li><a href="index.html#services">KfW Kreditanträge</a></li>
              </ul>
            </nav>

            <div class="col-lg-2 col-md-3 footer-contact-hours">
              <h4>Erreichbarkeit</h4>
              <ul class="list-unstyled">
                <li><i class="bi bi-open me-1"></i> Montag - Samstag<br>9:00 Uhr bis 18:00 Uhr</li>
                <li class="mt-2">
                  <a href="https://wa.me/491626985115" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp Chat">
                    <i class="bi bi-whatsapp me-1"></i> WhatsApp-Chat
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="container copyright text-center mt-4">
          <p>© <span>Copyright</span> <strong class="px-1 sitename">HK Energieberatung</strong> <span>Alle Rechte vorbehalten</span></p>
          <span class="d-flex gap-2 justify-content-center">
            <a href="impressum.html">Impressum</a> - <a href="datenschutz.html">Datenschutz</a>
          </span>
          <div class="credits">
            Designed by <a href="https://bootstrapmade.com/" target="_blank" rel="noopener noreferrer" aria-label="BootstrapMade Website">BootstrapMade</a> | Made by <a href="https://masrisystems.com/" target="_blank" rel="noopener noreferrer" aria-label="Masri Systems Website">Masri Systems</a>
          </div>
        </div>
      </footer>
    `;
  }

  // 3. CONTACT SECTION COMPONENT
  function renderContact() {
    const el = document.getElementById("contact-component");
    if (!el) return;

    el.innerHTML = `
      <section id="contact" class="contact section light-background">
        <div class="container section-title" data-aos="fade-up">
          <h2>Kontakt</h2>
          <p>Haben Sie Fragen oder möchten Sie mehr erfahren? Schreiben Sie uns - wir helfen Ihnen gerne weiter!</p>
        </div>

        <div class="container" data-aos="fade-up" data-aos-delay="100">
          <div class="row g-4 g-lg-5">
            <div class="col-lg-5">
              <div class="info-box" data-aos="fade-up" data-aos-delay="200">
                <h3>Kontaktdaten</h3>
                <p>Im Folgenden finden Sie alle wichtigen Kontaktdaten: Unsere Adresse, Telefonnummer sowie unsere E-Mail-Adresse. Zögern Sie nicht, uns jederzeit zu kontaktieren - wir freuen uns auf Ihre Anfrage!</p>

                <div class="info-item" data-aos="fade-up" data-aos-delay="300">
                  <a href="https://maps.app.goo.gl/Pd6vkvJnU2HgLyDv5" target="_blank" rel="noopener noreferrer">
                    <div class="icon-box"><i class="bi bi-geo-alt"></i></div>
                    <div class="content">
                      <h4>Adresse</h4>
                      Industriestraße 34
                      <p>28199 Bremen - Deutschland</p>
                    </div>
                  </a>
                </div>

                <div class="info-item" data-aos="fade-up" data-aos-delay="400">
                  <a href="tel:+491626985115">
                    <div class="icon-box"><i class="bi bi-telephone"></i></div>
                    <div class="content">
                      <h4>Kontakt</h4>
                      +49 162 6985115
                    </div>
                  </a>
                </div>

                <div class="info-item" data-aos="fade-up" data-aos-delay="500">
                  <a href="mailto:info@hk-energieberatung.de">
                    <div class="icon-box"><i class="bi bi-envelope"></i></div>
                    <div class="content">
                      <h4>Email Adresse</h4>
                      info@hk-energieberatung.de
                    </div>
                  </a>
                </div>
              </div>
            </div>

            <div class="col-lg-7">
              <div class="contact-form" data-aos="fade-up" data-aos-delay="300">
                <h3>Schicken Sie uns Ihr Anliegen!</h3>
                <p>Bitte geben Sie hier Ihren Namen, Ihre E-Mail-Adresse und Ihre Nachricht ein:</p>

                <form action="forms/contact.php" method="post" class="php-email-form" data-aos="fade-up" data-aos-delay="200">
                  <div class="row gy-4">
                    <div class="col-md-6">
                      <input type="text" name="name" class="form-control" placeholder="Name" required>
                    </div>
                    <div class="col-md-6">
                      <input type="email" name="email" class="form-control" placeholder="Ihre Email" required>
                    </div>
                    <div class="col-12">
                      <input type="text" name="subject" class="form-control" placeholder="Betreff" required>
                    </div>
                    <div class="col-12">
                      <textarea name="message" class="form-control" rows="6" placeholder="Nachricht" required></textarea>
                    </div>

                    <div style="display:none;">
                      <input type="text" name="website" autocomplete="off">
                    </div>

                    <div class="col-12">
                      <input id="privacy" type="checkbox" name="privacy" required>
                      <label for="privacy">
                        Ich akzeptiere die <a href="datenschutz.html" target="_blank">Datenschutzerklärung</a>.
                      </label>
                    </div>

                    <div class="col-12 text-center">
                      <div class="loading">Loading</div>
                      <div class="error-message"></div>
                      <div class="sent-message">Ihre Nachricht wurde erfolgreich abgeschickt. Vielen Dank!</div>
                      <button type="submit" class="btn">Senden</button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  // 4. MAP COMPONENT
  function renderMap() {
    const el = document.getElementById("map-component");
    if (!el) return;

    const mapSrc = el.getAttribute("data-map-src") || "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2396.5144844300077!2d8.804630276924848!3d53.08161887335264!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47b128151bce603d%3A0x2f7deec05f1ef59f!2sB%C3%BCrgermeister-Smidt-Stra%C3%9Fe%2C%2028195%20Bremen%2C%20Germany!5e0!3m2!1sen!2sde!4v1720000000000!5m2!1sen!2sde";

    el.innerHTML = `
      <section class="section p-0">
        <div class="container-fluid p-0" data-aos="fade-up">
          <iframe src="${mapSrc}" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
      </section>
    `;
  }

  function initAllComponents() {
    renderHeader();
    renderFooter();
    renderContact();
    renderMap();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAllComponents);
  } else {
    initAllComponents();
  }

})();
