/* ==========================
  /* ==========================
   LOAD CART FROM LOCALSTORAGE
==============================*/
let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

/* FIX MISSING FIELDS */
cart = cart.map(p => {

    // Fix Qty
    p.qty = Number(p.qty) || 1;

    // Fix Price (₹, comma sab remove → number)
    p.price = Number(
        p.price
        .toString()
        .replace(/,/g, "")     // remove comma
        .replace(/₹/g, "")     // remove rupee sign
        .trim()
    ) || 0;

    return p;
});


/* ==========================
   LOAD CART TABLE
==============================*/
function loadCart() {
    let body = document.getElementById("cart-body");
    body.innerHTML = "";

    if (cart.length === 0) {
        document.getElementById("cartBox").innerHTML =
            `<div class="empty">Your Cart is Empty 🛒</div>`;
        return;
    }

    let grand = 0;

    cart.forEach((p, i) => {
        let total = p.price * p.qty;
        grand += total;

        body.innerHTML += `
        <tr>
            <td>
                <img src="${p.img}" width="70" style="border-radius:8px"
                    onerror="this.src='${window.location.origin}/static/images/no-image.png'">
            </td>

            <td>${p.name}</td>
            <td>₹${p.price.toLocaleString()}</td>

            <td>
                <button class="qty-btn" onclick="changeQty(${i}, -1)">–</button>
                ${p.qty}
                <button class="qty-btn" onclick="changeQty(${i}, 1)">+</button>
            </td>

            <td>₹${total.toLocaleString()}</td>

            <td>
                <button class="remove-btn" onclick="removeItem(${i})">
                    Delete
                </button>
            </td>
        </tr>
        `;
    });

    document.getElementById("grandBox").innerHTML =
        `Grand Total: ₹${grand.toLocaleString()}`;
}

/* ==========================
   CHANGE QUANTITY
==============================*/
function changeQty(i, val) {
    cart[i].qty += val;
    if (cart[i].qty <= 0) cart.splice(i, 1);

    localStorage.setItem("cartItems", JSON.stringify(cart));
    loadCart();
    updateCartCount();
}

/* REMOVE ITEM */
function removeItem(i) {
    cart.splice(i, 1);
    localStorage.setItem("cartItems", JSON.stringify(cart));
    loadCart();
    updateCartCount();
}

/* ==========================
   UPDATE CART COUNT
==============================*/
/* ==========================
   UPDATE CART COUNT (FIXED)
==============================*/
function updateCartCount() {
    let c = JSON.parse(localStorage.getItem("cartItems")) || [];
    let totalQty = 0;

    c.forEach(item => {
        totalQty += Number(item.qty) || 1;
    });

    const counter = document.getElementById("cartCount");
    if (counter) counter.innerText = totalQty;
}

/* ==========================
   GO TO CHECKOUT (FIXED)
==============================*/
function goCheckout() {
    if (!cart.length) return alert("Your cart is empty!");

    // checkoutURL is injected from cart.html 
    // <script> const checkoutURL = "/checkout/"; </script>
    window.location.href = checkoutURL;
}

/* INIT */
loadCart();
updateCartCount();
