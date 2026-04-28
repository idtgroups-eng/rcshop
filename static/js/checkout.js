document.addEventListener("DOMContentLoaded", function () {

    /* ==========================
       LOAD CART DATA & SHOW SUMMARY (DB BASED)
    ========================== */
    
    // ❌ localStorage removed
    // let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

    let tableBody = document.getElementById("orderBody");

    if (!tableBody) {
        console.error("orderBody not found!");
        return;
    }

    let subtotal = 0;

    // ✅ अब cart backend (Django) से render हो रहा है
    let rows = tableBody.querySelectorAll("tr");

    rows.forEach(row => {
        let priceText = row.children[2]?.innerText.replace("₹", "").replace(/,/g, "") || "0";
        let qtyText = row.children[3]?.innerText || "1";

        let price = Number(priceText) || 0;
        let qty = Number(qtyText) || 1;

        subtotal += price * qty;
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

    // ❌ localStorage removed
    // if (itemsInput) itemsInput.value = JSON.stringify(cart);

    // ✅ optional: backend already has items (DB), but safe fallback:
    if (itemsInput) itemsInput.value = "DB_ITEMS";

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

        // 🔥 IMPORTANT — re-fill hidden inputs before submit
        if (subtotalInput) subtotalInput.value = subtotal;
        if (totalInput) totalInput.value = finalTotal;

        // 🚀 NO preventDefault → form will submit to backend
    });

});