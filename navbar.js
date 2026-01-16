// Navigation Bar Component - Version corrigée sans duplication
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la navbar...');
    
    // Vérifier s'il y a déjà une navbar dans le HTML
    const existingNavbar = document.getElementById('navbar');
    const existingHeader = document.querySelector('header');
    
    if (existingNavbar) {
        console.log('Navbar existante détectée, conversion en navbar dynamique');
        convertExistingNavbar(existingNavbar);
    } else if (existingHeader) {
        console.log('Header existant détecté, conversion en navbar');
        convertHeaderToNavbar(existingHeader);
    } else {
        console.log('Aucune navbar existante, création d\'une nouvelle navbar');
        createNewNavbar();
    }
    
    // Ajouter les styles CSS nécessaires
    addNavbarStyles();
    
    // Initialiser les fonctionnalités
    initializeNavbarFeatures();
});

function convertExistingNavbar(navbarElement) {
    // Convertir la navbar existante en navbar dynamique
    navbarElement.classList.add('dynamic-navbar');
    navbarElement.style.position = 'fixed';
    navbarElement.style.top = '0';
    navbarElement.style.left = '0';
    navbarElement.style.right = '0';
    navbarElement.style.zIndex = '1000';
    navbarElement.style.background = '#fff';
    navbarElement.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
    
    // S'assurer qu'elle a la structure correcte
    if (!navbarElement.querySelector('.nav-container')) {
        const container = document.createElement('div');
        container.className = 'nav-container';
        container.innerHTML = navbarElement.innerHTML;
        navbarElement.innerHTML = '';
        navbarElement.appendChild(container);
    }
}

function convertHeaderToNavbar(headerElement) {
    // Convertir le header en navbar
    headerElement.id = 'navbar';
    headerElement.classList.add('dynamic-navbar');
    headerElement.style.position = 'fixed';
    headerElement.style.top = '0';
    headerElement.style.left = '0';
    headerElement.style.right = '0';
    headerElement.style.zIndex = '1000';
    headerElement.style.background = '#fff';
    headerElement.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
    headerElement.style.marginTop = '0';
}

function createNewNavbar() {
    // Créer une nouvelle navbar avec le logo cohérent
    const navbarHTML = `
        <nav class="navbar dynamic-navbar" id="navbar">
            <div class="nav-container">
                <div class="nav-logo">
                    <a href="index">
                        <div class="logo">Expert<span>IA</span> Suisse</div>
                    </a>
                </div>
                <div class="nav-menu" id="navMenu">
                    <a href="/" class="nav-link">Accueil</a>
                    <a href="contact" class="nav-link">Contact</a>
                    <a href="mentions-legales" class="nav-link">Mentions Légales</a>
                    <a href="index#pricing" class="nav-link">Télécharger</a>
                </div>
                <div class="nav-toggle" id="navToggle">
                    <span class="bar"></span>
                    <span class="bar"></span>
                    <span class="bar"></span>
                </div>
            </div>
        </nav>
    `;
    
    document.body.insertAdjacentHTML('afterbegin', navbarHTML);
}

function addNavbarStyles() {
    const styles = `
        <style>
            /* Navbar professionnelle avec structure 3-zones */
            .dynamic-navbar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #fff;
                box-shadow: 0 2px 20px rgba(0,0,0,0.08);
                z-index: 1000;
                transition: all 0.3s ease;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .dynamic-navbar.scrolled {
                box-shadow: 0 4px 30px rgba(0,0,0,0.1);
            }
            
            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                min-height: 80px;
                gap: 40px;
            }
            
            /* Zones de navigation */
            .nav-zone {
                display: flex;
                align-items: center;
            }
            
            .nav-zone-left {
                flex: 0 0 auto;
                justify-content: flex-start;
            }
            
            .nav-zone-center {
                flex: 1 1 auto;
                justify-content: center;
            }
            
            .nav-zone-right {
                flex: 0 0 auto;
                justify-content: flex-end;
            }
            
            /* Logo */
            .nav-logo .logo {
                font-size: 24px;
                font-weight: 700;
                color: #1e40af;
                text-decoration: none;
                white-space: nowrap;
            }
            
            .nav-logo .logo span {
                color: #dc2626;
            }
            
            /* Menu de navigation */
            .nav-menu {
                display: flex;
                align-items: center;
                gap: 40px;
                margin: 0;
                padding: 0;
            }
            
            .nav-link {
                color: #374151;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                transition: all 0.3s ease;
                position: relative;
                padding: 12px 0;
                white-space: nowrap;
            }
            
            .nav-link:hover {
                color: #1e40af;
            }
            
            /* Soulignement actif professionnel */
            .nav-link::after {
                content: '';
                position: absolute;
                bottom: 6px;
                left: 0;
                width: 0;
                height: 2px;
                background: #E30613;
                transition: width 0.3s ease;
                border-radius: 1px;
            }
            
            .nav-link:hover::after {
                width: 100%;
            }
            
            .nav-link.active {
                color: #1e40af;
            }
            
            .nav-link.active::after {
                width: 100%;
                background: #E30613;
            }
            
            /* Bouton Connexion */
            .login-button {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 14px;
                white-space: nowrap;
            }
            
            .login-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(30, 64, 175, 0.3);
            }
            
            /* Burger menu */
            .nav-toggle {
                display: none;
                flex-direction: column;
                cursor: pointer;
                padding: 8px;
                margin-left: 20px;
            }
            
            .bar {
                width: 25px;
                height: 3px;
                background: #374151;
                margin: 3px 0;
                transition: 0.3s ease;
                border-radius: 2px;
            }
            
            /* Responsive mobile */
            @media screen and (max-width: 768px) {
                .nav-container {
                    padding: 0 20px;
                    gap: 20px;
                }
                
                .nav-zone-center {
                    display: none;
                }
                
                .nav-menu {
                    position: fixed;
                    left: -100%;
                    top: 80px;
                    flex-direction: column;
                    background: #fff;
                    width: 100%;
                    text-align: center;
                    transition: 0.3s ease;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    padding: 20px 0;
                    gap: 0;
                    border-top: 1px solid #e5e7eb;
                }
                
                .nav-menu.active {
                    left: 0;
                }
                
                .nav-link {
                    padding: 20px;
                    width: 100%;
                    display: block;
                    border-bottom: 1px solid #f3f4f6;
                }
                
                .nav-link:last-child {
                    border-bottom: none;
                }
                
                .nav-toggle {
                    display: flex;
                }
                
                .nav-toggle.active .bar:nth-child(2) {
                    opacity: 0;
                }
                
                .nav-toggle.active .bar:nth-child(1) {
                    transform: translateY(6px) rotate(45deg);
                }
                
                .nav-toggle.active .bar:nth-child(3) {
                    transform: translateY(-6px) rotate(-45deg);
                }
            }
            
            /* Animation au scroll */
            @keyframes slideDown {
                from {
                    transform: translateY(-100%);
                }
                to {
                    transform: translateY(0);
                }
            }
            
            .dynamic-navbar {
                animation: slideDown 0.5s ease-out;
            }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', styles);
}

function initializeNavbarFeatures() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (!navbar || !navToggle || !navMenu) {
        console.warn('Éléments de navbar non trouvés');
        return;
    }
    
    // Créer l'espaceur
    const spacer = document.createElement('div');
    spacer.className = 'navbar-spacer';
    spacer.style.height = '80px';
    navbar.parentNode.insertBefore(spacer, navbar.nextSibling);
    
    // Toggle mobile menu
    navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Active link highlighting
    const currentPage = window.location.pathname.split('/').pop();
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Ajuster dynamiquement la hauteur de l'espaceur
    function adjustSpacerHeight() {
        const navbarHeight = navbar.offsetHeight;
        spacer.style.height = navbarHeight + 'px';
    }
    
    adjustSpacerHeight();
    window.addEventListener('resize', adjustSpacerHeight);
}
