// College Academic Calendar Management System - JavaScript Helpers

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Form date validation for Add / Edit Event forms
    const eventForm = document.querySelector('#eventForm');
    if (eventForm) {
        const startDateInput = document.querySelector('#start_date');
        const endDateInput = document.querySelector('#end_date');

        if (startDateInput && endDateInput) {
            startDateInput.addEventListener('change', function () {
                if (endDateInput.value && endDateInput.value < startDateInput.value) {
                    endDateInput.value = startDateInput.value;
                }
                endDateInput.min = startDateInput.value;
            });
        }
    }
});
