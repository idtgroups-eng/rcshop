document.addEventListener("DOMContentLoaded", () => {

    // ✅ ONLY PRODUCT DETAILS PAGE
    if (!window.location.pathname.includes("product_details")) return;

    const p = JSON.parse(localStorage.getItem("selectedProduct"));
    console.log("📦 Product Data:", p);   // DEBUG

    if (!p) {
        alert("Product data not found!");
        window.location.href = "/products/";
        return;
    }

    /* ================= BASIC DETAILS ================= */
    const nameEl  = document.getElementById("pName");
    const priceEl = document.getElementById("pPrice");

    if (nameEl)  nameEl.innerText  = p.name || "";
    if (priceEl) priceEl.innerText = "₹ " + (p.price || "") + "/-";

    /* ================= MAIN IMAGE (STRONG FIX) ================= */
    const mainImg = document.getElementById("mainProductImage");

    if (!mainImg) {
        console.error("❌ mainProductImage ID NOT FOUND in HTML");
        return;
    }

    // image path resolve
    let imgPath = "/static/images/no-image.png";

    if (p.images && Array.isArray(p.images) && p.images.length > 0) {
        imgPath = p.images[0];
    }

    // force load image (delay safe)
    setTimeout(() => {
        mainImg.src = imgPath;
        console.log("🖼️ Image loaded:", imgPath);
    }, 100);

    /* ================= THUMBNAILS ================= */
    const thumbBox = document.getElementById("thumbBox");

    if (thumbBox && p.images && p.images.length > 0) {
        thumbBox.innerHTML = "";

        p.images.slice(0, 4).forEach((img, i) => {
            const t = document.createElement("img");
            t.src = img;
            t.className = "thumbImg";
            t.style.cssText = `
                width:70px;
                height:70px;
                border:2px solid #00d5ff6e;
                border-radius:7px;
                cursor:pointer;
                object-fit:cover;
            `;
            t.onclick = () => {
                mainImg.style.opacity = "0";
                setTimeout(() => {
                    mainImg.src = img;
                    mainImg.style.opacity = "1";
                }, 150);
            };
            thumbBox.appendChild(t);
        });
    }

    /* ================= HIGHLIGHTS ================= */
    const hBox = document.querySelector(".box ul");
    if (hBox && p.highlights) {
        hBox.innerHTML = "";
        p.highlights.forEach(h => hBox.innerHTML += `<li>${h}</li>`);
    }

    /* ================= SPECS ================= */
    const sBoxes = document.querySelectorAll(".box ul");
    if (sBoxes.length > 1 && p.specs) {
        sBoxes[1].innerHTML = "";
        p.specs.forEach(s => sBoxes[1].innerHTML += `<li>${s}</li>`);
    }

});
