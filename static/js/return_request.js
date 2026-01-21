document.addEventListener("DOMContentLoaded", function () {

    const orderInput = document.getElementById("orderId");
    const nameInput = document.getElementById("name");
    const reasonInput = document.getElementById("reason");
    const submitBtn = document.getElementById("submitBtn");

    function validate() {
        const id = orderInput.value.trim();
        const nm = nameInput.value.trim();
        const rs = reasonInput.value.trim();
        if (!id || !nm || !rs) return false;
        return { id, nm, rs };
    }

    submitBtn.addEventListener("click", function () {
        const data = validate();
        if (!data) {
            alert("Please fill all fields!");
            return;
        }

        // Save locally
        let requests = JSON.parse(localStorage.getItem("returnRequests")) || [];
        requests.push({
            orderId: data.id,
            name: data.nm,
            reason: data.rs,
            date: new Date().toLocaleString()
        });
        localStorage.setItem("returnRequests", JSON.stringify(requests));

        alert("Your return request has been submitted!");

        // WhatsApp quick-send
        const msg = `*RCShop Return Request*\n\nOrder ID: ${data.id}\nName: ${data.nm}\nReason: ${data.rs}\nDate: ${new Date().toLocaleString()}`;
        window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, "_blank");

        // redirect to return policy page (URL injected from template)
        const redirectUrl = window.RETURN_POLICY_URL || '/return-policy/';
        window.location.href = redirectUrl;
    });
});
