// payment-online.js (updated)
// Replace your current file with this.

document.addEventListener('DOMContentLoaded', () => {

  const $ = id => document.getElementById(id);

  /*********************************************************
   * 1) Populate Order Summary (left panel) from localStorage
   *********************************************************/
  (function populateSummaryFromLocalStorage() {
    try {
      const itemsTotalEl = $("itemsTotal");
      const totalPayEl = $("totalPay");
      const payBtn = $("payNow");

      if (!itemsTotalEl || !totalPayEl) {
        console.warn("payment-online: summary elements not found (itemsTotal/totalPay).");
        return;
      }

      const stored = localStorage.getItem("orderData");
      if (!stored) {
        itemsTotalEl.innerText = "₹0";
        totalPayEl.innerText = "₹0";
        if (payBtn) payBtn.disabled = true;
        return;
      }

      const order = JSON.parse(stored);

      // Prefer explicit keys, fallback to calculated
      const subtotal = Number(order.subtotal ?? order.itemsTotal ?? 0) || 0;
      const gst = Number(order.gst ?? 0) || Math.round(subtotal * 0.18);
      const shipping = Number(order.shipping ?? 0) || 0;
      const total = Number(order.total ?? order.total_amount ?? (subtotal + gst + shipping)) || 0;

      itemsTotalEl.innerText = "₹" + subtotal.toLocaleString();
      totalPayEl.innerText = "₹" + total.toLocaleString();

      if (payBtn) payBtn.disabled = false;

    } catch (err) {
      console.error("populateSummaryFromLocalStorage error:", err);
    }
  })();

  /*********************************************************
   * 2) Safe element references
   *********************************************************/
  const cardInput = $("card");
  const nameField = $("name");
  const expField = $("exp");
  const cvvField = $("cvv");
  const errorBox = $("errorBox");
  const payBtn = $("payNow");
  const brandBox = $("cardBrand");
  const otpModal = $("otpModal");
  const successScreen = $("successScreen");

  // If essential elements missing, warn and avoid attaching listeners that will crash
  if (!cardInput || !nameField || !expField || !cvvField || !errorBox || !payBtn) {
    console.warn("payment-online: some form elements are missing; JS handlers partially disabled.");
  }

  let validName = false, validCard = false, validExp = false, validCVV = false;
  let generatedOtp = null;

  /**************** Luhn and helpers ****************/
  function luhnCheck(num) {
    let arr = (num + "").split("").reverse().map(x => parseInt(x));
    let sum = arr.reduce((acc, val, i) => {
      if (i % 2 !== 0) {
        val *= 2;
        if (val > 9) val -= 9;
      }
      return acc + val;
    }, 0);
    return sum % 10 === 0;
  }

  function highlight(field, state) {
    if (!field) return;
    field.classList.toggle("input-valid", state);
    field.classList.toggle("input-invalid", !state);
  }

  function triggerShake() {
    if (!errorBox) return;
    errorBox.classList.add("shake");
    setTimeout(() => errorBox.classList.remove("shake"), 300);
  }

  function error(msg) {
    if (!errorBox) return;
    errorBox.style.display = "block";
    errorBox.textContent = msg;
    triggerShake();
  }

  /**************** Card number spacing / brand ****************/
  if (cardInput) {
    cardInput.addEventListener("input", () => {
      let v = cardInput.value.replace(/\D/g, "").slice(0, 16);
      let spaced = v.match(/.{1,4}/g)?.join(" ") || "";
      cardInput.value = spaced;

      validCard = (v.length === 16) && luhnCheck(v);

      const s = v.charAt(0);
      if (brandBox) {
        brandBox.innerHTML =
          s === "4"
            ? `<img src="https://cdn-icons-png.flaticon.com/512/349/349228.png" height="28">`
          : s === "5"
            ? `<img src="https://cdn-icons-png.flaticon.com/512/196/196566.png" height="28">`
          : s === "6"
            ? `<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Rupay-Logo.png" height="28">`
          : "";
      }
      highlight(cardInput, validCard);
      // live preview
      const pCardNumber = $("pCardNumber");
      if (pCardNumber) pCardNumber.textContent = cardInput.value || "#### #### #### ####";
    });
  }

  /**************** Name validation ****************/
  if (nameField) {
    nameField.addEventListener("input", () => {
      validName = nameField.value.trim().length >= 3;
      highlight(nameField, validName);
      const pCardName = $("pCardName");
      if (pCardName) pCardName.textContent = nameField.value.trim() || "CARD HOLDER";
    });
  }

  /**************** Expiry validation ****************/
  if (expField) {
    expField.addEventListener("input", () => {
      let v = expField.value.replace(/\D/g, "").slice(0, 4);
      if (v.length >= 3) expField.value = v.slice(0, 2) + "/" + v.slice(2);
      else expField.value = v;
      validExp = /^(0[1-9]|1[0-2])\/\d{2}$/.test(expField.value);
      highlight(expField, validExp);
      const pCardExp = $("pCardExp");
      if (pCardExp) pCardExp.textContent = expField.value.trim() || "MM/YY";
    });
  }

  /**************** CVV validation and preview flip ****************/
  if (cvvField) {
    cvvField.addEventListener("input", () => {
      let v = cvvField.value.replace(/\D/g, "").slice(0, 3);
      cvvField.value = v;
      validCVV = v.length === 3;
      highlight(cvvField, validCVV);
      const pCVV = $("pCVV");
      if (pCVV) pCVV.textContent = cvvField.value || "•••";
    });

    cvvField.addEventListener("focus", () => {
      const previewCard = $("previewCard");
      if (previewCard) previewCard.classList.add("flipped");
    });

    cvvField.addEventListener("blur", () => {
      const previewCard = $("previewCard");
      if (previewCard) previewCard.classList.remove("flipped");
    });
  }

  /**************** Pay button click -> show OTP modal ****************/
  if (payBtn) {
    payBtn.addEventListener("click", () => {
      if (!validName || !validCard || !validExp || !validCVV) {
        error("Please enter valid card details.");
        return;
      }

      if (errorBox) errorBox.style.display = "none";

      generatedOtp = (Math.floor(1000 + Math.random() * 9000)).toString();
      console.log("OTP:", generatedOtp);

      document.querySelectorAll(".otp-box").forEach(i => (i.value = ""));
      if (otpModal) otpModal.style.display = "flex";
    });
  }

  /**************** OTP Verify -> AJAX POST to /api/checkout/ ****************/
  const verifyBtn = $("verifyOtp");
  if (verifyBtn) {
    verifyBtn.addEventListener("click", () => {
      let entered = Array.from(document.querySelectorAll(".otp-box"))
        .map(i => i.value)
        .join("");

      if (entered !== generatedOtp) {
        alert("Wrong OTP");
        return;
      }

      if (otpModal) otpModal.style.display = "none";
      if (successScreen) successScreen.style.display = "flex";

      // Retrieve order data and update
      let order = JSON.parse(localStorage.getItem("orderData")) || {};
      order.payment = "ONLINE";
      localStorage.setItem("orderData", JSON.stringify(order));

      // CSRF token helper below
      const csrftoken = getCookie("csrftoken");

      // build payload
      const payload = {
        name: order.name,
        email: order.email,
        mobile: order.mobile,
        address: order.address,
        pin: order.pin || "",
        items: order.items || [],
        total: order.total || order.total_amount || 0,
        payment: "ONLINE"
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
            window.location.href = "/thankyou?order_id=" + data.order_id;
          }, 1200);
        } else {
          alert("Payment failed: " + (data.error || "Unknown"));
        }
      })
      .catch(err => {
        console.error(err);
        alert("Network error during online payment.");
      });

    });
  }

}); // DOMContentLoaded end


/* ===========================
   CSRF COOKIE READER
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
