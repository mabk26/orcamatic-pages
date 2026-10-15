(() => {
  const toggle = document.querySelector('[data-nav-toggle]');
  const mobileNav = document.querySelector('[data-mobile-nav]');

  if (toggle && mobileNav) {
    const isOpen = () => mobileNav.classList.contains('is-open');
    const setOpen = (open) => {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      mobileNav.classList.toggle('is-open', open);
    };

    toggle.addEventListener('click', () => setOpen(!isOpen()));
    mobileNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => setOpen(false));
    });

    // Escape closes the menu and returns focus to the button that opened it.
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && isOpen()) {
        setOpen(false);
        toggle.focus();
      }
    });

    // Tapping anywhere outside the header closes the menu.
    document.addEventListener('click', (event) => {
      if (isOpen() && !event.target.closest('.site-header')) {
        setOpen(false);
      }
    });

    // Rotating or resizing to desktop width hides the mobile menu, so reset its state.
    const desktop = window.matchMedia('(min-width: 801px)');
    const resetOnDesktop = () => {
      if (desktop.matches && isOpen()) setOpen(false);
    };
    if (desktop.addEventListener) {
      desktop.addEventListener('change', resetOnDesktop);
    } else {
      desktop.addListener(resetOnDesktop);
    }
  }

  document.querySelectorAll('[data-year]').forEach((element) => {
    element.textContent = new Date().getFullYear();
  });

  // Store screenshots are hot-linked from the Chrome Web Store CDN. If one ever
  // fails to load, hide that tile (or swap the hero frame for a link) instead of
  // leaving a broken image on the page.
  document.querySelectorAll('[data-shot] img').forEach((img) => {
    const markFailed = () => {
      const shot = img.closest('[data-shot]');
      if (shot) shot.setAttribute('data-shot-failed', '');
    };
    if (img.complete && img.naturalWidth === 0) markFailed();
    img.addEventListener('error', markFailed);
  });

  const revealItems = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealItems.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    // Items entering together fade in with a small stagger, so a section reads
    // top-to-bottom instead of popping as one block. The delay lives in CSS
    // (data-reveal-index) because the site's CSP disallows inline styles.
    const observer = new IntersectionObserver((entries) => {
      let step = 0;
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        if (step < 4) entry.target.setAttribute('data-reveal-index', String(step));
        entry.target.classList.add('is-visible');
        step += 1;
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  // The arithmetic block on the homepage: it only multiplies what the visitor
  // types and subtracts the checking time, so no invented savings claim is
  // attached to it. Without these values present, nothing here runs.
  const roi = document.querySelector('[data-roi]');
  if (roi) {
    const fields = ['roi-minutes', 'roi-runs', 'roi-check'].map((id) => document.getElementById(id));
    const hoursOut = roi.querySelector('[data-roi-hours]');
    const detailOut = roi.querySelector('[data-roi-detail]');
    if (fields.every(Boolean) && hoursOut && detailOut) {
      const recalc = () => {
        const value = (el) => {
          const raw = parseFloat(el.value);
          return Number.isFinite(raw) && raw > 0 ? raw : 0;
        };
        const perRun = Math.max(0, value(fields[0]) - value(fields[2]));
        const runs = value(fields[1]);
        const monthly = runs * 4.33;
        const hours = (perRun * monthly) / 60;
        hoursOut.textContent = hours >= 10 ? hours.toFixed(0) : hours.toFixed(1);
        detailOut.textContent = '\u00b7 ' + Math.round(monthly) + ' runs a month; ' +
          Math.round(perRun) + ' minutes of each one is off your hands';
      };
      fields.forEach((el) => el.addEventListener('input', recalc));
      recalc();
    }
  }

  // Consent-gated analytics (GA4). Disabled while GA_MEASUREMENT_ID is empty:
  // nothing is loaded, no banner is shown and no cookies are set.
  // To enable: set the ID (format G-XXXXXXXXXX), then add the Google domains to the
  // CSP in every page's <meta http-equiv="Content-Security-Policy"> and update the privacy policy.
  const GA_MEASUREMENT_ID = '';
  const CONSENT_KEY = 'orcamatic-analytics-consent';

  const loadAnalytics = () => {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_MEASUREMENT_ID);
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_MEASUREMENT_ID);
    document.head.appendChild(script);
  };

  const showConsentBanner = () => {
    if (document.querySelector('[data-consent-banner]')) return;
    const banner = document.createElement('div');
    banner.className = 'consent-banner';
    banner.setAttribute('data-consent-banner', '');
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Analytics consent');
    banner.innerHTML = '<p>We would like to measure visits to this site with Google Analytics. Cookies are only set if you accept. You can change your choice any time in the <a href="/privacy-policy/#analytics">privacy policy</a>.</p>' +
      '<div class="consent-actions"><button type="button" class="btn btn-secondary" data-consent="denied">Decline</button>' +
      '<button type="button" class="btn btn-primary" data-consent="granted">Accept</button></div>';
    banner.addEventListener('click', (event) => {
      const choice = event.target.getAttribute && event.target.getAttribute('data-consent');
      if (!choice) return;
      try { localStorage.setItem(CONSENT_KEY, choice); } catch (e) { /* storage unavailable */ }
      banner.remove();
      if (choice === 'granted') loadAnalytics();
    });
    document.body.appendChild(banner);
  };

  if (GA_MEASUREMENT_ID) {
    let stored = null;
    try { stored = localStorage.getItem(CONSENT_KEY); } catch (e) { stored = null; }
    if (stored === 'granted') loadAnalytics();
    else if (stored !== 'denied') showConsentBanner();
  }
})();
