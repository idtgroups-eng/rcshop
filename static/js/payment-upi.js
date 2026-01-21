/* ===========================
   TIMER
=========================== */
let time = 300;
setInterval(() => {
    let minutes = Math.floor(time / 60);
    let seconds = time % 60;

    const countdownEl = document.getElementById("countdown");
    if (countdownEl) {
        countdownEl.innerText =
            `${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    }

    if (time > 0) time--;
}, 1000);


/* ===========================
   CSRF TOKEN
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
   UTILS: sanitize amount & build QR
=========================== */
function sanitizeAmount(value) {
    if (value === undefined || value === null) return 0;
    // convert to string, remove currency symbols, commas, spaces; keep digits and dot
    const s = String(value).replace(/[^0-9.]/g, '');
    const n = Number(s);
    return isNaN(n) ? 0 : n;
}

function buildUpiQr(amountRaw, upiId = "9625252254@ybl", name = "RCStore") {
    const amountNum = sanitizeAmount(amountRaw);
    const amtStr = (amountNum % 1 === 0) ? String(Math.floor(amountNum)) : amountNum.toFixed(2);

    const upiUrl = `upi://pay?pa=${encodeURIComponent(upiId)}&pn=${encodeURIComponent(name)}&am=${encodeURIComponent(amtStr)}&cu=INR`;

    // Primary and fallback QR generators
    const googleQr = `https://chart.googleapis.com/chart?cht=qr&chs=350x350&chl=${encodeURIComponent(upiUrl)}`;
    const qrServer = `https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=${encodeURIComponent(upiUrl)}`;

    const qrImg = document.getElementById("upiQr") || document.querySelector(".qr-img");

    if (!qrImg) {
        console.warn("QR image element not found (id=upiQr or .qr-img).");
        // optionally create an element to show a message
        const wrapper = document.querySelector(".qr-wrapper") || document.body;
        const warn = document.createElement("div");
        warn.innerText = "QR element missing. Contact support.";
        warn.style.color = "#fff";
        wrapper.appendChild(warn);
        return;
    }

    let triedFallback = false;
    qrImg.onerror = function() {
        console.warn("Primary QR failed to load, trying fallback QR service...");
        if (!triedFallback) {
            triedFallback = true;
            qrImg.src = qrServer;
        } else {
            // both failed — show helpful UI
            qrImg.style.display = "none";
            const warn = document.createElement("div");
            warn.innerText = "QR unavailable. Please enter amount manually in your UPI app.";
            warn.style.color = "#fff";
            warn.style.textAlign = "center";
            warn.style.padding = "20px";
            qrImg.parentNode && qrImg.parentNode.insertBefore(warn, qrImg);
        }
    };

    // set src to primary (google)
    qrImg.src = googleQr;
    qrImg.alt = `Scan to pay ₹${amtStr}`;
    qrImg.style.width = "350px";
    qrImg.style.height = "350px";

    // update displayed amount text element too
    const upiAmountEl = document.getElementById("upiAmount");
    if (upiAmountEl) upiAmountEl.innerText = `₹${amtStr}`;

    // update top heading text if exists
    const topHeading = document.querySelector(".scan-heading");
    if (topHeading) topHeading.innerText = `Scan to pay ₹${amtStr}`;

    // update instructions area (optional)
    const instr = document.querySelector(".instructions");
    if (instr) {
        instr.innerHTML = `
            <p>✔ Scan the QR Code</p>
            <p>✔ Pay Amount: <strong>₹${amtStr}</strong></p>
            <p>✔ After payment click button below</p>
        `;
    }
}


/* ===========================
   AUTO UPDATE QR WITH TOTAL AMOUNT (on load)
=========================== */
document.addEventListener("DOMContentLoaded", () => {

    // read order from localStorage (may be undefined)
    let order = {};
    try {
        order = JSON.parse(localStorage.getItem("orderData")) || {};
    } catch (e) {
        order = {};
    }

    // Determine raw amount (may contain ₹ or commas)
    let rawAmount = 0;
    if (order.total !== undefined && order.total !== null) {
        rawAmount = order.total;
    } else if (order.amount !== undefined && order.amount !== null) {
        rawAmount = order.amount;
    } else {
        rawAmount = 0;
    }

    // Build QR with sanitized amount and fallback handling
    buildUpiQr(rawAmount, "ar783524@okicici", order.name || "RCStore");
});


/* ===========================
   CONFIRM PAYMENT (POST)
=========================== */

function confirmPayment() {

    const processingEl = document.getElementById("processing");
    if (processingEl) processingEl.style.display = "block";

    let order = {};
    try {
        order = JSON.parse(localStorage.getItem("orderData")) || {};
    } catch (e) {
        order = {};
    }

    order.payment = "UPI";
    localStorage.setItem("orderData", JSON.stringify(order));

    const payload = {
        name: order.name || "",
        email: order.email || "",
        mobile: order.mobile || "",
        address: order.address || "",
        pin: order.pin || "",
        items: order.items || [],
        total: sanitizeAmount(order.total || order.amount || 0),
        payment: "UPI"
    };

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

            localStorage.removeItem("cartItems");
            localStorage.removeItem("orderData");

            setTimeout(() => {
                window.location.href = "/thankyou?order_id=" + encodeURIComponent(data.order_id);
            }, 1200);

        } else {
            alert("UPI Payment Failed: " + (data.error || "Unknown Error"));
            if (processingEl) processingEl.style.display = "none";
        }
    })
    .catch(err => {
        console.error("Network error:", err);
        alert("Network error during UPI payment.");
        if (processingEl) processingEl.style.display = "none";
    });
}
