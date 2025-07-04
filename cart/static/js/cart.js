console.log('Cart JavaScript loading...');

$(document).ready(function () {
    console.log('Document ready, jQuery version:', $.fn.jquery);
    
    // Function to get the correct quantity input
    function getQuantityInput(itemId, isMobile = false) {
        if (isMobile || window.innerWidth < 992) {
            return $('#qty-mobile-' + itemId);
        } else {
            return $('#qty-' + itemId);
        }
    }
    
    // Function to update quantity display
    function updateQuantityDisplay(itemId, newValue) {
        // Update both desktop and mobile inputs
        $('#qty-' + itemId).val(newValue);
        $('#qty-mobile-' + itemId).val(newValue);
        
        console.log('Updated quantity display for item ' + itemId + ' to ' + newValue);
    }
    
    // Increment quantity
    $('.increment-qty').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Increment button clicked');
        var itemId = $(this).data('item-id');
        var isMobile = $(this).hasClass('mobile-qty-btn') || $(this).data('target') === 'mobile';
        
        console.log('Item ID:', itemId, 'Mobile:', isMobile);
        
        var qtyInput = getQuantityInput(itemId, isMobile);
        
        if (qtyInput.length === 0) {
            console.error('Quantity input not found for item:', itemId);
            return;
        }
        
        var currentValue = parseInt(qtyInput.val()) || 1;
        console.log('Current value:', currentValue);
        
        if (currentValue < 99) {
            var newValue = currentValue + 1;
            updateQuantityDisplay(itemId, newValue);
            console.log('Incremented to:', newValue);
        } else {
            console.log('Maximum quantity reached');
        }
    });
    
    // Decrement quantity
    $('.decrement-qty').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Decrement button clicked');
        var itemId = $(this).data('item-id');
        var isMobile = $(this).hasClass('mobile-qty-btn') || $(this).data('target') === 'mobile';
        
        console.log('Item ID:', itemId, 'Mobile:', isMobile);
        
        var qtyInput = getQuantityInput(itemId, isMobile);
        
        if (qtyInput.length === 0) {
            console.error('Quantity input not found for item:', itemId);
            return;
        }
        
        var currentValue = parseInt(qtyInput.val()) || 1;
        console.log('Current value:', currentValue);
        
        if (currentValue > 1) {
            var newValue = currentValue - 1;
            updateQuantityDisplay(itemId, newValue);
            console.log('Decremented to:', newValue);
        } else {
            console.log('Minimum quantity reached');
        }
    });
    
    // Update quantity
    $('.update-link').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Update button clicked');
        var itemId = $(this).data('item-id');
        console.log('Updating item ID:', itemId);
        
        // Disable the button to prevent double-clicks
        var updateBtn = $(this);
        updateBtn.prop('disabled', true).text('Updating...');
        
        var form = $('#update-form-mobile-' + itemId);
        if (form.length === 0) {
            form = $('#update-form-' + itemId);
        }
        
        console.log('Form found:', form.length > 0);
        
        if (form.length > 0) {
            // Ensure both inputs have the same value before submitting
            var mobileInput = $('#qty-mobile-' + itemId);
            var desktopInput = $('#qty-' + itemId);
            
            var currentValue = mobileInput.length > 0 ? mobileInput.val() : desktopInput.val();
            
            if (mobileInput.length > 0) mobileInput.val(currentValue);
            if (desktopInput.length > 0) desktopInput.val(currentValue);
            
            console.log('Submitting form with quantity:', currentValue);
            
            // Add a small delay to ensure UI updates are visible
            setTimeout(function() {
                form.submit();
            }, 100);
        } else {
            console.error('Form not found for item ID:', itemId);
            updateBtn.prop('disabled', false).text('Update');
        }
    });
    
    // Remove item
    $('.remove-item').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Remove button clicked');
        var itemId = $(this).data('item-id');
        console.log('Removing item ID:', itemId);
        
        if (!itemId) {
            console.error('Item ID is undefined');
            return;
        }
        
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            var removeBtn = $(this);
            removeBtn.prop('disabled', true).text('Removing...');
            
            var csrfToken = $('[name=csrfmiddlewaretoken]').val();
            var url = '/cart/remove/' + itemId + '/';
            
            console.log('Making AJAX request to:', url);
            
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': csrfToken,
                    'action': 'decrement'
                },
                timeout: 10000, // 10 second timeout
                success: function (response) {
                    console.log('Remove success:', response);
                    location.reload();
                },
                error: function (xhr, status, error) {
                    console.log('Remove error:', xhr.responseText);
                    console.log('Status:', status);
                    console.log('Error:', error);
                    alert('Error removing item from cart: ' + error);
                    removeBtn.prop('disabled', false).text('Remove');
                }
            });
        }
    });
    
    // Prevent manual input on mobile quantity fields
    $('.mobile-qty-input').on('keydown', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Handle window resize
    $(window).on('resize', function() {
        $('.qty_input').each(function() {
            var itemId = $(this).data('item-id');
            var value = $(this).val();
            updateQuantityDisplay(itemId, value);
        });
    });
    
    console.log('Cart JavaScript loaded successfully');
});