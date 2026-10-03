// Client-side interactions for Small Business Sales & Customer Management System

document.addEventListener('DOMContentLoaded', function () {
    // Enable Bootstrap tooltips if present
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-calculate Item Total and Grand Total on Sale Form
    var productSelect = document.getElementById('product_id');
    var quantityInput = document.getElementById('quantity');
    var priceInput = document.getElementById('selling_price');
    var discountInput = document.getElementById('discount');
    var stockBadge = document.getElementById('available_stock_badge');
    var subtotalDisplay = document.getElementById('subtotal_display');
    var grandTotalDisplay = document.getElementById('grand_total_display');

    function updateCalculations() {
        if (!productSelect || !quantityInput || !priceInput || !discountInput) return;

        var selectedOption = productSelect.options[productSelect.selectedIndex];
        if (selectedOption && selectedOption.dataset) {
            var defaultPrice = parseFloat(selectedOption.dataset.price || 0);
            var stock = parseInt(selectedOption.dataset.stock || 0);

            // If price hasn't been set or product changed, default price can be filled
            if (productSelect.dataset.lastSelected !== productSelect.value) {
                priceInput.value = defaultPrice.toFixed(2);
                productSelect.dataset.lastSelected = productSelect.value;
            }

            if (stockBadge) {
                stockBadge.textContent = 'Available Stock: ' + stock;
                if (stock <= 0) {
                    stockBadge.className = 'badge bg-danger';
                } else if (stock <= 5) {
                    stockBadge.className = 'badge bg-warning text-dark';
                } else {
                    stockBadge.className = 'badge bg-success';
                }
            }
        }

        var qty = parseInt(quantityInput.value) || 0;
        var unitPrice = parseFloat(priceInput.value) || 0;
        var discount = parseFloat(discountInput.value) || 0;

        var subtotal = qty * unitPrice;
        var grandTotal = Math.max(0, subtotal - discount);

        if (subtotalDisplay) subtotalDisplay.textContent = '₹' + subtotal.toFixed(2);
        if (grandTotalDisplay) grandTotalDisplay.textContent = '₹' + grandTotal.toFixed(2);
    }

    if (productSelect) {
        productSelect.addEventListener('change', updateCalculations);
    }
    if (quantityInput) {
        quantityInput.addEventListener('input', updateCalculations);
    }
    if (priceInput) {
        priceInput.addEventListener('input', updateCalculations);
    }
    if (discountInput) {
        discountInput.addEventListener('input', updateCalculations);
    }

    // Trigger calculation initially if form elements exist
    if (productSelect) {
        updateCalculations();
    }
});
