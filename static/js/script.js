// JavaScript helper functions for Student Project Showcase Portal

document.addEventListener('DOMContentLoaded', function () {
    // Image Upload Preview logic
    const imageInput = document.getElementById('project_image');
    const imagePreview = document.getElementById('image_preview');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Client-side quick filter on My Projects or Showcase tables if needed
    const clientSearchInput = document.getElementById('clientSearchInput');
    if (clientSearchInput) {
        clientSearchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            const projectCards = document.querySelectorAll('.project-card-item');

            projectCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(filter)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});
