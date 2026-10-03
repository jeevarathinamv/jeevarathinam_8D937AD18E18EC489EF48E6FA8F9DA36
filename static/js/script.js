// JavaScript functionality for College Library Book Issue & Return System

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Client-side quick filter for tables if table has data-table-filter attribute
    const searchInputs = document.querySelectorAll('.table-search-input');
    searchInputs.forEach(function (input) {
        input.addEventListener('keyup', function () {
            const filterValue = this.value.toLowerCase();
            const targetTableId = this.getAttribute('data-target-table');
            const targetTable = document.getElementById(targetTableId);

            if (targetTable) {
                const rows = targetTable.querySelectorAll('tbody tr');
                rows.forEach(function (row) {
                    const rowText = row.textContent.toLowerCase();
                    if (rowText.includes(filterValue)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Confirmation dialogs for deletion actions
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete-form');
    confirmDeleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('data-confirm-message') || 'Are you sure you want to perform this action?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
