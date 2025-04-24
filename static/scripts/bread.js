

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
        document.getElementById('bread-container').innerHTML = `<div class="error-message">Failed to load bread products. Please try again later.</div>`;
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
      const subtotalElement = document.getElementById(`subtotal-${breadId}`);
      const bread = breads.find(b => b.id === parseInt(breadId));

      if (bread && subtotalElement) {
        const subtotal = bread.price * quantity;
        subtotalElement.textContent = formatPrice(subtotal, bread.currency);
      }
    }

    // Handle quantity change
    function handleQuantityChange(event) {
      const breadId = event.target.dataset.breadId;
      const quantity = parseInt(event.target.value);
      const maxAvailable = parseInt(event.target.max);

      // Ensure quantity is within valid range
      if (quantity < 0) {
        event.target.value = 0;
        orderItems[breadId] = 0;
      } else if (quantity > maxAvailable) {
        event.target.value = maxAvailable;
        orderItems[breadId] = maxAvailable;
      } else {
        orderItems[breadId] = quantity;
      }

      updateSubtotal(breadId, orderItems[breadId]);
      updateTotalPrice();
    }

    // Generate bread item HTML
    function generateBreadItemHTML(bread) {
      orderItems[bread.id] = 0; // Initialize order quantity

      return `
        <div class="bread-item">
          <div class="bread-header">
            <div class="bread-name">${bread.name}</div>
            <div class="bread-price">${formatPrice(bread.price, bread.currency)}</div>
          </div>
          <div class="bread-availability">${bread.available} available</div>
          <div class="order-controls">
            <label for="quantity-${bread.id}">Quantity:</label>
            <input
              type="number"
              id="quantity-${bread.id}"
              class="quantity-selector"
              min="0"
              max="${bread.available}"
              value="0"
              data-bread-id="${bread.id}"
            >
            <div class="subtotal" id="subtotal-${bread.id}">${formatPrice(0, bread.currency)}</div>
          </div>
        </div>
      `;
    }

    // Render bread items
    function renderBreadItems(breadsList) {
      if (breadsList.length === 0) {
        document.getElementById('bread-container').innerHTML = `<div class="error-message">No bread products available at the moment.</div>`;
        return;
      }

      const breadItemsHTML = breadsList.map(generateBreadItemHTML).join('');
      document.getElementById('bread-container').innerHTML = breadItemsHTML;

      // Add event listeners to quantity inputs
      document.querySelectorAll('.quantity-selector').forEach(input => {
        input.addEventListener('change', handleQuantityChange);
      });
    }

    // Generate order summary
    function generateOrderSummary() {
      let summaryHTML = '';
      let orderTotal = 0;
      let purchaseUnits = [];
      let currency = 'EUR'; // Default currency

      for (const breadId in orderItems) {
        const quantity = orderItems[breadId];
        if (quantity > 0) {
          const bread = breads.find(b => b.id === parseInt(breadId));
          const itemTotal = bread.price * quantity;
          orderTotal += itemTotal;
          currency = bread.currency; // Use the currency from items

          summaryHTML += `
            <div class="summary-item">
              <div>${bread.name} x ${quantity}</div>
              <div>${formatPrice(itemTotal, bread.currency)}</div>
            </div>
          `;
        }
      }

      document.getElementById('summary-items').innerHTML = summaryHTML;
      document.getElementById('summary-total').textContent = formatPrice(orderTotal, currency);

      return {
        orderTotal,
        currency
      };
    }

    // Handle "Place Order" button click
    function handlePlaceOrder() {
      const { orderTotal, currency } = generateOrderSummary();

      // Hide order form and show summary
      document.getElementById('order-form').style.display = 'none';
      document.getElementById('order-summary').style.display = 'block';

      // Initialize PayPal button
      initializePayPalButton(orderTotal, currency);
    }

    // Initialize PayPal button
    function initializePayPalButton(orderTotal, currency) {
      // Clear previous buttons
      document.getElementById('paypal-button-container').innerHTML = '';

      // Create PayPal button with purchase details
      paypal.Buttons({
        createOrder: function(data, actions) {
          // Create an array for the purchase items
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
        onApprove: function(data, actions) {
          return actions.order.capture().then(function(orderData) {
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.style.padding = '15px';
            successMessage.style.marginTop = '20px';
            successMessage.style.backgroundColor = '#d4edda';
            successMessage.style.color = '#155724';
            successMessage.style.borderRadius = '5px';
            successMessage.style.textAlign = 'center';
            successMessage.innerHTML = '<h3>Payment Successful!</h3><p>Thank you for your order. You will receive a confirmation email shortly.</p>';

            // Replace PayPal button with success message
            document.getElementById('paypal-button-container').innerHTML = '';
            document.getElementById('paypal-button-container').appendChild(successMessage);

            console.log('Capture result', orderData);
          });
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
      document.getElementById('place-order-btn').addEventListener('click', handlePlaceOrder);
    }

    // Start the application
    document.addEventListener('DOMContentLoaded', initApp);