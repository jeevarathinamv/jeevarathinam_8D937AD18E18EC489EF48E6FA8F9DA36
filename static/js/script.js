// Custom JavaScript for College Attendance System

document.addEventListener('DOMContentLoaded', function () {
  // Search filter helper for tables
  const searchInputs = document.querySelectorAll('.table-search');
  searchInputs.forEach(input => {
    input.addEventListener('keyup', function () {
      const filter = this.value.toLowerCase();
      const targetTableId = this.getAttribute('data-table');
      const table = document.getElementById(targetTableId);
      if (!table) return;

      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.indexOf(filter) > -1 ? '' : 'none';
      });
    });
  });

  // Mark All Present / Mark All Absent helper
  const markAllPresentBtn = document.getElementById('btnMarkAllPresent');
  const markAllAbsentBtn = document.getElementById('btnMarkAllAbsent');

  if (markAllPresentBtn) {
    markAllPresentBtn.addEventListener('click', function () {
      const presentRadios = document.querySelectorAll('input[type="radio"][value="Present"]');
      presentRadios.forEach(radio => radio.checked = true);
    });
  }

  if (markAllAbsentBtn) {
    markAllAbsentBtn.addEventListener('click', function () {
      const absentRadios = document.querySelectorAll('input[type="radio"][value="Absent"]');
      absentRadios.forEach(radio => radio.checked = true);
    });
  }
});
