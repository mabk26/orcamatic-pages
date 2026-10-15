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

  const revealItems = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealItems.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }
})();
