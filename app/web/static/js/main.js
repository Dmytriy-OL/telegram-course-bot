document.addEventListener('DOMContentLoaded', () => {
  // Просте появлення елементів при скролі
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

  // Просте відправлення контактної форми через fetch (порожня заглушка)
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = document.getElementById('contactFormMsg');
      msg.textContent = 'Відправляємо...';
      const formData = new FormData(contactForm);
      try {
        // Заміни URL на реальний endpoint у бекенді
        const res = await fetch(contactForm.action || '/contact_submit', {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          msg.textContent = 'Дякуємо! Ми зв’яжемося з вами найближчим часом.';
          contactForm.reset();
        } else {
          msg.textContent = 'Сталася помилка. Спробуйте ще раз.';
        }
      } catch (err) {
        msg.textContent = 'Помилка мережі. Перевірте підключення.';
      }
      setTimeout(()=> msg.textContent = '', 6000);
    });
  }
});
