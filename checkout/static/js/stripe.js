$(document).ready(function() {
    // Better way to get the keys from the template
    var stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    var clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);
    
    // Debug: Check if keys are properly loaded
    console.log('Stripe Public Key:', stripePublicKey);
    console.log('Client Secret:', clientSecret);
    
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
        } else {
            displayError.textContent = '';
        }
    });
    
    // Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();
        
        // Disable card and submit button to prevent multiple submissions
        card.update({'disabled': true});
        $('#submit-button').attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);
        //$('#submit-button').html(`
          //  <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            //Processing...
        //`);
        
        // Get form data for the payment intent
        var saveInfo = Boolean($('#id-save-info').attr('checked'));
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        var postData ={
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };
        var url='/checkout/cache_checkout_data/';

        $.post(url, postData).done(function(){
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
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>
                `;
                $(errorDiv).html(html);
                
                // Re-enable card and submit button
                card.update({'disabled': false});
                $('#submit-button').attr('disabled', false);
                $('#submit-button').html(`
                    <span class="font-weight-bold">Complete Order</span>
                    <span class="icon"><i class="fas fa-lock"></i></span>
                `);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function (){
        location.reload();
    })
});
 });