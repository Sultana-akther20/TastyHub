$(document).ready(function() {
var stripePublicKey=$('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
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
    invalid:{
        color:'#dc3545',
        iconColor:'#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-payment');

// Fixed: Changed from 'change' to proper event handling
card.on('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});

var form = document.getElementById('payment-form');
form.addEventListener('submit', function(ev){
    ev.preventDefault();
    card.update({'disabled': true});
    $('#submit-button').attr('disabled', true);
    
    // Fixed: corrected typo from 'connfirmCardPayment' to 'confirmCardPayment'
    stripe.confirmCardPayment(clientSecret, {
        payment_method:{
            card: card,
        }
    }).then(function(result){
        if (result.error){
            // Fixed: changed from 'card-error' to 'card-errors' to match the element above
            var errorDiv = document.getElementById('card-errors');
            var html =`<span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            card.update({'disabled': false});
            $('#submit-button').attr('disabled', false);
        }else{ 
            if(result.paymentIntent.status === 'succeeded'){
                // Fixed: changed from 'form.onsubmit()' to 'form.submit()' for proper form submission
                form.submit();
            }
        }
    });
});
});