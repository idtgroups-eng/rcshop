document.getElementById("searchInput").addEventListener("keyup", function(){
    let val = this.value.toLowerCase();
    document.querySelectorAll(".product-card").forEach(card=>{
        card.style.display = card.innerText.toLowerCase().includes(val) ? "" : "none";
    });
});


/* =========================================================
   🔥 FILTER BY CATEGORY (Top Buttons Inside PRODUCTS Page)
========================================================= */
document.querySelectorAll(".filter-btn").forEach(btn=>{
    btn.addEventListener("click", ()=>{

        document.querySelectorAll(".filter-btn").forEach(b=>b.classList.remove("active"));
        btn.classList.add("active");

        let cat = btn.dataset.category;

        document.querySelectorAll(".product-card").forEach(card=>{
            let match = (cat === "all" || card.dataset.category === cat);
            card.style.display = match ? "" : "none";
        });
    });
});

/* =========================================================
   🛒 ADD TO CART
========================================================= */
function addToCart(name, price, img){
    let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

    let exist = cart.find(item => item.name === name);

    if (exist) {
        exist.qty += 1;
    } else {
        cart.push({
            name: name,
            price: Number(price),
            img: img,
            qty: 1
        });
    }

    localStorage.setItem("cartItems", JSON.stringify(cart));
    updateCartCount();

    // Toast notification
    let note = document.createElement("div");
    note.style.cssText =
        "position:fixed;top:18px;right:18px;background:#00eaff;color:#000;padding:10px 14px;font-weight:700;border-radius:6px;z-index:99999;box-shadow:0 0 10px #00eaff;";
    note.innerText = "✔ Added to Cart";
    document.body.appendChild(note);

    setTimeout(() => note.remove(), 1500);
}


/* =========================================================
   ⚡ BUY NOW
========================================================= */
function buyNow(name, price, img){
    addToCart(name, price, img);
    window.location.href = "/cart/";
}

function openProductDetails(name, price, images, extra = {}) {
    let product = {
        name,
        price,
        images,
        highlights: extra.highlights || [],
        specs: extra.specs || []
    };

    localStorage.setItem("selectedProduct", JSON.stringify(product));

    // Django redirect
    window.location.href = "/product_details/";
}


/* =========================================================
   ❤️ WISHLIST 
========================================================= */
document.querySelectorAll(".wishlist").forEach(w=>{
    w.onclick = ()=> w.classList.toggle("active");
});


/* =========================================================
   🛒 UPDATE CART COUNTER
========================================================= */
function updateCartCount(){
    let cart = JSON.parse(localStorage.getItem("cartItems")) || [];
    if(document.getElementById("cartCount"))
        document.getElementById("cartCount").innerText = cart.length;
}
updateCartCount();


/* =========================================================
   🎤 VOICE SEARCH
========================================================= */
const mic = document.getElementById("micBtn");
mic.onclick = ()=>{
    let s = new webkitSpeechRecognition();
    s.lang="en-IN";
    s.onresult=e=>{
        searchInput.value = e.results[0][0].transcript;
        searchInput.dispatchEvent(new Event("keyup"));
    };
    s.start();
};


/* =========================================================
   📦 STOCK CONTROLLER
========================================================= */
function checkStock(){
    let stockDB = {
        "HP Pavilion 15":5,"Dell Inspiron 3511":3,"Lenovo IdeaPad Slim":4,"Acer Aspire 7":2,
        "MSI Curved Gaming Monitor":3,"Acer 24 Full HD Monitor":8,
        "Gaming Mechanical Keyboard":10,"Logitech K120":7,
        "Logitech G102 RGB":6,"HP Wireless Mouse":9,
        "Sandisk 64GB Pen Drive":11,"HP 32GB Pen Drive":14,
        "HDMI Cable 4K":12,"Type C Fast Cable":16,
        "HikVision CCTV Camera":3,"CP Plus CCTV Camera":4,
        "Laptop Cleaning Kit":8,"1080p Full HD Webcam":6
    };

    document.querySelectorAll(".product-card").forEach(card=>{
        let name = card.querySelector("h5").innerText.trim();
        if(stockDB[name] <= 0){
            card.querySelector(".add-btn").innerText="OUT OF STOCK";
            card.querySelector(".add-btn").disabled=true;
            card.querySelector(".buy-btn").style.display="none";
        }
    });
}
checkStock();


/* =========================================================
   🌐 SYNC NEW PRODUCTS FROM LOCALSTORAGE
========================================================= */
let newProducts = JSON.parse(localStorage.getItem("productsDB")) || [];
let mainBox = document.getElementById("productContainer");

newProducts.forEach(p=>{
    mainBox.innerHTML += `
    <div class="product-card" data-category="${p.category}">
        <img src="${p.imageURL}" />
        <h5 class="mt-2">${p.name}</h5>
        <p class="price">₹${p.price}</p>
        <p style="color:#444">${p.desc}</p>

        <div class="d-flex justify-content-between mt-2">
            <button class="add-btn" onclick="addToCart('${p.name}',${p.price},'${p.imageURL}')">Add</button>
            <button class="buy-btn" onclick="buyNow('${p.name}',${p.price},'${p.imageURL}')">Buy</button>
            <button class="view-btn"
                onclick="openProductDetails('${p.name}',${p.price},['${p.imageURL}'])">
                View
            </button>
        </div>
    </div>`;
});

// Read category from URL
const urlParams = new URLSearchParams(window.location.search);
const selectedCategory = urlParams.get("category");

// Show title
if (selectedCategory) {
    document.getElementById("categoryTitle").innerText =
        selectedCategory.toUpperCase();
}

// Wait until productsDB items added to page
setTimeout(() => {

    if (!selectedCategory) return;   // ⭐ If no category, do nothing

    const products = document.querySelectorAll(".product-card");


    products.forEach(card => {
        let prodCat = card.dataset.category?.toLowerCase();
        let selCat = selectedCategory?.toLowerCase();

        card.style.display =
            (!selectedCategory || selectedCategory === "all" || prodCat === selCat)
            ? ""
            : "none";
    });

}, 100); // delay so products load first

document.getElementById("productHamburger").addEventListener("click", function () {
  document.getElementById("productMenu").classList.toggle("show");
});
document.querySelectorAll(".dropdown-toggle").forEach(btn=>{
  btn.addEventListener("click",e=>{
    e.preventDefault();
    btn.parentElement.classList.toggle("open");
  });
});

document.querySelectorAll(".dropdown").forEach(d=>{
  d.addEventListener("mouseleave",()=>{
    d.classList.remove("open");
  });
});


