// Исправленная версия whatsapp.js

(function() {
    'use strict';
    
    console.log('WhatsApp script initializing...');
    
    // Проверяем, не был ли скрипт уже инициализирован
    if (window.WhatsAppManager) {
        console.log('WhatsApp script already initialized');
        return;
    }
    
    // Функция для позиционирования кнопки относительно footer
    function positionWhatsAppButton() {
        const button = document.getElementById('ht-ctc-chat');
        const footer = document.querySelector('footer');
        
        if (!button) {
            console.warn('WhatsApp button not found for positioning');
            return;
        }
        
        // Проверяем, разрешено ли показывать кнопку (cookie consent)
        if (!isCookieConsentGiven()) {
            console.log('Cookie consent not given, hiding button');
            button.style.display = 'none';
            return;
        }
        
        // Если footer не найден, используем фиксированное позиционирование
        if (!footer) {
            button.style.position = 'fixed';
            button.style.bottom = '35px';
            button.style.right = '25px';
            return;
        }
        
        const footerRect = footer.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const buttonHeight = 80; // Примерная высота кнопки с отступами
        
        // Если footer виден на экране
        if (footerRect.top < windowHeight) {
            // Позиционируем кнопку над footer
            const distanceFromTop = footerRect.top - buttonHeight;
            button.style.position = 'fixed';
            button.style.bottom = 'auto';
            button.style.top = Math.max(distanceFromTop, 20) + 'px';
            button.style.right = '25px';
        } else {
            // Footer не виден - обычное фиксированное позиционирование
            button.style.position = 'fixed';
            button.style.bottom = '35px';
            button.style.top = 'auto';
            button.style.right = '25px';
        }
    }

    // Функция проверки согласия на cookies
    function isCookieConsentGiven() {
        // Проверяем наличие класса на body
        if (document.body.classList.contains('cookie-consent-given')) {
            return true;
        }
        
        // Дополнительная проверка через localStorage
        try {
            const stored = localStorage.getItem('cookieConsents');
            if (stored) {
                const parsed = JSON.parse(stored);
                return parsed.hasConsented === true;
            }
        } catch (e) {
            console.warn('Error checking cookie consent:', e);
        }
        
        return false;
    }

    // НОВАЯ ФУНКЦИЯ для анимации скрытия текста
    function hideTextWithDelay() {
        const textElement = document.querySelector('.ctc_cta');
        if (!textElement) return;
        
        console.log('Starting text hide animation...');
        
        // Через 1 секунду после появления кнопки начинаем скрывать текст
        setTimeout(() => {
            textElement.classList.add('hide-text');
            console.log('Text hiding animation started');
            
            // Через еще 0.5 секунды (время анимации) полностью убираем элемент
            setTimeout(() => {
                textElement.classList.add('completely-hidden');
                console.log('Text completely hidden');
            }, 500);
        }, 1000);
    }

    // Функция инициализации WhatsApp кнопки
    function initializeWhatsAppButton() {
        const whatsappButton = document.getElementById('ht-ctc-chat');
        
        if (whatsappButton) {
            console.log('WhatsApp button found, checking cookie consent...');
            
            // Проверяем согласие на cookies
            if (!isCookieConsentGiven()) {
                console.log('Cookie consent not given, keeping button hidden');
                whatsappButton.style.display = 'none';
                return false;
            }
            
            console.log('Cookie consent given, initializing button...');
            
            // Устанавливаем начальную позицию
            positionWhatsAppButton();
            
            // Добавляем обработчики событий только если их еще нет
            if (!whatsappButton.hasAttribute('data-listeners-added')) {
                // Обновляем позицию при прокрутке
                window.addEventListener('scroll', positionWhatsAppButton);
                
                // Обновляем позицию при изменении размера окна
                window.addEventListener('resize', positionWhatsAppButton);
                
                // Помечаем, что обработчики добавлены
                whatsappButton.setAttribute('data-listeners-added', 'true');
                
                console.log('WhatsApp button event listeners added');
            }
            
            return true;
        } else {
            console.warn('WhatsApp button not found during initialization');
            return false;
        }
    }

    // Функция ожидания появления кнопки с проверкой согласия
    function waitForButtonAndConsent(maxAttempts = 30, interval = 200) {
        let attempts = 0;
        
        const checkInterval = setInterval(() => {
            attempts++;
            
            // Проверяем наличие кнопки и согласия
            const button = document.getElementById('ht-ctc-chat');
            const consentGiven = isCookieConsentGiven();
            
            if (button && consentGiven) {
                if (initializeWhatsAppButton()) {
                    clearInterval(checkInterval);
                    console.log('WhatsApp button initialized successfully');
                }
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                console.log('WhatsApp initialization timeout. Button:', !!button, 'Consent:', consentGiven);
            }
        }, interval);
    }

    // Функция для анимации heartBeat
    function addHeartBeatAnimation() {
        const button = document.getElementById('ht-ctc-chat');
        if (button && isCookieConsentGiven()) {
            // Убираем класс анимации
            button.classList.remove('ht_ctc_an_heartBeat');
            
            // Добавляем обратно через небольшую задержку
            setTimeout(() => {
                button.classList.add('ht_ctc_an_heartBeat');
            }, 100);
            
            // Убираем через время анимации
            setTimeout(() => {
                button.classList.remove('ht_ctc_an_heartBeat');
            }, 1300);
        }
    }

    // Основная функция инициализации
    function initialize() {
        console.log('Starting WhatsApp button initialization...');
        
        // Если DOM уже готов, инициализируем сразу
        if (document.readyState === 'loading') {
            // DOM еще загружается
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded, initializing WhatsApp button...');
                waitForButtonAndConsent();
            });
        } else {
            // DOM уже готов (скрипт загружен динамически)
            console.log('DOM already loaded, initializing WhatsApp button immediately...');
            waitForButtonAndConsent();
        }
    }

    // Создаем глобальный менеджер
    window.WhatsAppManager = {
        initialize: initialize,
        positionButton: positionWhatsAppButton,
        addHeartBeat: addHeartBeatAnimation,
        checkConsent: isCookieConsentGiven,
        
        // Функция для ручной переинициализации
        reinitialize: function() {
            console.log('Reinitializing WhatsApp button...');
            waitForButtonAndConsent(20, 200);
        },
        
        // ОБНОВЛЕННАЯ функция показа кнопки (вызывается из Cookie Manager)
        showButton: function() {
            console.log('WhatsApp Manager: Showing button...');
            const button = document.getElementById('ht-ctc-chat');
            if (button) {
                // Проверяем согласие перед показом
                if (!isCookieConsentGiven()) {
                    console.log('Cannot show button - no cookie consent');
                    return;
                }
                
                button.style.display = 'block';
                
                // Добавляем класс для анимации
                setTimeout(() => {
                    button.classList.add('show');
                }, 50);
                
                // Позиционируем кнопку
                setTimeout(positionWhatsAppButton, 100);
                
                // НОВОЕ: Запускаем анимацию скрытия текста
                setTimeout(hideTextWithDelay, 100);
                
                console.log('WhatsApp button shown and positioned');
            } else {
                console.warn('WhatsApp button element not found for showing');
            }
        },
        
        // Функция скрытия кнопки
        hideButton: function() {
            const button = document.getElementById('ht-ctc-chat');
            if (button) {
                button.style.display = 'none';
                button.classList.remove('show');
                
                // Сбрасываем состояние текста при скрытии кнопки
                const textElement = document.querySelector('.ctc_cta');
                if (textElement) {
                    textElement.classList.remove('hide-text', 'completely-hidden');
                }
                
                console.log('WhatsApp button hidden');
            }
        },
        
        // НОВАЯ функция для показа текста обратно
        showText: function() {
            const textElement = document.querySelector('.ctc_cta');
            if (textElement) {
                textElement.classList.remove('hide-text', 'completely-hidden');
                console.log('WhatsApp text shown');
            }
        },
        
        // НОВАЯ функция для скрытия текста
        hideText: function() {
            hideTextWithDelay();
        },
        
        // Функция для отладки
        debug: function() {
            const button = document.getElementById('ht-ctc-chat');
            const textElement = document.querySelector('.ctc_cta');
            console.log('=== WHATSAPP MANAGER DEBUG ===');
            console.log('Button exists:', !!button);
            console.log('Text element exists:', !!textElement);
            console.log('Cookie consent given:', isCookieConsentGiven());
            console.log('Body has cookie-consent-given class:', document.body.classList.contains('cookie-consent-given'));
            if (button) {
                console.log('Button styles:', {
                    display: window.getComputedStyle(button).display,
                    position: window.getComputedStyle(button).position,
                    bottom: window.getComputedStyle(button).bottom,
                    top: window.getComputedStyle(button).top,
                    right: window.getComputedStyle(button).right,
                    opacity: window.getComputedStyle(button).opacity
                });
                console.log('Button classes:', button.className);
                console.log('Listeners added:', button.hasAttribute('data-listeners-added'));
            }
            if (textElement) {
                console.log('Text element classes:', textElement.className);
                console.log('Text element styles:', {
                    display: window.getComputedStyle(textElement).display,
                    opacity: window.getComputedStyle(textElement).opacity,
                    transform: window.getComputedStyle(textElement).transform
                });
            }
            console.log('Footer exists:', !!document.querySelector('footer'));
            console.log('Window size:', { width: window.innerWidth, height: window.innerHeight });
            console.log('Is mobile:', window.innerWidth <= 480);
            console.log('=== END DEBUG ===');
        }
    };

    // Запускаем инициализацию
    initialize();

    // Устанавливаем интервал для анимации heartBeat каждые 10 секунд
    let heartBeatInterval = setInterval(addHeartBeatAnimation, 10000);

    // Очистка интервалов при выгрузке страницы
    window.addEventListener('beforeunload', function() {
        if (heartBeatInterval) clearInterval(heartBeatInterval);
    });

    // Помечаем скрипт как загруженный
    if (document.currentScript) {
        document.currentScript.setAttribute('data-loaded', 'true');
    }
    
    console.log('WhatsApp script loaded successfully');

})();