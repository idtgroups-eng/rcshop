document.addEventListener("DOMContentLoaded", () => {

    // ✅ ONLY PRODUCT DETAILS PAGE
    if (!window.location.pathname.includes("product_details")) return;

    // ✅ Load Product Data from localStorage
    const p = JSON.parse(localStorage.getItem("selectedProduct"));
    console.log("📦 Product Data:", p);   // DEBUG

    // ✅ If No Product Found
    if (!p) {
        alert("Product data not found!");
        window.location.href = "/products/";
        return;
    }

    /* ================= BASIC DETAILS ================= */
    const nameEl  = document.getElementById("pName");
    const priceEl = document.getElementById("pPrice");

    if (nameEl)  nameEl.innerText  = p.name || "No Name";
    if (priceEl) priceEl.innerText = "₹ " + (p.price || "0") + "/-";


    /* ================= MAIN IMAGE (STRONG FIX) ================= */
    const mainImg = document.getElementById("mainProductImage");

    if (!mainImg) {
        console.error("❌ mainProductImage ID NOT FOUND in HTML");
        return;
    }

    // ✅ Default Fallback Image
    let imgPath = "/static/images/no-image.png";

    // ✅ Load First Product Image
    if (p.images && Array.isArray(p.images) && p.images.length > 0) {
        imgPath = p.images[0];
    }

    // ✅ Force Load Image (Delay Safe)
    setTimeout(() => {
        mainImg.src = imgPath;
        console.log("🖼️ Image loaded:", imgPath);
    }, 100);


    /* ================= THUMBNAILS ================= */
    const thumbBox = document.getElementById("thumbBox");

    if (thumbBox && p.images && p.images.length > 0) {

        thumbBox.innerHTML = "";

        // ✅ Max 4 Thumbnails Show
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
                transition:0.3s;
            `;

            // ✅ On Click Change Main Image
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
    const hBox = document.querySelectorAll(".box ul")[0];

    if (hBox && p.highlights && p.highlights.length > 0) {

        hBox.innerHTML = "";

        p.highlights.forEach(h => {
            hBox.innerHTML += `<li>${h}</li>`;
        });

    }


    /* ================= SPECS ================= */
    const sBoxes = document.querySelectorAll(".box ul")[1];

    if (sBoxes && p.specs && p.specs.length > 0) {

        sBoxes.innerHTML = "";

        p.specs.forEach(s => {
            sBoxes.innerHTML += `<li>${s}</li>`;
        });

    }

});
