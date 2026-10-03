// Student Skill Workshop Management Portal - Client JS

document.addEventListener('DOMContentLoaded', function () {
    // Auto-hide alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form Bootstrap validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Confirm deletion
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            const name = this.getAttribute('data-name') || 'this item';
            if (!confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
});
