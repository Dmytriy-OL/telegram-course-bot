document.addEventListener("DOMContentLoaded", () => {

    /* ========= ПРЕВ'Ю АВАТАРА ========= */
    const avatarInput = document.getElementById("avatarInput");

    if (avatarInput) {
        avatarInput.addEventListener("change", () => {
            const file = avatarInput.files[0];
            if (!file) return;

            const preview = document.querySelector(".profile-avatar");
            if (preview) {
                preview.src = URL.createObjectURL(file);
            }
        });
    }

    /* ========= ЗАБУЛИ ПАРОЛЬ ========= */
    const forgotBtn = document.getElementById("forgotPasswordBtn");
    const successMsg = document.getElementById("forgotSuccessMessage");

    if (!forgotBtn || !successMsg) {
        console.warn("Кнопка або повідомлення не знайдені");
        return;
    }

    forgotBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        // ✅ Миттєвий показ повідомлення
        successMsg.style.display = "block";
        successMsg.style.opacity = "1";
        successMsg.classList.add("show");

        // ✅ Плавне зникнення
        setTimeout(() => {
            successMsg.classList.remove("show");
            successMsg.style.opacity = "0";
        }, 10000);

        setTimeout(() => {
            successMsg.style.display = "none";
            successMsg.style.opacity = "1";
        }, 11000);

        // ✅ Відправка email у фоні
        try {
            const response = await fetch("/settings/forgot-password", {
                method: "POST"
            });

            if (!response.ok) {
                console.error("Сервер повернув помилку");
            }

        } catch (error) {
            console.error("Помилка:", error);
        }
    });

});
