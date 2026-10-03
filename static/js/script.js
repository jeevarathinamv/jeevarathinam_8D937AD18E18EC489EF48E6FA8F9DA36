// Client-side JavaScript helpers for Student Assignment Submission & Deadline Tracker

document.addEventListener('DOMContentLoaded', function () {
    // Enable Bootstrap tooltips if any are present
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form confirmation for deletion actions
    const deleteForms = document.querySelectorAll('.delete-confirm-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const confirmed = confirm('Are you sure you want to delete this assignment? This action cannot be undone.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
