$(document).ready(function() {
    // Better way to get the keys from the template
    var stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    var clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);
    
    
    // Check if keys exist before initializing Stripe
    if (!stripePublicKey) {
        console.error('Stripe publishable key is missing!');
        return;
    }
    
    if (!clientSecret) {
        console.error('Client secret is missing!');
        return;
    }
    
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    
    // Improved responsive styling for the card element
    var style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            lineHeight: '24px',
            letterSpacing: '0.025em',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        },
        complete: {
            color: '#28a745',
            iconColor: '#28a745'
        }
    };
    
    // Create card element with responsive options
    var cardOptions = {
        style: style,
        hidePostalCode: true,
        iconStyle: 'solid',
        classes: {
            focus: 'StripeElement--focus',
            empty: 'StripeElement--empty',
            invalid: 'StripeElement--invalid',
        }
    };
    
    var card = elements.create('card', cardOptions);
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
    
    if (!form) {
        console.error('Payment form not found! Check your HTML.');
        return;
    }
    
    if (!submitButton) {
        console.error('Submit button not found! Check your HTML.');
        return;
    }
    
    // Add click event listener to submit button as backup
    submitButton.addEventListener('click', function(e) {
        console.log('Submit button clicked!');
        e.preventDefault();
        handleFormSubmission();
    });
    
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();
        console.log('Form submission started via submit event');
        handleFormSubmission();
    });
    
    function handleFormSubmission() {
        console.log('handleFormSubmission called');
        
        // Disable card and submit button to prevent multiple submissions
        card.update({'disabled': true});
        $('#submit-button').attr('disabled', true);
        $('#submit-button').html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Processing...
        `);
        
        // Get form data for the payment intent
        var saveInfo = Boolean($('#id-save-info').attr('checked'));
        var csrfToken = $('[name="csrfmiddlewaretoken"]').val();
        
        // First, cache the checkout data
        var postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };
        
        var url = '/checkout/cache_checkout_data/';
        
        console.log('Sending cache request to:', url);
        console.log('Post data:', postData);
        
        $.post(url, postData)
            .done(function(response) {
                console.log('Cache request succeeded:', response);
                
                // If caching succeeds, proceed with payment confirmation
                console.log('Starting payment confirmation...');
                
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
                                country: 'GB',
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
                            country: 'GB',
                            postal_code: $.trim(form.postcode.value),
                            state: $.trim(form.county.value),
                        }
                    },
                }).then(function(result) {
                    console.log('Payment confirmation result:', result);
                    
                    if (result.error) {
                        console.error('Payment error:', result.error);
                        
                        var errorDiv = document.getElementById('card-errors');
                        var html = `
                            <span class="icon" role="alert">
                                <i class="fas fa-times"></i>
                            </span>
                            <span>${result.error.message}</span>
                        `;
                        $(errorDiv).html(html);
                        
                        // Re-enable card and submit button
                        resetForm();
                        
                    } else {
                        console.log('Payment Intent status:', result.paymentIntent.status);
                        
                        if (result.paymentIntent.status === 'succeeded') {
                            console.log('Payment succeeded! Submitting form...');
                            
                            // Add the client_secret to the form before submitting
                            var hiddenInput = document.createElement('input');
                            hiddenInput.type = 'hidden';
                            hiddenInput.name = 'client_secret';
                            hiddenInput.value = clientSecret;
                            form.appendChild(hiddenInput);
                            
                            // Submit the form
                            form.submit();
                        } else {
                            console.log('Payment not succeeded, status:', result.paymentIntent.status);
                            resetForm();
                        }
                    }
                }).catch(function(error) {
                    console.error('Payment confirmation error:', error);
                    showError('There was an error processing your payment. Please try again.');
                    resetForm();
                });
                
            })
            .fail(function(xhr, status, error) {
                console.error('Cache request failed:', status, error);
                console.error('Response:', xhr.responseText);
                console.error('Status code:', xhr.status);
                
                // Show specific error message
                var errorMessage = 'There was an error processing your payment. Please try again.';
                if (xhr.status === 404) {
                    errorMessage = 'Cache endpoint not found. Please contact support.';
                } else if (xhr.status === 403) {
                    errorMessage = 'Permission denied. Please refresh the page and try again.';
                }
                
                showError(errorMessage);
                resetForm();
            });
    }
    
    // Helper function to show errors
    function showError(message) {
        var errorDiv = document.getElementById('card-errors');
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${message}</span>
        `;
        $(errorDiv).html(html);
        errorDiv.style.display = 'block';
    }
    
    // Helper function to reset the form
    function resetForm() {
        card.update({'disabled': false});
        $('#submit-button').attr('disabled', false);
        $('#submit-button').html(`
            <span class="font-weight-bold">Complete Order</span>
            <span class="icon"><i class="fas fa-lock"></i></span>
        `);
    }
    
    // Additional debugging for form elements
    console.log('Form found:', form);
    console.log('Card element mounted on:', document.getElementById('card-payment'));
    console.log('Error div found:', document.getElementById('card-errors'));
    console.log('Submit button found:', document.getElementById('submit-button'));
});