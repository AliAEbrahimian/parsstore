/* ParsStore - theme switcher (dark / light / auto)
This file is intentionally loaded synchronously in <head> so the saved theme is
applied to <html> before the first paint and no colour flash (FOUC) occurs.
It contains no inline code, keeping the strict Content-Security-Policy intact. */
(function () {
  "use strict";

  var STORAGE_KEY = "parsstore.theme";
  var MODES = ["dark", "light", "auto"];
  var root = document.documentElement;

  var systemLight = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: light)")
    : null;

/* Add js-ready before the first paint so .reveal elements start hidden and
   appear after the page loads (prevents FOUC). */
  if (!systemLight || !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    root.classList.add("js-ready");
  }

  function readMode() {
    try {
      var stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored && MODES.indexOf(stored) !== -1) return stored;
    } catch (error) {
/* localStorage access may be blocked in private mode */
    }
    return "auto";
  }

  function resolveMode(mode) {
    if (mode === "auto") {
      return systemLight && systemLight.matches ? "light" : "dark";
    }
    return mode;
  }

  function syncButtons(mode) {
    var buttons = document.querySelectorAll("[data-theme-choice]");
    for (var i = 0; i < buttons.length; i += 1) {
      var isActive = buttons[i].getAttribute("data-theme-choice") === mode;
      buttons[i].setAttribute("aria-pressed", isActive ? "true" : "false");
    }
  }

  var fadeTimer = null;

/* Short colour transition only for manual theme choices */
  function fadeTheme() {
    root.classList.add("theme-fade");
/* Reading a property forces a reflow so the transition starts from the current colour */
    void root.offsetWidth;
    if (fadeTimer) window.clearTimeout(fadeTimer);
    fadeTimer = window.setTimeout(function () {
      root.classList.remove("theme-fade");
    }, 320);
  }

  function updateMeta(resolved) {
    var meta = document.getElementById("theme-color-meta");
    if (meta) {
      meta.setAttribute("content", resolved === "light" ? "#f6f3ee" : "#080b0e");
    }
  }

  function applyMode(mode, persist) {
    var resolved = resolveMode(mode);
    root.setAttribute("data-theme", resolved);
    root.setAttribute("data-theme-mode", mode);
    updateMeta(resolved);
    syncButtons(mode);
    if (persist) {
      try {
        window.localStorage.setItem(STORAGE_KEY, mode);
      } catch (error) {
/* Failing to save the theme must not cause an error */
      }
    }
  }

/* Apply immediately, before the body is rendered */
  applyMode(readMode(), false);

/* One shared click handler for all theme buttons (desktop and mobile menu) */
  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    var button = target.closest("[data-theme-choice]");
    if (!button) return;
    fadeTheme();
    applyMode(button.getAttribute("data-theme-choice"), true);
  });

  document.addEventListener("DOMContentLoaded", function () {
    syncButtons(readMode());
  });

  function onSystemChange() {
    if (readMode() === "auto") applyMode("auto", false);
  }

  if (systemLight) {
    if (systemLight.addEventListener) {
      systemLight.addEventListener("change", onSystemChange);
    } else if (systemLight.addListener) {
      systemLight.addListener(onSystemChange);
    }
  }
})();
