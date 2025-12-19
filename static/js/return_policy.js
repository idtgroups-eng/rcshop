// ------------------------------
// RCShop Return Policy Script
// ------------------------------

// Smooth scroll for internal links
document.addEventListener("DOMContentLoaded", () => {
    const smoothLinks = document.querySelectorAll("a[href^='#']");
    
    smoothLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            let targetId = link.getAttribute("href").substring(1);
            let target = document.getElementById(targetId);
            
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
});

// Highlight sections on scroll
window.addEventListener("scroll", () => {
    const sections = document.querySelectorAll("h2");

    sections.forEach(sec => {
        let position = sec.getBoundingClientRect();

        if (position.top >= 0 && position.top <= 250) {
            sec.style.color = "#00eaff";
        } else {
            sec.style.color = "#00ff9d";
        }
    });
});

// Button click animation
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector(".btn");

    if (btn) {
        btn.addEventListener("click", () => {
            btn.style.transform = "scale(0.95)";
            setTimeout(() => {
                btn.style.transform = "scale(1)";
            }, 150);
        });
    }
});
