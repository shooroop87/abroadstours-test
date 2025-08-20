// whatsapp.js — финальная версия
(function () {
  'use strict';

  console.log('WhatsApp script initializing...');

  // Не допускаем повторное подключение скрипта
  if (window.WhatsAppManager && window.WhatsAppManager.__ready) {
    console.log('WhatsApp script already initialized');
    return;
  }

  // ===== ВНУТРЕННИЕ ФЛАГИ/КОНСТАНТЫ =========================================
  let waInited = false;              // защита от двойной инициализации
  const POLL_INTERVAL = 100;         // мс
  const MAX_WAIT = 10000;            // мс ожидание прелоадера
  const EXTRA_SAFETY_DELAY = 500;    // мс «на всякий случай» после прелоадера
  const BTN_ID = 'ht-ctc-chat';

  // ===== ПОЛЕЗНЫЕ ХЕЛПЕРЫ ====================================================

  // Проверяем, завершён ли прелоадер
  function isPreloaderComplete() {
    if (document.body.classList.contains('preloader-done')) return true;
    // Если на странице вообще нет прелоадера — считаем, что ждать нечего.
    return !document.querySelector('.js-preloader');
  }

  // Ждём, пока прелоадер «доиграет»
  function waitForPreloaderToComplete(callback, maxWait = MAX_WAIT) {
    const startTime = Date.now();

    const tick = setInterval(() => {
      const elapsed = Date.now() - startTime;

      if (isPreloaderComplete()) {
        clearInterval(tick);
        console.log('Preloader fully completed after', elapsed, 'ms');
        setTimeout(() => {
          console.log('Additional delay complete, executing callback');
          callback();
        }, EXTRA_SAFETY_DELAY);
      } else if (elapsed > maxWait) {
        clearInterval(tick);
        console.log('Preloader wait timeout, proceeding anyway');
        callback();
      }
    }, POLL_INTERVAL);
  }

  function isCookieConsentGiven() {
    // быстрый флажок от твоего кода куки-баннера
    if (document.body.classList.contains('cookie-consent-given')) {
      return true;
    }

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

  // Позиционирование кнопки относительно футера
  function positionWhatsAppButton() {
    const button = document.getElementById(BTN_ID);
    const footer = document.querySelector('footer');

    if (!button) {
      console.warn('WhatsApp button not found for positioning');
      return;
    }

    if (!isCookieConsentGiven()) {
      button.style.display = 'none';
      return;
    }

    // Базовое фиксированное позиционирование
    button.style.position = 'fixed';
    button.style.right = '25px';

    if (!footer) {
      button.style.bottom = '35px';
      button.style.top = 'auto';
      return;
    }

    const footerRect = footer.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const buttonHeight = 80;

    if (footerRect.top < windowHeight) {
      // футер заходит в вьюпорт — поднимаем кнопку выше него
      const distanceFromTop = footerRect.top - buttonHeight;
      button.style.top = Math.max(distanceFromTop, 20) + 'px';
      button.style.bottom = 'auto';
    } else {
      // футер не виден — ставим стандартно снизу
      button.style.bottom = '35px';
      button.style.top = 'auto';
    }
  }

  // Плавное скрытие текста «cta»
  function hideTextWithDelay() {
    const textElement = document.querySelector('.ctc_cta');
    if (!textElement) return;

    setTimeout(() => {
      textElement.classList.add('hide-text');
      setTimeout(() => {
        textElement.classList.add('completely-hidden');
      }, 500);
    }, 1000);
  }

  // Однократный запуск реальной инициализации кнопки после прелоадера
  function initOnce() {
    if (waInited) return;
    waInited = true;
    initializeWhatsAppAfterPreloader();
  }

  // ===== ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ КНОПКИ ПОСЛЕ ПРЕЛОАДЕРА ======================

  function initializeWhatsAppAfterPreloader() {
    console.log('Initializing WhatsApp after preloader completion...');

    const whatsappButton = document.getElementById(BTN_ID);

    if (!whatsappButton) {
      console.warn('WhatsApp button not found');
      return;
    }

    if (!isCookieConsentGiven()) {
      console.log('No cookie consent, keeping button hidden');
      whatsappButton.style.display = 'none';
      return;
    }

    // Показываем кнопку; CSS-стоппер в теме/стилях должен не пускать её до preloader-done:
    // body:not(.preloader-done) #ht-ctc-chat { display: none !important; }
    whatsappButton.style.display = 'block';

    // Небольшая задержка для CSS-анимации появления
    setTimeout(() => {
      whatsappButton.classList.add('show');
    }, 100);

    // Позиционируем
    setTimeout(() => {
      positionWhatsAppButton();
    }, 200);

    // Прячем текст по таймингу
    setTimeout(() => {
      hideTextWithDelay();
    }, 300);

    // Навешиваем слушатели один раз
    if (!whatsappButton.hasAttribute('data-listeners-added')) {
      window.addEventListener('scroll', positionWhatsAppButton, { passive: true });
      window.addEventListener('resize', positionWhatsAppButton);
      window.addEventListener('orientationchange', positionWhatsAppButton);
      document.addEventListener('visibilitychange', () => {
        if (!document.hidden) positionWhatsAppButton();
      });
      whatsappButton.setAttribute('data-listeners-added', 'true');
    }

    console.log('WhatsApp button fully initialized');
  }

  // Лёгкая «пульсация» раз в 10 секунд
  function addHeartBeatAnimation() {
    const button = document.getElementById(BTN_ID);
    if (button && isCookieConsentGiven()) {
      button.classList.remove('ht_ctc_an_heartBeat');
      setTimeout(() => {
        button.classList.add('ht_ctc_an_heartBeat');
      }, 100);
      setTimeout(() => {
        button.classList.remove('ht_ctc_an_heartBeat');
      }, 1300);
    }
  }

  // ===== ГЛАВНАЯ ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ ======================================

  function initialize() {
    console.log('Starting WhatsApp initialization...');

    // Спрятать кнопку пока всё грузится
    const btn = document.getElementById(BTN_ID);
    if (btn) {
      btn.style.display = 'none';
      console.log('WhatsApp button hidden during initialization');
    }

    // Если прелоадер уже завершён, стартуем сразу
    if (isPreloaderComplete()) {
      initOnce();
      return;
    }

    // Подписка на явный сигнал от main.js
    window.addEventListener('preloader:done', initOnce, { once: true });

    // Запасной поллинг (если событие пролетит до подписки)
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        waitForPreloaderToComplete(initOnce);
      });
    } else {
      waitForPreloaderToComplete(initOnce);
    }
  }

  // ===== ГЛОБАЛЬНЫЙ МЕНЕДЖЕР (API) ===========================================

  window.WhatsAppManager = {
    __ready: true, // маркер одного подключения
    initialize,
    positionButton: positionWhatsAppButton,
    addHeartBeat: addHeartBeatAnimation,
    checkConsent: isCookieConsentGiven,

    reinitialize: function () {
      console.log('Manual reinitialize requested...');
      // Перезапуск с учётом прелоадера
      if (isPreloaderComplete()) {
        initOnce();
      } else {
        waitForPreloaderToComplete(initOnce);
      }
    },

    showButton: function () {
      console.log('Manual show button requested...');

      if (!isCookieConsentGiven()) {
        console.log('Cannot show button — no cookie consent');
        return;
      }

      if (isPreloaderComplete()) {
        initOnce();
      } else {
        console.log('Preloader still active, waiting...');
        waitForPreloaderToComplete(initOnce);
      }
    },

    hideButton: function () {
      const button = document.getElementById(BTN_ID);
      if (button) {
        button.style.display = 'none';
        button.classList.remove('show');

        const textElement = document.querySelector('.ctc_cta');
        if (textElement) {
          textElement.classList.remove('hide-text', 'completely-hidden');
        }
        console.log('WhatsApp button hidden');
      }
    },

    showText: function () {
      const textElement = document.querySelector('.ctc_cta');
      if (textElement) {
        textElement.classList.remove('hide-text', 'completely-hidden');
        console.log('WhatsApp text shown');
      }
    },

    hideText: function () {
      hideTextWithDelay();
    },

    // Быстрый отладчик
    debug: function () {
      const button = document.getElementById(BTN_ID);
      const textElement = document.querySelector('.ctc_cta');
      const preloader = document.querySelector('.js-preloader');

      console.log('=== WHATSAPP MANAGER DEBUG ===');
      console.log('Button exists:', !!button);
      console.log('Text element exists:', !!textElement);
      console.log('Preloader exists:', !!preloader);
      console.log('Cookie consent given:', isCookieConsentGiven());
      console.log('Preloader completed:', isPreloaderComplete());
      console.log('Body has cookie-consent-given class:', document.body.classList.contains('cookie-consent-given'));

      if (button) {
        const cs = window.getComputedStyle(button);
        console.log('Button styles:', {
          display: cs.display,
          position: cs.position,
          bottom: cs.bottom,
          top: cs.top,
          right: cs.right,
          opacity: cs.opacity
        });
        console.log('Button classes:', button.className);
        console.log('Listeners added:', button.hasAttribute('data-listeners-added'));
      }

      if (preloader) {
        const computedStyle = window.getComputedStyle(preloader);
        console.log('Preloader state:', {
          classes: preloader.className,
          display: computedStyle.display,
          opacity: computedStyle.opacity,
          visibility: computedStyle.visibility
        });
      }
      console.log('=== END DEBUG ===');
    }
  };

  // ===== ЗАПУСК ==============================================================
  try {
    initialize();
  } catch (e) {
    console.error('Initialize() failed:', e);
  }

  // Пульс сердца каждые 10 секунд
  let heartBeatInterval = setInterval(addHeartBeatAnimation, 10000);

  window.addEventListener('beforeunload', function () {
    if (heartBeatInterval) clearInterval(heartBeatInterval);
  });

  // Технический маркер загрузки скрипта
  if (document.currentScript) {
    document.currentScript.setAttribute('data-loaded', 'true');
  }

  console.log('WhatsApp script loaded successfully');
})();
