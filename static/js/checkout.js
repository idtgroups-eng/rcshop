document.addEventListener("DOMContentLoaded", function () {

    /* ==========================
       LOAD CART DATA & SHOW SUMMARY
    ========================== */
    let cart = JSON.parse(localStorage.getItem("cartItems")) || [];
    let tableBody = document.getElementById("orderBody");

    if (!tableBody) {
        console.error("orderBody not found!");
        return;
    }

    let subtotal = 0;
    tableBody.innerHTML = "";

    cart.forEach(item => {
        let price = Number(item.price) || 0;
        let qty = Number(item.qty) || 1;
        subtotal += price * qty;

        tableBody.innerHTML += `
            <tr>
                <td>
                    <img src="${item.img}" width="60" style="border-radius:8px"
                         onerror="this.src='/static/images/no-image.png'">
                </td>
                <td>${item.name}</td>
                <td>₹${price.toLocaleString()}</td>
                <td>${qty}</td>
            </tr>
        `;
    });

    /* ==========================
       CALCULATIONS (NO GST / NO DISCOUNT)
    ========================== */
    let shipping = 0;            // FREE SHIPPING
    let finalTotal = subtotal;   // ONLY subtotal

    /* ==========================
       PRINT SUMMARY
    ========================== */
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    setText("sumSubtotal", "₹" + subtotal.toLocaleString());
    setText("sumShip", "FREE");
    setText("grandTotal", "₹" + finalTotal.toLocaleString());

    /* ==========================
       SET HIDDEN INPUTS
    ========================== */
    const subtotalInput = document.getElementById("subtotalInput");
    const totalInput = document.getElementById("totalInput");
    const itemsInput = document.getElementById("itemsInput");

    if (subtotalInput) subtotalInput.value = subtotal;
    if (totalInput) totalInput.value = finalTotal;
    if (itemsInput) itemsInput.value = JSON.stringify(cart);

    /* ==========================
       FORM SUBMIT HANDLER (FINAL FIX)
    ========================== */
    const form = document.getElementById("checkoutForm");
    if (!form) {
        console.error("checkoutForm not found!");
        return;
    }

    form.addEventListener("submit", function (e) {

        const name = document.getElementById("custName").value.trim();
        const email = document.getElementById("custEmail").value.trim();
        const mobile = document.getElementById("custMobile").value.trim();
        const address = document.getElementById("custAddress").value.trim();
        const pin = document.getElementById("custPin").value.trim();

        // ❌ Validation fail → stop submit
        if (!name || !email || !mobile || !address || !pin) {
            alert("Please fill all shipping details");
            e.preventDefault();
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address");
            e.preventDefault();
            return;
        }

        // ✅ Cart data already set in hidden input
        // ✅ Browser will now submit naturally to /payment/
    });

});
