var updateBtns = document.getElementsByClassName('update-cart');

for(let i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        var orderId;
        if (this.dataset.order)
            orderId = this.dataset.order;

        if(user == 'AnonymousUser'){
            addCookieItem(productId, action);
        } else {
            updateUserOrder(productId, action, orderId);
        }
    })
}

function addCookieItem(productId, action) {
    console.log('not logged in');

    if(action == 'add'){
        if(!cart[productId]){
            cart[productId]={'quantity': 1};
        } else {
            cart[productId]['quantity'] += 1;
        }
    } else if (action == 'remove'){
        cart[productId]['quantity'] -= 1;
        if(cart[productId]['quantity'] <= 0){
            console.log('Removed item');
            delete cart[productId]
        }
    }
    console.log('Cart= ', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
    location.reload()
}

function updateUserOrder(productId, action, orderId) {
    console.log('user is logged and sending data...');

    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId,
                              'action': action,
                              'orderId': orderId})
    }).then((response) => {
        return response.json()
    }).then((data) => {
        console.log('data:', data);
        location.reload()
    })
}
