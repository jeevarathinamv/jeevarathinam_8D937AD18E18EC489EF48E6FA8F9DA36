// Business Supplier & Purchase Management System JavaScript

document.addEventListener('DOMContentLoaded', function () {

    // Dynamic Calculation for Purchase Form
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('purchase_price');
    const totalAmountInput = document.getElementById('total_amount');
    const totalAmountDisplay = document.getElementById('total_amount_display');
    const productSelect = document.getElementById('product_id');

    function calculateTotal() {
        if (!quantityInput || !priceInput) return;

        const qty = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = (qty * price).toFixed(2);

        if (totalAmountInput) {
            totalAmountInput.value = total;
        }

        if (totalAmountDisplay) {
            totalAmountDisplay.textContent = '₹' + parseFloat(total).toLocaleString('en-IN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    }

    if (quantityInput) {
        quantityInput.addEventListener('input', calculateTotal);
    }

    if (priceInput) {
        priceInput.addEventListener('input', calculateTotal);
    }

    // Product selection auto-populates default price
    if (productSelect && priceInput) {
        productSelect.addEventListener('change', function () {
            const selectedOption = productSelect.options[productSelect.selectedIndex];
            const defaultPrice = selectedOption.getAttribute('data-price');
            if (defaultPrice) {
                priceInput.value = parseFloat(defaultPrice).toFixed(2);
                calculateTotal();
            }
        });
    }

    // Initial total calculation on load
    calculateTotal();

    // Confirm Delete Dialogs
    const deleteForms = document.querySelectorAll('.delete-confirm-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const itemName = this.getAttribute('data-item-name') || 'this item';
            if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });

    // Auto-dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});
