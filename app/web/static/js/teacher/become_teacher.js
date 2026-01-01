const steps = document.querySelectorAll(".step");
const nextBtns = document.querySelectorAll(".next");
const prevBtns = document.querySelectorAll(".prev");
const progress = document.getElementById("progress-fill");
const indicator = document.getElementById("step-indicator");

let current = 0;

function updateStep() {
    steps.forEach((s, i) => s.classList.toggle("active", i === current));
    progress.style.width = `${(current + 1) * 33}%`;
    indicator.textContent = `Крок ${current + 1} з 3`;
}

nextBtns.forEach(btn =>
    btn.addEventListener("click", () => {
        if (current < steps.length - 1) {
            current++;
            updateStep();
        }
    })
);

prevBtns.forEach(btn =>
    btn.addEventListener("click", () => {
        if (current > 0) {
            current--;
            updateStep();
        }
    })
);

// accordion
document.querySelector(".accordion-toggle")
    .addEventListener("click", () => {
        document.querySelector(".accordion").classList.toggle("open");
        document.querySelector(".accordion").style.display =
            document.querySelector(".accordion").classList.contains("open")
                ? "block"
                : "none";
    });
