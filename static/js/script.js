// Lab Computer Fault Reporting System JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auto dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirmation dialog for delete actions
    const deleteButtons = document.querySelectorAll('.btn-confirm-delete');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm-message') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Optional Lab to Computer mapping helper for report_fault form
    const labSelect = document.getElementById('lab_name');
    const compSelect = document.getElementById('computer_number');

    if (labSelect && compSelect) {
        labSelect.addEventListener('change', function () {
            const selectedLab = this.value;
            const options = compSelect.querySelectorAll('option');

            options.forEach(function (option) {
                if (!option.value) return; // Keep placeholder option
                const optionLab = option.getAttribute('data-lab');
                if (!selectedLab || !optionLab || optionLab === selectedLab) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    }
});
