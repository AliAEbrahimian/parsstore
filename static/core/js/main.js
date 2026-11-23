/* ParsStore - lightweight interactive behaviour */
(function () {
  "use strict";

/* ------------------------------------------------ mobile menu */
  var header = document.getElementById("site-header");
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");

  if (toggle && nav) {
    var closeNav = function () {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeNav();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        closeNav();
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1200) closeNav();
    });
  }

/* ------------------------------------------------ header shadow on scroll */
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 10);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

/* ------------------------------------------------ reveal sections on scroll */
  var reveals = document.querySelectorAll(".reveal");
  var reduceMotion = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
    : false;

  if (!reduceMotion && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var group = el.parentElement ? el.parentElement.querySelectorAll(".reveal") : [];
          var index = Array.prototype.indexOf.call(group, el);
          el.style.transitionDelay = (index > 0 ? Math.min(index, 4) * 70 : 0) + "ms";
          el.classList.add("is-visible");
          observer.unobserve(el);
          window.setTimeout(function () {
            el.classList.remove("reveal", "is-visible");
            el.style.transitionDelay = "";
          }, 1100);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );

    reveals.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    reveals.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

/* ------------------------------------------------ prefill inquiry message */
  document.addEventListener("click", function (event) {
    var trigger = event.target.closest ? event.target.closest("[data-inquire]") : null;
    if (!trigger) return;

    var field = document.getElementById("id_message");
    if (!field || field.value.trim()) return;

    var template = document.body.getAttribute("data-inquire-template") || "{name}";
    field.value = template.replace("{name}", trigger.getAttribute("data-inquire") || "");
    field.dispatchEvent(new Event("input", { bubbles: true }));
  });

/* ------------------------------------------------ top-of-page messages */
  document.querySelectorAll("[data-flash]").forEach(function (flash) {
    var closeBtn = flash.querySelector(".flash-close");
    var hidden = false;
    var timer = window.setTimeout(hide, 7000);
    function hide() {
      if (hidden) return;
      hidden = true;
      window.clearTimeout(timer);
      flash.style.transition = "opacity .3s ease, transform .3s ease";
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      window.setTimeout(function () {
        flash.remove();
      }, 320);
    }

    if (closeBtn) closeBtn.addEventListener("click", hide);
  });
})();
