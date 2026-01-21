// Fetch order from LocalStorage
let order = JSON.parse(localStorage.getItem("orderData")) || {};

// Insert data into page
document.getElementById("name").innerText  = order?.name || "Customer";
document.getElementById("oid").innerText   = order?.orderId || "N/A";
document.getElementById("total").innerText = "₹" + (order?.total || 0);
document.getElementById("pay").innerText   = order?.paymentMode || "N/A";

// RETURN HOME
function goHome(){
    window.location.href = "/";
}

// WHATSAPP SHARE
function shareOrder(){
    let msg = `🛒 *RCShop Order Details*  
------------------------------------
👤 Name: ${order.name}
📞 Mobile: ${order.mobile}
📍 Address: ${order.address}
------------------------------------
🧾 Order ID: ${order.orderId}
💰 Total: ₹${order.total}
💳 Payment Mode: ${order.paymentMode}
------------------------------------
Thank you for choosing RCShop ❤️`;

    window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, "_blank");
}

// Backup cart
localStorage.setItem("cartItemsBak", localStorage.getItem("cartItems"));
localStorage.removeItem("cartItems");

// CONFETTI + SOUND
window.onload = () => {

    confetti({
        particleCount: 200,
        spread: 120,
        startVelocity: 50,
        origin: { y: 0.2 }
    });

    let duration = 2000;
    let end = Date.now() + duration;

    (function frame() {
        confetti({
            particleCount: 5,
            startVelocity: 30,
            spread: 360,
            ticks: 60,
            origin: { x: Math.random(), y: Math.random() - 0.2 }
        });

        if (Date.now() < end) requestAnimationFrame(frame);
    })();

    let sound = new Audio("{% static 'sounds/celebration.mp3' %}");
    sound.volume = 0.7;
    sound.play();
};
