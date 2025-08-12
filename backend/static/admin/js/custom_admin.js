// backend/core/static/admin/js/custom_admin.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Loading custom WordPress-style admin...');
    
    // Добавляем иконки к заголовкам модулей
    addModuleIcons();
    
    // Улучшаем навигацию
    enhanceNavigation();
    
    // Добавляем статистику на главную страницу
    if (window.location.pathname.includes('/admin/')) {
        addDashboardStats();
    }
    
    // Улучшаем формы
    enhanceForms();
    
    // Добавляем уведомления
    enhanceMessages();
});

function addModuleIcons() {
    const moduleHeaders = document.querySelectorAll('.module h2, .module h3');
    
    moduleHeaders.forEach(header => {
        const text = header.textContent.toLowerCase();
        let icon = '';
        
        if (text.includes('blog') || text.includes('post')) {
            icon = '📝';
        } else if (text.includes('categor')) {
            icon = '📁';
        } else if (text.includes('comment')) {
            icon = '💬';
        } else if (text.includes('user')) {
            icon = '👤';
        } else if (text.includes('image') || text.includes('media')) {
            icon = '🖼️';
        } else if (text.includes('tag')) {
            icon = '🏷️';
        } else if (text.includes('auth')) {
            icon = '🔐';
        } else if (text.includes('site')) {
            icon = '🌐';
        } else {
            icon = '⚙️';
        }
        
        header.innerHTML = icon + ' ' + header.innerHTML;
    });
}

function enhanceNavigation() {
    // Добавляем хлебные крошки
    const breadcrumbs = document.querySelector('.breadcrumbs');
    if (breadcrumbs) {
        breadcrumbs.style.background = '#fff';
        breadcrumbs.style.borderBottom = '1px solid #ccd0d4';
        breadcrumbs.style.padding = '10px 20px';
        breadcrumbs.style.fontSize = '13px';
    }
    
    // Улучшаем кнопки навигации
    const navButtons = document.querySelectorAll('.button, input[type="submit"]');
    navButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

function addDashboardStats() {
    // Проверяем, находимся ли мы на главной странице админки
    if (!document.querySelector('#content h1') || 
        !document.querySelector('#content h1').textContent.includes('Site administration')) {
        return;
    }
    
    // Создаем блок статистики
    const statsHTML = `
        <div class="blog-admin-header">
            <h2 style="margin: 0; font-size: 24px;">🌍 Abroads Tours - Admin Dashboard</h2>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to your travel blog administration panel</p>
            <div class="blog-admin-stats">
                <div class="blog-stat-card">
                    <span class="blog-stat-number" id="posts-count">...</span>
                    <div class="blog-stat-label">Blog Posts</div>
                </div>
                <div class="blog-stat-card">
                    <span class="blog-stat-number" id="categories-count">...</span>
                    <div class="blog-stat-label">Categories</div>
                </div>
                <div class="blog-stat-card">
                    <span class="blog-stat-number" id="comments-count">...</span>
                    <div class="blog-stat-label">Comments</div>
                </div>
                <div class="blog-stat-card">
                    <span class="blog-stat-number" id="users-count">...</span>
                    <div class="blog-stat-label">Users</div>
                </div>
            </div>
        </div>
    `;
    
    const content = document.querySelector('#content');
    if (content) {
        content.insertAdjacentHTML('afterbegin', statsHTML);
        
        // Загружаем статистику
        loadDashboardStats();
    }
}

function loadDashboardStats() {
    // Симуляция загрузки статистики
    // В реальном проекте здесь был бы AJAX запрос
    setTimeout(() => {
        const stats = {
            posts: Math.floor(Math.random() * 50) + 10,
            categories: Math.floor(Math.random() * 10) + 3,
            comments: Math.floor(Math.random() * 200) + 50,
            users: Math.floor(Math.random() * 20) + 5
        };
        
        animateCounter('posts-count', stats.posts);
        animateCounter('categories-count', stats.categories);
        animateCounter('comments-count', stats.comments);
        animateCounter('users-count', stats.users);
    }, 500);
}

function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let currentValue = 0;
    const increment = targetValue / 20;
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = Math.floor(currentValue);
    }, 50);
}

function enhanceForms() {
    // Добавляем улучшения для форм
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], textarea');
    
    inputs.forEach(input => {
        // Добавляем анимацию фокуса
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 2px rgba(0, 115, 170, 0.2)';
            this.style.borderColor = '#0073aa';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = 'inset 0 1px 2px rgba(0,0,0,0.07)';
            this.style.borderColor = '#ccd0d4';
        });
    });
    
    // Улучшаем чекбоксы
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.style.accentColor = '#0073aa';
    });
}

function enhanceMessages() {
    // Добавляем автоматическое скрытие сообщений
    const messages = document.querySelectorAll('.messagelist li');
    
    messages.forEach((message, index) => {
        // Добавляем кнопку закрытия
        const closeButton = document.createElement('span');
        closeButton.innerHTML = '×';
        closeButton.style.cssText = `
            float: right;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            opacity: 0.7;
            margin-left: 10px;
        `;
        
        closeButton.addEventListener('click', function() {
            message.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => message.remove(), 300);
        });
        
        message.appendChild(closeButton);
        
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            if (message.parentNode) {
                message.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => message.remove(), 300);
            }
        }, 5000 + (index * 1000));
    });
}

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
            max-height: 100px;
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
            max-height: 0;
            padding: 0;
            margin: 0;
        }
    }
    
    .module {
        transition: all 0.2s ease !important;
    }
    
    .module:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    .button, input[type="submit"] {
        transition: all 0.2s ease !important;
    }
    
    .results tbody tr {
        transition: background-color 0.2s ease !important;
    }
    
    /* Улучшенный скроллбар */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #ccd0d4;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0073aa;
    }
`;

document.head.appendChild(style);

// Функция для добавления WordPress-подобных уведомлений
function showAdminNotice(message, type = 'success') {
    const notice = document.createElement('div');
    notice.className = `notice notice-${type} is-dismissible`;
    notice.innerHTML = `
        <p>${message}</p>
        <button type="button" class="notice-dismiss">
            <span class="screen-reader-text">Dismiss this notice.</span>
        </button>
    `;
    
    const content = document.querySelector('#content');
    if (content) {
        content.insertBefore(notice, content.firstChild);
        
        // Автоматическое скрытие
        setTimeout(() => {
            notice.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notice.remove(), 300);
        }, 4000);
    }
}

// Экспортируем функцию для использования в других скриптах
window.showAdminNotice = showAdminNotice;