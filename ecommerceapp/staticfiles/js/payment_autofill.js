document.addEventListener('DOMContentLoaded', function () {
    const orderSelect = document.querySelector('#id_order');
    const amountInput = document.querySelector('#id_amount');

    if (orderSelect && amountInput) {
        orderSelect.addEventListener('change', function () {
            const orderId = this.value;
            if (!orderId) return;

            // Fetch order total_due via AJAX
            fetch(`/admin/get_order_total/${orderId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.total_due !== undefined) {
                        amountInput.value = data.total_due;
                    }
                })
                .catch(err => console.error('Error fetching order total:', err));
        });
    }
});
