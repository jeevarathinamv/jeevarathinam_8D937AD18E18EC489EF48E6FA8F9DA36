// Student Career Goal & Progress Tracker JS

document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss alert banners after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // Range slider real-time value display for Progress Percentage forms
  const progressSliders = document.querySelectorAll('.progress-range-input');
  progressSliders.forEach(function (slider) {
    const outputId = slider.getAttribute('data-output-target');
    const output = document.getElementById(outputId);
    if (output) {
      slider.addEventListener('input', function () {
        output.textContent = slider.value + '%';
      });
    }
  });

  // Client-side confirmation for deletions
  const deleteForms = document.querySelectorAll('.confirm-delete');
  deleteForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const itemName = form.getAttribute('data-item-name') || 'this item';
      if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  // Dynamic filter table search script
  const searchInput = document.getElementById('tableSearchInput');
  if (searchInput) {
    searchInput.addEventListener('keyup', function () {
      const filter = searchInput.value.toLowerCase();
      const rows = document.querySelectorAll('.searchable-table tbody tr');
      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        if (text.includes(filter)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
});
