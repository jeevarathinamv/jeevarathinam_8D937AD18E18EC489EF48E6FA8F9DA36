// College Digital Library Management Portal
// Client-side interactions & Form Validations

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Client-side file extension check for PDF upload inputs
    const pdfInputs = document.querySelectorAll('input[type="file"][accept*="pdf"]');
    pdfInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileName = file.name;
                const fileExt = fileName.split('.').pop().toLowerCase();
                if (fileExt !== 'pdf') {
                    alert('Invalid file format! Please upload a PDF file (.pdf).');
                    input.value = ''; // clear input
                }
            }
        });
    });
});
