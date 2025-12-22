/* =========================
   ⭐ NAVBAR ACTIVE LINK
========================= */
const page = window.location.pathname.split("/").pop();

if (page === "" || page.includes("index"))
    document.getElementById("nav-home")?.classList.add("active");

if (page.includes("products"))
    document.getElementById("nav-products")?.classList.add("active");

if (page.includes("about"))
    document.getElementById("nav-about")?.classList.add("active");

if (page.includes("contact"))
    document.getElementById("nav-contact")?.classList.add("active");



/* =========================
   ⭐ CART COUNTER
========================= */
function updateCartCounter() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    const counter = document.getElementById("cartCount");

    if (counter) counter.textContent = total;
}
updateCartCounter();



/* =========================
   ⭐ ADD TO CART FUNCTION
========================= */
function addToCart(name, price, image, category) {

    // Always use the unified key "cartItems"
    let cart = JSON.parse(localStorage.getItem("cartItems")) || [];

    // Check if product already exists
    let existing = cart.find(item => item.name === name);

    if (existing) {
        existing.qty = (existing.qty || existing.quantity || 0) + 1;
    } else {
        cart.push({
            name: name,
            price: Number(price),
            img: image,
            category: category,
            qty: 1
        });
    }

    // Save updated cart
    localStorage.setItem("cartItems", JSON.stringify(cart));

    updateCartCounter();

    alert(name + " added to cart!");
}

/* =========================
   ⭐ AUTO CONNECT ADD TO CART BUTTONS
========================= */
document.querySelectorAll(".add-to-cart").forEach(btn => {
    btn.addEventListener("click", function () {
        let card = this.closest(".product-card");
        let name = card.dataset.name;
        let category = card.dataset.category;
        let price = parseInt(card.querySelector("p").innerText.replace("₹", ""));
        let image = card.querySelector("img").src;

        addToCart(name, price, image, category);
    });
});



/* =========================
   ⭐ SIMPLE COUNTDOWN TIMER
========================= */
(function () {
    const el = document.getElementById("deal-timer");
    if (!el) return;

    let h = 6, m = 12, s = 45;

    function pad(v) { return v.toString().padStart(2, "0"); }

    function tick() {
        s--;
        if (s < 0) { s = 59; m--; }
        if (m < 0) { m = 59; h--; }
        if (h < 0) { h = 0; m = 0; s = 0; }

        el.textContent = pad(h) + ":" + pad(m) + ":" + pad(s);
    }

    setInterval(tick, 1000);
})();



/* =========================
   ⭐ SEARCH FILTER (Featured Products)
========================= */
const searchBox = document.getElementById("searchBox");
const cards = document.querySelectorAll(".featured-products .product-card");

searchBox?.addEventListener("keyup", () => {
    let text = searchBox.value.toLowerCase();

    cards.forEach(card => {
        let name = card.dataset.name.toLowerCase();
        card.parentElement.style.display = name.includes(text) ? "block" : "none";
    });
});



/* =========================
   ⭐ PRODUCT DETAILS PAGE REDIRECT
========================= */
/* =========================
   ⭐ PRODUCT DETAILS PAGE REDIRECT (FIXED)
========================= */
function openProductDetails(name, price, images, extraData) {

    let product = {
        name: name,
        price: Number(price),   // ✅ IMPORTANT FIX
        images: images,
        highlights: extraData.highlights,
        specs: extraData.specs
    };

    localStorage.setItem("selectedProduct", JSON.stringify(product));

    window.location.href = "/product_details/";
}

/* =========================
   ⭐ HERO SLIDER
========================= */
let index = 0;
let slides = document.querySelectorAll(".slide");
let dotsBox = document.querySelector(".dots");

// Create dots equal to number of slides
if (dotsBox && slides.length > 0) {
    slides.forEach((_, i) => {
        let d = document.createElement("span");
        d.onclick = () => goToSlide(i);
        dotsBox.appendChild(d);
    });
}

function showSlide(n) {
    slides.forEach(s => s.classList.remove("active"));
    slides[n].classList.add("active");
    updateDots();
}

function nextSlide() {
    index = (index + 1) % slides.length;
    showSlide(index);
}

function prevSlide() {
    index = (index - 1 + slides.length) % slides.length;
    showSlide(index);
}

function goToSlide(n) {
    index = n;
    showSlide(n);
}

function updateDots() {
    let dots = document.querySelectorAll(".dots span");
    dots.forEach(d => d.classList.remove("active-dot"));
    dots[index].classList.add("active-dot");
}

// Auto slide every 5 seconds
setInterval(nextSlide, 5000);

// ================= MOBILE HAMBURGER MENU =================
const hamburger = document.getElementById("hamburgerBtn");
const mobileMenu = document.getElementById("mobileMenu");

hamburger.addEventListener("click", () => {
  mobileMenu.classList.toggle("show");
});
document.addEventListener("click", (e) => {
  if (
    !mobileMenu.contains(e.target) &&
    !hamburger.contains(e.target)
  ) {
    mobileMenu.classList.remove("show");
  }
});
