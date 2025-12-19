/* ===========================
   CSRF TOKEN HELPER
=========================== */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const c = cookies[i].trim();
            if (c.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");



/* ===========================
   COMPLETE PAYMENT (COD / UPI / ONLINE)
=========================== */

function completePayment(mode) {

    let order = JSON.parse(localStorage.getItem("orderData"));

    if (!order) {
        alert("Order Missing — Please Checkout First");
        window.location.href = "/checkout";
        return;
    }

    // Set selected payment method
    order.payment = mode;
    localStorage.setItem("orderData", JSON.stringify(order));

    // Prepare POST Payload for Django
    const payload = {
        name: order.name,
        email: order.email,
        mobile: order.mobile,
        address: order.address,
        pin: order.pin || "",
        items: order.items || [],
        total: order.total,
        payment: order.payment
    };

    // Send AJAX POST → Django → Save Order → Send Email → Return order_id
    fetch("/api/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {

        if (data.success) {

            // Clear cart and orderData
            localStorage.removeItem("cartItems");
            localStorage.removeItem("orderData");

            // Redirect to Django thankyou page with order_id
            window.location.href = "/thankyou?order_id=" + data.order_id;

        } else {
            alert("Checkout Failed: " + (data.error || "Unknown Error"));
            console.error(data);
        }
    })
    .catch(err => {
        console.error("Network error:", err);
        alert("Network error, please try again.");
    });
}
function selectCOD(){
    window.location.href = "/payment/cod/";
}
