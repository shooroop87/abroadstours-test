// backend/core/static/js/mobile-tour-enhancements.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Инициализация мобильных улучшений для туров');

    // === МОБИЛЬНАЯ ПАНЕЛЬ БРОНИРОВАНИЯ ===
    initMobileBookingBar();
    
    // === FAQ АККОРДЕОН ===
    initFAQAccordion();
    
    // === МОБИЛЬНОЕ МЕНЮ FIXES ===
    initMobileMenuFixes();
    
    // === ГАЛЕРЕЯ УЛУЧШЕНИЯ ===
    initGalleryEnhancements();
});

function initMobileBookingBar() {
    const openButton = document.getElementById("openBooking");
    const closeButton = document.getElementById("closeBooking");
    const modal = document.getElementById("bookingModal");
    const whatsappButton = document.querySelector('.ht-ctc');

    if (openButton && closeButton && modal) {
        console.log('📱 Инициализация мобильной панели бронирования');

        openButton.addEventListener("click", function() {
            modal.classList.add("open");
            document.body.classList.add("modal-open");
            
            // Скрываем WhatsApp кнопку когда открыт модал
            if (whatsappButton) {
                whatsappButton.style.display = 'none';
            }
            
            console.log('📱 Модал бронирования открыт');
        });

        closeButton.addEventListener("click", function() {
            modal.classList.remove("open");
            document.body.classList.remove("modal-open");
            
            // Показываем WhatsApp кнопку обратно
            if (whatsappButton) {
                whatsappButton.style.display = 'block';
            }
            
            console.log('📱 Модал бронирования закрыт');
        });

        // Закрытие по клику вне модала
        modal.addEventListener("click", function(e) {
            if (e.target === this) {
                this.classList.remove("open");
                document.body.classList.remove("modal-open");
                
                if (whatsappButton) {
                    whatsappButton.style.display = 'block';
                }
            }
        });

        // Закрытие по Escape
        document.addEventListener("keydown", function(e) {
            if (e.key === "Escape" && modal.classList.contains("open")) {
                modal.classList.remove("open");
                document.body.classList.remove("modal-open");
                
                if (whatsappButton) {
                    whatsappButton.style.display = 'block';
                }
            }
        });
    }
}

function initFAQAccordion() {
    const accordionItems = document.querySelectorAll('.accordion__item');
    
    accordionItems.forEach(item => {
        const button = item.querySelector('.accordion__button');
        const content = item.querySelector('.accordion__content');
        
        if (button && content) {
            button.addEventListener('click', function() {
                const isActive = item.classList.contains('is-active');
                
                // Закрываем все другие аккордеоны
                accordionItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('is-active');
                        const otherContent = otherItem.querySelector('.accordion__content');
                        if (otherContent) {
                            otherContent.style.maxHeight = null;
                        }
                    }
                });
                
                // Переключаем текущий
                if (isActive) {
                    item.classList.remove('is-active');
                    content.style.maxHeight = null;
                } else {
                    item.classList.add('is-active');
                    content.style.maxHeight = content.scrollHeight + "px";
                }
                
                console.log('❓ FAQ аккордеон переключен');
            });
        }
    });
}

function initMobileMenuFixes() {
    const menuButton = document.querySelector('.js-menu-button');
    const menu = document.querySelector('.js-menu');
    const bookingBar = document.querySelector('.booking-cta-wrapper');
    const whatsappButton = document.querySelector('.ht-ctc');
    
    if (menuButton && menu) {
        menuButton.addEventListener('click', function() {
            const isMenuOpen = menu.classList.contains('is-active');
            
            setTimeout(() => {
                const isMenuOpenNow = menu.classList.contains('is-active');
                
                // Управляем видимостью элементов
                if (isMenuOpenNow) {
                    // Меню открыто - скрываем booking bar
                    if (bookingBar) {
                        bookingBar.style.display = 'none';
                    }
                    console.log('📱 Мобильное меню открыто');
                } else {
                    // Меню закрыто - показываем booking bar обратно
                    if (bookingBar && window.innerWidth <= 768) {
                        bookingBar.style.display = 'block';
                    }
                    console.log('📱 Мобильное меню закрыто');
                }
            }, 50);
        });
    }
}

function initGalleryEnhancements() {
    // Улучшения для галереи - ленивая загрузка и оптимизация
    const galleryImages = document.querySelectorAll('.tourSingleGrid__grid img');
    
    if ('loading' in HTMLImageElement.prototype) {
        // Браузер поддерживает lazy loading
        galleryImages.forEach(img => {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
    } else {
        // Полифилл для старых браузеров
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        galleryImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Добавляем плавные переходы для изображений
    galleryImages.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        
        img.addEventListener('error', function() {
            console.warn('⚠️ Ошибка загрузки изображения:', this.src);
            this.src = '/static/img/tours/00_bg_general/default-tour.webp';
        });
    });
    
    console.log('🖼️ Галерея инициализирована');
}

// === ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ===

// Функция для копирования в буфер обмена
window.copyToClipboard = function(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Ссылка скопирована в буфер обмена!');
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
};

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Ссылка скопирована в буфер обмена!');
    } catch (err) {
        console.error('Ошибка копирования:', err);
        showNotification('Не удалось скопировать ссылку');
    }
    
    document.body.removeChild(textArea);
}

// Показ уведомлений
function showNotification(message, type = 'success') {
    // Удаляем существующие уведомления
    const existingNotifications = document.querySelectorAll('.toast-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#46b450' : '#dc3232'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Автоудаление
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Отслеживание скролла для мобильной панели
let lastScrollTop = 0;
window.addEventListener('scroll', function() {
    const bookingBar = document.querySelector('.booking-cta-wrapper');
    if (!bookingBar || window.innerWidth > 768) return;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop && scrollTop > 100) {
        // Скролл вниз - скрываем панель
        bookingBar.style.transform = 'translateY(100%)';
    } else {
        // Скролл вверх - показываем панель
        bookingBar.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
}, { passive: true });

// Улучшение производительности на мобильных устройствах
if (window.innerWidth <= 768) {
    // Отключаем анимации на слабых устройствах
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) {
        document.documentElement.style.setProperty('--animation-duration', '0s');
    }
    
    // Оптимизация для touch событий
    document.addEventListener('touchstart', function() {}, { passive: true });
    document.addEventListener('touchmove', function() {}, { passive: true });
}

console.log('✅ Мобильные улучшения загружены');