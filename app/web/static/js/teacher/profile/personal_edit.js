// Елементи
const avatarInput = document.getElementById('avatar');
const avatarPreview = document.getElementById('avatarPreview');
const changeAvatarBtn = document.getElementById('changeAvatarBtn');

// Клік по кнопці "Змінити фото"
changeAvatarBtn.addEventListener('click', () => {
    avatarInput.click();
});

// Попередній перегляд аватару
avatarInput.addEventListener('change', () => {
    const file = avatarInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        avatarPreview.src = e.target.result;
    };
    reader.readAsDataURL(file);
});
