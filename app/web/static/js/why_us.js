// app/web/static/js/why_us.js
(() => {
  // Працюємо лише після готовності DOM
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    const modal   = document.getElementById("testInfoModal");
    const openBtn = document.getElementById("testInfoBtn");
    if (!modal || !openBtn) return; // тихо виходимо, якщо елементів немає

    const backdrop   = modal.querySelector(".modal__backdrop");
    const closeNodes = modal.querySelectorAll("[data-close-modal]");
    const root       = document.documentElement;

    function openModal() {
      modal.setAttribute("aria-hidden", "false");
      root.classList.add("no-scroll");
      // спробуємо поставити фокус на перший фокусований елемент
      const firstFocusable = modal.querySelector(
        'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus?.();
    }

    function closeModal() {
      modal.setAttribute("aria-hidden", "true");
      root.classList.remove("no-scroll");
      openBtn.focus?.();
    }

    openBtn.addEventListener("click", openModal);
    backdrop?.addEventListener("click", closeModal);
    closeNodes.forEach((el) => el.addEventListener("click", closeModal));

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.getAttribute("aria-hidden") === "false") {
        closeModal();
      }
    });
  }
})();
