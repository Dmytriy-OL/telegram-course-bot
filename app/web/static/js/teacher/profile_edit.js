const percent = 60; // 🔁 пізніше підтягну з бекенду

const fill = document.getElementById("progressFill");
const label = document.getElementById("progressPercent");
const publishBtn = document.getElementById("publishBtn");

fill.style.width = percent + "%";
label.innerText = percent + "%";

if (percent >= 80) {
    publishBtn.disabled = false;
    publishBtn.innerText = "🚀 Опублікувати профіль";
}
