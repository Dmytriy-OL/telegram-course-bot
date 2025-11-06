document.addEventListener('DOMContentLoaded', () => {

  /* --- Анімація появи елементів --- */
  const appearElems = document.querySelectorAll('.course-card, .teacher-card, .adv-card, .test, .feature-item');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.transition = 'transform 0.6s cubic-bezier(.2,.9,.2,1), opacity 0.6s';
        entry.target.style.transform = 'translateY(0)';
        entry.target.style.opacity = '1';
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  appearElems.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    io.observe(el);
  });

  /* --- Відправка форми --- */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = document.getElementById('contactFormMsg');
      msg.textContent = 'Відправляємо...';
      const formData = new FormData(contactForm);
      try {
        const res = await fetch(contactForm.action || '/contact_submit', {
          method: 'POST',
          body: formData
        });
        msg.textContent = res.ok
          ? 'Дякуємо! Ми зв’яжемося з вами.'
          : 'Сталася помилка. Спробуйте ще раз.';
        if (res.ok) contactForm.reset();
      } catch {
        msg.textContent = 'Помилка мережі.';
      }
      setTimeout(()=> msg.textContent = '', 6000);
    });
  }

  /* --- Меню користувача по кліку --- */
  const dropBtn = document.querySelector(".dropbtn");
  const dropMenu = document.querySelector(".dropdown-content");

  if (dropBtn && dropMenu) {
    dropBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dropMenu.classList.toggle("show");
    });

    document.addEventListener("click", () => {
      dropMenu.classList.remove("show");
    });
  }

});
const sidebar = document.getElementById("sidebar");
const openSidebar = document.getElementById("openSidebar");
const closeSidebar = document.getElementById("closeSidebar");

if (openSidebar && closeSidebar && sidebar) {
  openSidebar.addEventListener("click", () => sidebar.classList.add("open"));
  closeSidebar.addEventListener("click", () => sidebar.classList.remove("open"));
}