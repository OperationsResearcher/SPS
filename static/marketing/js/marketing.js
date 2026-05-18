/* Kokpitim Marketing JS */
"use strict";

// ── Navbar scroll efekti ──────────────────────────────────────────────────────
const nav = document.getElementById("mk-nav");
if (nav) {
  window.addEventListener("scroll", () => {
    nav.classList.toggle("scrolled", window.scrollY > 50);
  }, { passive: true });
}

// ── Hamburger menü ────────────────────────────────────────────────────────────
const hamburger = document.getElementById("mk-hamburger");
const mobileMenu = document.getElementById("mk-mobile-menu");
if (hamburger && mobileMenu) {
  hamburger.addEventListener("click", () => {
    const open = mobileMenu.classList.toggle("open");
    hamburger.classList.toggle("open", open);
    hamburger.setAttribute("aria-expanded", open);
  });
}

// ── Accordion ─────────────────────────────────────────────────────────────────
document.querySelectorAll(".mk-acc-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const body = btn.nextElementSibling;
    const isOpen = body.classList.contains("open");
    document.querySelectorAll(".mk-acc-body").forEach(b => b.classList.remove("open"));
    if (!isOpen) body.classList.add("open");
  });
});

// ── Sayaç animasyonu ──────────────────────────────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const duration = 1500;
  const step = target / (duration / 16);
  let current = 0;
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      el.textContent = target.toLocaleString("tr-TR");
      clearInterval(timer);
    } else {
      el.textContent = Math.floor(current).toLocaleString("tr-TR");
    }
  }, 16);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting && !e.target.dataset.counted) {
      e.target.dataset.counted = "1";
      animateCounter(e.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll(".mk-stat-num[data-target]").forEach(el => {
  counterObserver.observe(el);
});

// ── Scroll fade-in ────────────────────────────────────────────────────────────
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add("visible");
      fadeObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll(".fade-in").forEach(el => fadeObserver.observe(el));

// ── Form validasyon ───────────────────────────────────────────────────────────
document.querySelectorAll(".mk-form").forEach(form => {
  form.addEventListener("submit", e => {
    const required = form.querySelectorAll("[required]");
    let valid = true;
    required.forEach(field => {
      field.style.borderColor = "";
      if (!field.value.trim()) {
        field.style.borderColor = "#ef4444";
        valid = false;
      }
    });
    if (!valid) {
      e.preventDefault();
      if (typeof Swal !== "undefined") {
        Swal.fire({
          toast: true, position: "top-end", icon: "warning",
          title: "Lütfen zorunlu alanları doldurun.",
          showConfirmButton: false, timer: 3000
        });
      }
    }
  });
});

// ── Dropdown JS kontrolü (CSS hover yerine) ──────────────────────────────────
document.querySelectorAll(".mk-dropdown").forEach(function(dropdown) {
  var menu = dropdown.querySelector(".mk-dropdown-menu");
  var btn  = dropdown.querySelector(".mk-dropdown-btn");
  var timer = null;

  function openMenu() {
    clearTimeout(timer);
    menu.classList.add("open");
    dropdown.classList.add("open");
    if (btn) btn.setAttribute("aria-expanded", "true");
  }
  function closeMenu() {
    timer = setTimeout(function() {
      menu.classList.remove("open");
      dropdown.classList.remove("open");
      if (btn) btn.setAttribute("aria-expanded", "false");
    }, 120);
  }

  dropdown.addEventListener("mouseenter", openMenu);
  dropdown.addEventListener("mouseleave", closeMenu);
  menu.addEventListener("mouseenter", openMenu);
  menu.addEventListener("mouseleave", closeMenu);

  // Tıklama ile de aç/kapat
  if (btn) {
    btn.addEventListener("click", function(e) {
      e.stopPropagation();
      if (menu.classList.contains("open")) { closeMenu(); } else { openMenu(); }
    });
  }
});

// Dışarı tıklayınca kapat
document.addEventListener("click", function() {
  document.querySelectorAll(".mk-dropdown-menu.open").forEach(function(m) {
    m.classList.remove("open");
    m.closest(".mk-dropdown").classList.remove("open");
  });
});
