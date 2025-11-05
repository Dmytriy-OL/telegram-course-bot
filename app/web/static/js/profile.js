document.addEventListener("DOMContentLoaded", () => {
    const avatarInput = document.getElementById("avatar");
    const avatarImg = document.querySelector(".avatar");

    if (!avatarInput || !avatarImg) return;

    avatarInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                avatarImg.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});
