/* ==========================
   LOAD CART FROM LOCALSTORAGE
==============================*/
let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

/* ==========================
   FIX DATA (SAFE CLEAN)
==============================*/
cart = cart.map(p => {

    p.qty = Number(p.qty);
    if (!p.qty || p.qty < 1) p.qty = 1;

    p.price = Number(
        p.price?.toString().replace(/,/g, "").replace(/₹/g, "").trim()
    ) || 0;

    return p;
});


/* ==========================
   ADD TO CART (SYNC SAFE)
==============================*/
function addToCart(name, price, img, qty = 1) {

    if (name.toLowerCase().includes("bulk") && qty === 1) {
        qty = 100;
    }

    let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

    let existing = cart.find(item => item.name === name);

    if (existing) {
        existing.qty += qty;
    } else {
        cart.push({
            name: name,
            price: Number(price),
            img: img,
            qty: qty
        });
    }

    localStorage.setItem("cartItems", JSON.stringify(cart));
    updateCartCount();
}


/* ==========================
   BUY NOW
==============================*/
function buyNow(name, price, img, qty = 1) {

    if (name.toLowerCase().includes("bulk") && qty === 1) {
        qty = 100;
    }

    addToCart(name, price, img, qty);
    window.location.href = "/cart/";
}


/* ==========================
   LOAD CART TABLE
==============================*/
function loadCart() {

    cart = JSON.parse(localStorage.getItem("cartItems")) || [];

    let body = document.getElementById("cart-body");
    if (!body) return;

    body.innerHTML = "";

    if (cart.length === 0) {
        let box = document.getElementById("cartBox");
        if (box) {
            box.innerHTML = `<div class="empty">Your Cart is Empty 🛒</div>`;
        }
        return;
    }

    let grand = 0;

    cart.forEach((p, i) => {

        p.price = Number(
            p.price?.toString().replace(/,/g, "").replace(/₹/g, "").trim()
        ) || 0;

        p.qty = Number(p.qty) || 1;

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

    let grandBox = document.getElementById("grandBox");
    if (grandBox) {
        grandBox.innerHTML = `Grand Total: ₹${grand.toLocaleString()}`;
    }
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


/* ==========================
   REMOVE ITEM
==============================*/
function removeItem(i) {

    cart.splice(i, 1);

    localStorage.setItem("cartItems", JSON.stringify(cart));

    loadCart();
    updateCartCount();
}


/* ==========================
   UPDATE CART COUNT (FIXED)
==============================*/
function updateCartCount() {

    let c = JSON.parse(localStorage.getItem("cartItems")) || [];

    let totalQty = 0;

    c.forEach(item => {
        totalQty += Number(item.qty) || 1;
    });

    let counter = document.getElementById("cartCount");

    if (counter) counter.innerText = totalQty;
}


/* ==========================
   GO TO CHECKOUT
==============================*/
function goCheckout() {
    try {
        window.location.href = checkoutURL || "/checkout/";
    } catch (e) {
        console.error("Redirect error:", e);
        alert("Unable to proceed to checkout!");
    }
}

/* ==========================
   INIT
==============================*/
loadCart();
updateCartCount();


/* ==========================
   CART DRAWER (SAFE)
==============================*/
let btn = document.getElementById("cartMenuBtn");

if (btn) {
    btn.onclick = () => {
        document.getElementById("cartDrawer")?.classList.toggle("open");
    };
}

document.addEventListener("click", function (e) {

    let drawer = document.getElementById("cartDrawer");
    let btn = document.getElementById("cartMenuBtn");

    if (drawer && btn && drawer.classList.contains("open")) {
        if (!drawer.contains(e.target) && !btn.contains(e.target)) {
            drawer.classList.remove("open");
        }
    }
});