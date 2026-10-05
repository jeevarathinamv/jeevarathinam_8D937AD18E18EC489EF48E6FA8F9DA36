// JavaScript for College Digital Document Verification System

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Simple file input extension checker on client side
    const fileInput = document.getElementById('document_file');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const filePath = fileInput.value;
            const allowedExtensions = /(\.pdf|\.jpg|\.jpeg|\.png)$/i;
            if (filePath && !allowedExtensions.exec(filePath)) {
                alert('Invalid file format! Please select a PDF, JPG, or PNG file.');
                fileInput.value = '';
            }
        });
    }
});
