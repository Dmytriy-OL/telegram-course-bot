const steps = document.querySelectorAll(".step");
const nextBtns = document.querySelectorAll(".next");
const prevBtns = document.querySelectorAll(".prev");
const progress = document.getElementById("progress-fill");
const indicator = document.getElementById("step-indicator");

let current = 0;

function updateStep() {
    steps.forEach((s, i) => s.classList.toggle("active", i === current));
    progress.style.width = `${((current + 1) / steps.length) * 100}%`;
    indicator.textContent = `Крок ${current + 1} з ${steps.length}`;

    // Кнопка "Далі" → "Надіслати заявку" на останньому кроці
    nextBtns.forEach(btn => {
        btn.textContent = current === steps.length - 1 ? "Надіслати заявку" : "Далі";
    });
}

nextBtns.forEach(btn =>
    btn.addEventListener("click", e => {
        e.preventDefault();
        if (current < steps.length - 1) {
            current++;
            updateStep();
        } else {
            // якщо останній крок, відправляємо форму
            btn.closest("form").submit();
        }
    })
);

prevBtns.forEach(btn =>
    btn.addEventListener("click", e => {
        e.preventDefault();
        if (current > 0) {
            current--;
            updateStep();
        }
    })
);

updateStep();
