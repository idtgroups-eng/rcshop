document.addEventListener("DOMContentLoaded", function () {

    /* -------- LOAD CART DATA & SHOW SUMMARY -------- */
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
                <td><img src="${item.img}" width="60" style="border-radius:8px"></td>
                <td>${item.name}</td>
                <td>₹${price.toLocaleString()}</td>
                <td>${qty}</td>
            </tr>
        `;
    });

    /* -------- CALCULATIONS -------- */
    let gst = Math.round(subtotal * 0.18);
    let shipping = subtotal > 20000 ? 0 : 99;
    let flatDiscount = subtotal > 0 ? 50 : 0;
    let extraDiscount = subtotal > 1999 ? Math.floor(subtotal * 0.10) : 0;

    let finalTotal = subtotal + gst + shipping - flatDiscount - extraDiscount;

    /* -------- PRINT SUMMARY -------- */
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    setText("sumSubtotal", "₹" + subtotal.toLocaleString());
    setText("sumGst", "₹" + gst.toLocaleString());
    setText("sumShip", shipping === 0 ? "FREE" : "₹" + shipping);
    setText("sumFlat", "-₹" + flatDiscount.toLocaleString());
    setText("sumExtra", "-₹" + extraDiscount.toLocaleString());
    setText("grandTotal", "₹" + finalTotal.toLocaleString());

    /* -------- SET HIDDEN INPUTS (VERY IMPORTANT) -------- */
    document.getElementById("subtotalInput").value = subtotal;
    document.getElementById("gstInput").value = gst;
    document.getElementById("flatDiscountInput").value = flatDiscount;
    document.getElementById("extraDiscountInput").value = extraDiscount;
    document.getElementById("totalInput").value = finalTotal;

    /* -------- FORM SUBMIT HANDLER -------- */
    const form = document.getElementById("checkoutForm");
    if (!form) {
        console.error("checkoutForm not found!");
        return;
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("custName").value.trim();
        const email = document.getElementById("custEmail").value.trim();
        const mobile = document.getElementById("custMobile").value.trim();
        const address = document.getElementById("custAddress").value.trim();
        const pin = document.getElementById("custPin").value.trim();

        if (!name || !email || !mobile || !address || !pin) {
            alert("Please fill all shipping details");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address");
            return;
        }

        // ✅ CART + BILL DATA → DJANGO
        document.getElementById("itemsInput").value = JSON.stringify(cart);

        // FINAL SUBMIT (Django handles redirect)
        form.submit();
    });

});
