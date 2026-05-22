// Theme Toggler for Light / Dark Mode

function toggleTheme() {
    const htmlElement = document.documentElement;
    const currentTheme = htmlElement.getAttribute("data-bs-theme") || "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    htmlElement.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById("themeIcon");
    if (icon) {
        if (theme === "dark") {
            icon.className = "fa-solid fa-sun";
            icon.style.color = "#ffb300"; // Warm yellow for sun
        } else {
            icon.className = "fa-solid fa-moon";
            icon.style.color = "#4f46e5"; // Cool indigo for moon
        }
    }
}

// Apply theme as early as possible
(function () {

    const savedTheme = localStorage.getItem("theme");

    // Default theme = dark
    const themeToApply = savedTheme || "dark";

    document.documentElement.setAttribute("data-bs-theme", themeToApply);

})();

// Once DOM is fully loaded, update the theme toggle icon
document.addEventListener("DOMContentLoaded", () => {
    const activeTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
    updateThemeIcon(activeTheme);
});