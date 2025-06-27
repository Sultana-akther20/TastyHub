$(document).ready(function() {
    // Get the keys from the template
    var stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    var clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);
    
    // Validate keys
    if (!stripePublicKey) {
        console.error('Stripe publishable key is missing!');
        showError('Payment system configuration error. Please contact support.');
        return;
    }
    
    if (!clientSecret) {
        console.error('Client secret is missing!');
        showError('Payment initialization error. Please refresh and try again.');
        return;
    }
    
    // Initialize Stripe
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    
    // Card element styling
    var style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };
    
    var card = elements.create('card', {style: style});
    card.mount('#card-payment');
    
    // Handle real-time validation errors from the card Element
    card.on('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
            displayError.style.display = 'block';
        } else {
            displayError.textContent = '';
            displayError.style.display = 'none';
        }
    });
    
    // Handle form submission
    var form = document.getElementById('payment-form');
    var submitButton = document.getElementById('submit-button');
    
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();
        
        // Validate form before processing
        if (!validateForm()) {
            return;
        }
        
        // Disable form to prevent multiple submissions
        setLoadingState(true);
        
        // Get form data for the payment intent
        var saveInfo = Boolean($('#id-save-info').prop('checked'));
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        var postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };
        var url = '/checkout/cache_checkout_data/';
        
        // Cache checkout data first
        $.post(url, postData)
            .done(function() {
                // Confirm payment with Stripe
                stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: $.trim(form.full_name.value),
                            phone: $.trim(form.phone_number.value),
                            email: $.trim(form.email.value),
                            address: {
                                line1: $.trim(form.street_address1.value),
                                line2: $.trim(form.street_address2.value),
                                city: $.trim(form.town_or_city.value),
                                country: $.trim(form.country.value),
                                state: $.trim(form.county.value),
                                postal_code: $.trim(form.postcode.value),
                            }
                        }
                    },
                    shipping: {
                        name: $.trim(form.full_name.value),
                        phone: $.trim(form.phone_number.value),
                        address: {
                            line1: $.trim(form.street_address1.value),
                            line2: $.trim(form.street_address2.value),
                            city: $.trim(form.town_or_city.value),
                            country: $.trim(form.country.value),
                            postal_code: $.trim(form.postcode.value),
                            state: $.trim(form.county.value),
                        }
                    },
                }).then(function(result) {
                    if (result.error) {
                        handlePaymentError(result.error);
                    } else {
                        if (result.paymentIntent.status === 'succeeded') {
                            // Payment succeeded, submit the form
                            form.submit();
                        }
                    }
                });
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error('Cache checkout data failed:', textStatus, errorThrown);
                showError('Unable to process payment. Please try again.');
                setLoadingState(false);
            });
    });
    
    // Helper functions
    function validateForm() {
        var requiredFields = ['full_name', 'email', 'phone_number', 'country', 
                             'town_or_city', 'street_address1', 'postcode'];
        var isValid = true;
        
        requiredFields.forEach(function(fieldName) {
            var field = form[fieldName];
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Validate email format
        var emailField = form.email;
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailField.value && !emailRegex.test(emailField.value)) {
            showFieldError(emailField, 'Please enter a valid email address');
            isValid = false;
        }
        
        return isValid;
    }
    
    function showFieldError(field, message) {
        var errorDiv = field.parentNode.querySelector('.field-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-danger small mt-1';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        field.classList.add('is-invalid');
        
        // Remove error on field change
        field.addEventListener('input', function() {
            errorDiv.textContent = '';
            field.classList.remove('is-invalid');
        }, { once: true });
    }
    
    function setLoadingState(loading) {
        if (loading) {
            card.update({'disabled': true});
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Processing...
            `;
            $('#payment-form').fadeOut(100);
            showLoadingOverlay();
        } else {
            card.update({'disabled': false});
            submitButton.disabled = false;
            submitButton.innerHTML = `
                <span class="font-weight-bold">Complete Order</span>
                <span class="icon"><i class="fas fa-lock"></i></span>
            `;
            $('#payment-form').fadeIn(100);
            hideLoadingOverlay();
        }
    }
    
    function handlePaymentError(error) {
        var errorDiv = document.getElementById('card-errors');
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${error.message}</span>
        `;
        $(errorDiv).html(html);
        errorDiv.style.display = 'block';
        
        // Scroll to error
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setLoadingState(false);
    }
    
    function showError(message) {
        var errorDiv = document.getElementById('card-errors');
        if (errorDiv) {
            errorDiv.innerHTML = `
                <span class="icon" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                </span>
                <span>${message}</span>
            `;
            errorDiv.style.display = 'block';
        }
    }
    
    function showLoadingOverlay() {
        var overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    function hideLoadingOverlay() {
        var overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
});