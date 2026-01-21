let order = JSON.parse(localStorage.getItem("orderData")) || {};

document.getElementById("oid").innerText = order.orderId || "N/A";
document.getElementById("total").innerText = order.total || "0";

function goToOTP(){

    // Generate 4 digit OTP
    let otp = Math.floor(1000 + Math.random() * 9000).toString();

    order.paymentMode = "Cash on Delivery";
    order.codOtp = otp;
    order.codVerified = false;

    localStorage.setItem("orderData", JSON.stringify(order));

    alert("Demo OTP (testing): " + otp); // real app me SMS jayega

    window.location.href = "/payment/cod/otp/";
}
