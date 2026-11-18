/* پارس تکستایل — انتخاب تم (تاریک / روشن / خودکار)
   این فایل عمداً در <head> و به‌صورت همگام بارگذاری می‌شود تا پیش از
   نخستین رنگ‌آمیزی صفحه، تم ذخیره‌شده روی <html> اعمال شود و پرش رنگ (FOUC) رخ ندهد.
   هیچ کد inline ندارد تا با CSP سخت‌گیرانهٔ پروژه سازگار بماند. */
(function () {
  "use strict";

  var STORAGE_KEY = "parstextile.theme";
  var MODES = ["dark", "light", "auto"];
  var root = document.documentElement;

  var systemLight = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: light)")
    : null;

  function readMode() {
    try {
      var stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored && MODES.indexOf(stored) !== -1) return stored;
    } catch (error) {
      /* دسترسی به localStorage ممکن است در حالت خصوصی مسدود باشد */
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

  /* گذار کوتاه رنگ‌ها فقط هنگام انتخاب دستی کاربر */
  function fadeTheme() {
    root.classList.add("theme-fade");
    /* خواندن یک ویژگی، مرورگر را به بازچینش وامی‌دارد تا گذار از رنگ فعلی شروع شود */
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
        /* ذخیره‌نشدن تم نباید باعث خطا شود */
      }
    }
  }

  /* اعمال فوری پیش از رندر شدن body */
  applyMode(readMode(), false);

  /* یک کلیک مشترک برای همهٔ کلیدهای تم (دسکتاپ و منوی موبایل) */
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
