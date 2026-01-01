document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector(".toggle-socials");
    const content = document.querySelector(".socials-content");

    btn.addEventListener("click", () => {
        const visible = content.style.display === "block";
        content.style.display = visible ? "none" : "block";
        btn.textContent = visible
            ? "Соцмережі (за бажанням) ⯈"
            : "Соцмережі (за бажанням) ⯆";
    });
});
