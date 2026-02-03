document.addEventListener('DOMContentLoaded', function() {
    const updateTotals = () => {
        let grandTotal = 0;
        // Iterate through all inline rows (tabular inline uses .dynamic-orderitem_set)
        document.querySelectorAll('.tabular.inline-related tr.form-row').forEach(row => {
            const qty = parseFloat(row.querySelector('.field-quantity input')?.value) || 0;
            // Note: In a real app, you'd fetch the price via AJAX or data-attributes
            // For now, we assume price_at_purchase is visible or use a placeholder
            const price = parseFloat(row.querySelector('.field-price_at_purchase p')?.innerText) || 0;
            
            grandTotal += (qty * price);
        });

        // Update the 'Total Due' readonly field display
        const totalDisplay = document.querySelector('.field-total_due .readonly');
        if (totalDisplay) {
            totalDisplay.innerText = `$${grandTotal.toFixed(2)}`;
        }
    };

    // Listen for changes in the inline group
    document.querySelector('#orderitem_set-group').addEventListener('change', updateTotals);
});