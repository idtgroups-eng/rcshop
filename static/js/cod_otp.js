let order = JSON.parse(localStorage.getItem("orderData")) || {};

function verifyOTP(){

    let entered = document.getElementById("otp").value;

    if (entered !== order.codOtp) {
        alert("❌ Invalid OTP");
        return;
    }

    order.codVerified = true;
    order.status = "Placed";
    localStorage.setItem("orderData", JSON.stringify(order));

    fetch("/api/save-cod-order/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(order)
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            localStorage.setItem(
                "invoiceCart",
                localStorage.getItem("cartItems")
            );
            localStorage.removeItem("cartItems");
            window.location.href = "/thankyou/";
        } else {
            alert("Order save failed");
        }
    });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(";").forEach(c => {
            c = c.trim();
            if (c.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(c.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}
