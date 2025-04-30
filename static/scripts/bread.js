const API_ENDPOINT = window.location.href + '/inventory';

// State
let breads = [];
let orderItems = {};
let totalPrice = 0;

// Fetch breads data
async function fetchBreads() {
    try {
        const response = await fetch(API_ENDPOINT);
        const data = await response.json();

        // Transform the data to a more usable format
        // Format: [id, type_id, name, price, currency, available]
        const formattedData = data.map(item => ({
            id: item[0],
            typeId: item[1],
            name: item[2],
            price: parseFloat(item[3]),
            currency: item[4],
            available: item[5]
        }));

        return formattedData;
    } catch (error) {
        console.error('Error fetching breads:', error);
        document.getElementById('bread-container').innerHTML = `<div class="error-message">${languageValues["module_bread_error_loading"]}</div>`;
        return [];
    }
}

// Format price with currency
function formatPrice(price, currency = 'EUR') {
    return currency === 'EUR' ? '€' + price.toFixed(2) : price.toFixed(2) + ' ' + currency;
}

// Update the total price
function updateTotalPrice() {
    totalPrice = 0;

    for (const breadId in orderItems) {
        const quantity = orderItems[breadId];
        const bread = breads.find(b => b.id === parseInt(breadId));

        if (bread && quantity > 0) {
            totalPrice += bread.price * quantity;
        }
    }

    document.getElementById('total-price').textContent = formatPrice(totalPrice);
    document.getElementById('place-order-btn').disabled = totalPrice <= 0;
}

// Update subtotal for an individual bread item
function updateSubtotal(breadId, quantity) {
    const subtotalElement = document.querySelector(`.bread-card[data-id="${breadId}"] .bread-card-total`);
    const bread = breads.find(b => b.id === parseInt(breadId));

    if (bread && subtotalElement) {
        const subtotal = bread.price * quantity;
        subtotalElement.textContent = formatPrice(subtotal, bread.currency);
    }
}

// Generate bread item HTML
function generateBreadItemHTML(bread) {
    orderItems[bread.id] = 0; // Initialize order quantity
    return `
        <div class="bread-card" data-id="${bread.id}" data-price="${bread.price}" data-available="${bread.available}">
            <div class="bread-card-content">
                <div class="bread-card-header">
                    <h3 class="bread-card-name">${bread.name}</h3>
                    <div class="bread-card-price">${formatPrice(bread.price, bread.currency)}</div>
                </div>
                <div class="bread-card-availability">
                    <span>${bread.available} ${languageValues["module_bread_pieces"]}</span>
                    <span class="availability-label">${languageValues["module_bread_total_stock_label"]}</span>
                </div>
                <div class="quantity-selector">
                    <button class="decrease">-</button>
                    <input type="number" min="0" max="${bread.available}" value="0" data-bread-id="${bread.id}">
                    <button class="increase">+</button>
                </div>
                <div class="bread-card-total">${formatPrice(0, bread.currency)}</div>
            </div>
        </div>
    `;
}

// Render bread items
function renderBreadItems(breadsList) {
    const breadContainer = document.getElementById('bread-container');
    if (breadsList.length === 0) {
        breadContainer.innerHTML = `<div class="error-message">${languageValues["module_bread_no_products"]}</div>`;
        return;
    }

    const breadItemsHTML = breadsList.map(generateBreadItemHTML).join('');
    breadContainer.innerHTML = breadItemsHTML;

    // Add event listeners to quantity controls
    document.querySelectorAll('.bread-card').forEach(card => {
        const breadId = card.getAttribute('data-id');
        const price = parseFloat(card.getAttribute('data-price'));
        const available = parseInt(card.getAttribute('data-available'));
        const input = card.querySelector('input');
        const decreaseBtn = card.querySelector('.decrease');
        const increaseBtn = card.querySelector('.increase');

        decreaseBtn.addEventListener('click', () => {
            let value = parseInt(input.value) - 1;
            if (value < 0) value = 0;
            input.value = value;
            orderItems[breadId] = value;
            updateSubtotal(breadId, value);
            updateTotalPrice();
        });

        increaseBtn.addEventListener('click', () => {
            let value = parseInt(input.value) + 1;
            if (value > available) value = available;
            input.value = value;
            orderItems[breadId] = value;
            updateSubtotal(breadId, value);
            updateTotalPrice();
        });

        input.addEventListener('change', () => {
            let value = parseInt(input.value);
            if (value < 0 || isNaN(value)) value = 0;
            if (value > available) value = available;
            input.value = value;
            orderItems[breadId] = value;
            updateSubtotal(breadId, value);
            updateTotalPrice();
        });
    });
}

// Generate order summary
function generateOrderSummary() {
    let summaryHTML = '';
    let orderTotal = 0;
    let currency = 'EUR';

    for (const breadId in orderItems) {
        const quantity = orderItems[breadId];
        if (quantity > 0) {
            const bread = breads.find(b => b.id === parseInt(breadId));
            const itemTotal = bread.price * quantity;
            orderTotal += itemTotal;
            currency = bread.currency;

            summaryHTML += `
                <div class="summary-item">
                    <span>${bread.name} x${quantity}</span>
                    <span>${formatPrice(itemTotal, bread.currency)}</span>
                </div>
            `;
        }
    }

    document.getElementById('summary-items').innerHTML = summaryHTML;
    document.getElementById('summary-total').textContent = formatPrice(orderTotal, currency);

    return { orderTotal, currency };
}

// Initialize PayPal button
function initializePayPalButton(orderTotal, currency) {
    document.getElementById('paypal-button-container').innerHTML = '';

    paypal.Buttons({
        createOrder: (data, actions) => {
            const purchaseItems = [];
            for (const breadId in orderItems) {
                const quantity = orderItems[breadId];
                if (quantity > 0) {
                    const bread = breads.find(b => b.id === parseInt(breadId));
                    purchaseItems.push({
                        name: bread.name,
                        quantity: quantity,
                        unit_amount: {
                            value: bread.price.toFixed(2),
                            currency_code: bread.currency
                        }
                    });
                }
            }

            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: orderTotal.toFixed(2),
                        currency_code: currency,
                        breakdown: {
                            item_total: {
                                value: orderTotal.toFixed(2),
                                currency_code: currency
                            }
                        }
                    },
                    items: purchaseItems,
                    description: 'Bakery Order'
                }]
            });
        },
        onApprove: (data, actions) => {
            return actions.order.capture().then(orderData => {
                const successMessage = document.createElement('div');
                successMessage.style.padding = '15px';
                successMessage.style.marginTop = '20px';
                successMessage.style.backgroundColor = '#d4edda';
                successMessage.style.color = '#155724';
                successMessage.style.borderRadius = '5px';
                successMessage.style.textAlign = 'center';
                successMessage.innerHTML = `<h3>${languageValues["module_bread_order_success"]}</h3><p>${languageValues["module_bread_order_confirmation"]}</p>`;

                document.getElementById('paypal-button-container').innerHTML = '';
                document.getElementById('paypal-button-container').appendChild(successMessage);

                // Reset order
                orderItems = {};
                renderBreadItems(breads);
                updateTotalPrice();
                document.getElementById('order-summary').style.display = 'none';
                document.getElementById('order-form').style.display = 'block';
            });
        },
        onError: () => {
            alert(languageValues["module_bread_payment_error"]);
        }
    }).render('#paypal-button-container');
}

// Initialize the application
async function initApp() {
    // Fetch bread data
    breads = await fetchBreads();

    // Render bread items
    renderBreadItems(breads);

    // Add event listener to Place Order button
    document.getElementById('place-order-btn').addEventListener('click', () => {
        const { orderTotal, currency } = generateOrderSummary();
        document.getElementById('order-form').style.display = 'none';
        document.getElementById('order-summary').style.display = 'block';
        initializePayPalButton(orderTotal, currency);
    });
}

// Start the application
document.addEventListener('DOMContentLoaded', initApp);