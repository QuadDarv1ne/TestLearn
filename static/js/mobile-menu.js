// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
}

// Mobile submenu toggle (accordion)
function toggleMobileSubmenu(id) {
    const submenu = document.getElementById(id);
    const icon = document.getElementById(id + '-icon');
    
    if (submenu.classList.contains('hidden')) {
        submenu.classList.remove('hidden');
        if (icon) icon.style.transform = 'rotate(180deg)';
    } else {
        submenu.classList.add('hidden');
        if (icon) icon.style.transform = 'rotate(0deg)';
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const nav = document.querySelector('nav');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenu && !nav.contains(event.target) && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
    }
});
