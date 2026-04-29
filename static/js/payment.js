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
   COMPLETE PAYMENT (COD / ONLINE)
=========================== */

function completePayment(mode) {

    // 🔥 अब localStorage use नहीं करना
    // payment flow already Django + session based है

    if (mode === "COD") {
        // 👉 COD page पर भेजो
        window.location.href = "/payment/cod/";
        return;
    }

    if (mode === "ONLINE") {
        // 👉 Razorpay trigger होगा (payBtn click से)
        document.getElementById("payBtn").click();
        return;
    }

    alert("Invalid payment method");
}


/* ===========================
   COD DIRECT SELECT
=========================== */

function selectCOD(){
    window.location.href = "/payment/cod/";
}