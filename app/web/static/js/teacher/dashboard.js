document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.request-item button').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.request-item')?.classList.add('handled');
        });
    });
});
