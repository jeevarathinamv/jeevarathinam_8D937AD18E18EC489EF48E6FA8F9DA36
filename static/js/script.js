/* Custom JavaScript for Library New Book Request System */

document.addEventListener('DOMContentLoaded', function () {
    // Form validation check for HTML forms with needs-validation class
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

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Helper function to insert pre-made admin remark templates into modal remark textareas
function setAdminRemark(modalId, remarkText) {
    const textarea = document.querySelector(`#${modalId} textarea[name="admin_remarks"]`);
    if (textarea) {
        textarea.value = remarkText;
    }
}
