// JavaScript for College Canteen Feedback & Complaint System

document.addEventListener('DOMContentLoaded', function () {
    // Live update for Star Rating Selectors
    const ratingSelects = document.querySelectorAll('.rating-select');
    ratingSelects.forEach(function (select) {
        select.addEventListener('change', function () {
            const targetId = this.getAttribute('data-target');
            const targetBadge = document.getElementById(targetId);
            if (targetBadge) {
                targetBadge.textContent = this.value + ' Stars';
            }
        });
    });

    // Bootstrap Form Validation Enable
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});
