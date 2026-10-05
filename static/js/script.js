// JavaScript for Library Book Fine Management System

document.addEventListener('DOMContentLoaded', function () {

    // Form validation check for all forms with class 'needs-validation'
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

    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Automatically fill dates in issue book form if present
    const issueDateInput = document.getElementById('issue_date');
    const dueDateInput = document.getElementById('due_date');

    if (issueDateInput && !issueDateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        issueDateInput.value = today;

        // Default due date = 14 days from today
        const defaultDue = new Date();
        defaultDue.setDate(defaultDue.getDate() + 14);
        if (dueDateInput && !dueDateInput.value) {
            dueDateInput.value = defaultDue.toISOString().split('T')[0];
        }
    }

    // Dynamic Late Days and Fine preview in Return Book form
    const returnDateInput = document.getElementById('return_date');
    const selectedDueDateElem = document.getElementById('selected_due_date');
    const calculatedLateDaysElem = document.getElementById('calculated_late_days');
    const calculatedFineElem = document.getElementById('calculated_fine');

    function calculateReturnFinePreview() {
        if (!returnDateInput || !selectedDueDateElem || !calculatedLateDaysElem || !calculatedFineElem) return;

        const returnVal = returnDateInput.value;
        const dueVal = selectedDueDateElem.dataset.dueDate;

        if (returnVal && dueVal) {
            const returnDate = new Date(returnVal);
            const dueDate = new Date(dueVal);

            const diffTime = returnDate - dueDate;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            const lateDays = Math.max(0, diffDays);
            const fine = lateDays * 5;

            calculatedLateDaysElem.textContent = lateDays + ' day(s)';
            calculatedFineElem.textContent = '₹' + fine.toFixed(2);
        }
    }

    if (returnDateInput) {
        returnDateInput.addEventListener('change', calculateReturnFinePreview);
        calculateReturnFinePreview();
    }
});
