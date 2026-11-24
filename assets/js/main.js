// ============================================================
// THE AFRO PROJECT — Main JavaScript
// ============================================================

(function () {
  'use strict';

  // ---------- MOBILE NAVIGATION ----------
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen);
      navToggle.textContent = isOpen ? '✕' : '☰';
    });

    // Close on link click (mobile)
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 900) {
          navLinks.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.textContent = '☰';
        }
      });
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.textContent = '☰';
      }
    });
  }

  // ---------- ACTIVE NAV HIGHLIGHT ----------
  const currentPath = window.location.pathname;
  const currentPage = currentPath.split('/').pop().replace('.html', '') || 'home';

  document.querySelectorAll('[data-page]').forEach(function (link) {
    const page = link.getAttribute('data-page');
    if (page === currentPage ||
        (currentPage === 'home' && page === 'home') ||
        (currentPath.includes('blog/') && page === 'blog')) {
      link.classList.add('active');
    }
  });

  // ---------- SMOOTH SCROLL FOR ANCHORS ----------
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ---------- FADE-IN ON SCROLL ----------
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-up');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.stat-card, .card, .post-card').forEach(function (el) {
      observer.observe(el);
    });
  }

  // ---------- COPY-TO-CLIPBOARD FOR CODE BLOCKS ----------
  document.querySelectorAll('pre').forEach(function (pre) {
    const button = document.createElement('button');
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.style.cssText = 'position:absolute;top:8px;right:8px;padding:4px 10px;font-size:0.75rem;background:rgba(245,179,66,0.15);color:#f5b342;border:1px solid rgba(245,179,66,0.3);border-radius:4px;cursor:pointer;font-family:Inter,sans-serif;';

    button.addEventListener('click', function () {
      const code = pre.querySelector('code') || pre;
      navigator.clipboard.writeText(code.textContent).then(function () {
        button.textContent = 'Copied!';
        setTimeout(function () { button.textContent = 'Copy'; }, 1500);
      });
    });

    pre.style.position = 'relative';
    pre.appendChild(button);
  });

  // ---------- NEWSLETTER FORM (Formspree) ----------
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const input = newsletterForm.querySelector('input[type="email"]');
      if (input && input.value) {
        input.value = '';
        const button = newsletterForm.querySelector('button');
        if (button) {
          button.textContent = '✓ Subscribed';
          setTimeout(function () { button.textContent = 'Subscribe'; }, 2500);
        }
      }
    });
  }

})();