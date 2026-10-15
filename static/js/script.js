// College Attendance & Internal Mark Management System JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar Toggle Functionality
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapse = document.getElementById('sidebarCollapse');

    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }

    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Mark All Present / Mark All Absent Utility in Attendance Marking
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');
    const markAllAbsentBtn = document.getElementById('markAllAbsentBtn');

    if (markAllPresentBtn) {
        markAllPresentBtn.addEventListener('click', function () {
            const radioPresent = document.querySelectorAll('input[type="radio"][value="Present"]');
            radioPresent.forEach(radio => radio.checked = true);
        });
    }

    if (markAllAbsentBtn) {
        markAllAbsentBtn.addEventListener('click', function () {
            const radioAbsent = document.querySelectorAll('input[type="radio"][value="Absent"]');
            radioAbsent.forEach(radio => radio.checked = true);
        });
    }

    // Live Search Filter for Tables
    const searchInputs = document.querySelectorAll('.table-search-input');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function () {
            const targetTableId = this.getAttribute('data-table');
            const targetTable = document.getElementById(targetTableId);
            if (!targetTable) return;

            const filterValue = this.value.toLowerCase();
            const rows = targetTable.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
});
