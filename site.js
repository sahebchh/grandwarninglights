document.addEventListener("DOMContentLoaded", function () {
  function updateHeaderOffset() {
    var infoBar = document.querySelector('body > div[style*="position:fixed"][style*="top:0"]');
    var nav = document.querySelector("nav");
    var total = 0;

    if (infoBar) total += infoBar.offsetHeight;
    if (nav) total += nav.offsetHeight;

    if (total > 0) {
      document.documentElement.style.setProperty("--header-offset", total + "px");
    }
  }

  function syncHamburgerState(button) {
    var menuId = button.getAttribute("aria-controls");
    if (!menuId) return;
    var menu = document.getElementById(menuId);
    if (!menu) return;
    button.setAttribute("aria-expanded", menu.classList.contains("open") ? "true" : "false");
  }

  var hamburgerButtons = document.querySelectorAll(".hamburger[aria-controls]");
  updateHeaderOffset();
  hamburgerButtons.forEach(function (button) {
    syncHamburgerState(button);
    button.addEventListener("click", function () {
      // Let existing inline toggle handlers run first.
      window.requestAnimationFrame(function () {
        syncHamburgerState(button);
      });
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".mobile-menu.open").forEach(function (menu) {
      menu.classList.remove("open");
    });
    hamburgerButtons.forEach(syncHamburgerState);
  });

  document.querySelectorAll(".mobile-menu a").forEach(function (link) {
    link.addEventListener("click", function () {
      var menu = link.closest(".mobile-menu");
      if (!menu) return;
      menu.classList.remove("open");
      var id = menu.getAttribute("id");
      if (!id) return;
      var trigger = document.querySelector('.hamburger[aria-controls="' + id + '"]');
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  });

  // Security hardening for links that open a new tab.
  document.querySelectorAll('a[target="_blank"]').forEach(function (link) {
    var rel = (link.getAttribute("rel") || "").toLowerCase();
    var relParts = rel.split(/\s+/).filter(Boolean);
    if (relParts.indexOf("noopener") === -1) relParts.push("noopener");
    if (relParts.indexOf("noreferrer") === -1) relParts.push("noreferrer");
    link.setAttribute("rel", relParts.join(" "));
  });

  // Light performance enhancement for non-critical media.
  document.querySelectorAll("img").forEach(function (img) {
    if (!img.hasAttribute("decoding")) {
      img.setAttribute("decoding", "async");
    }
    if (
      img.closest("nav") ||
      img.closest(".hero") ||
      img.closest(".amb-hero") ||
      img.closest(".products-hero") ||
      img.closest(".heritage-hero") ||
      img.closest(".exh-hero")
    ) {
      return;
    }
    if (!img.hasAttribute("loading")) {
      img.setAttribute("loading", "lazy");
    }
  });

  window.addEventListener("resize", updateHeaderOffset);
  window.addEventListener("load", updateHeaderOffset);
});
