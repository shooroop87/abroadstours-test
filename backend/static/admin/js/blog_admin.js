// Улучшенная админка блога для django-parler
(function($) {
    $(document).ready(function() {
        
        // Функция для создания slug из строки
        function createSlug(str) {
            return str
                .toLowerCase()
                .trim()
                .replace(/[^\w\s-]/g, '') // Удаляем спецсимволы
                .replace(/[\s_-]+/g, '-') // Заменяем пробелы на дефисы
                .replace(/^-+|-+$/g, ''); // Убираем дефисы в начале и конце
        }
        
        // Автозаполнение slug для категорий
        $('input[name*="name"]').on('keyup paste', function() {
            var nameValue = $(this).val();
            var slugField = $('input[name*="slug"]').not('[name*="meta"]');
            
            if (nameValue && (!slugField.val() || slugField.data('auto-generated'))) {
                var newSlug = createSlug(nameValue);
                slugField.val(newSlug).data('auto-generated', true);
            }
        });
        
        // Автозаполнение slug для постов
        $('input[name*="title"]').on('keyup paste', function() {
            var titleValue = $(this).val();
            var slugField = $('input[name*="slug"]').not('[name*="meta"]');
            
            if (titleValue && (!slugField.val() || slugField.data('auto-generated'))) {
                var newSlug = createSlug(titleValue);
                slugField.val(newSlug).data('auto-generated', true);
            }
        });
        
        // Отключаем автогенерацию если пользователь вручную редактирует slug
        $('input[name*="slug"]').not('[name*="meta"]').on('keyup', function() {
            $(this).removeData('auto-generated');
        });
        
        // Автозаполнение meta_title если пустое
        $('input[name*="title"]').on('keyup paste', function() {
            var titleValue = $(this).val();
            var metaTitleField = $('input[name*="meta_title"]');
            
            if (titleValue && !metaTitleField.val()) {
                metaTitleField.val(titleValue.substring(0, 60));
            }
        });
        
        // Счетчик символов для SEO полей
        function addCharCounter(selector, maxLength) {
            $(selector).each(function() {
                var $field = $(this);
                var $counter = $('<div class="char-counter" style="font-size: 12px; color: #666; margin-top: 5px;"></div>');
                $field.after($counter);
                
                function updateCounter() {
                    var length = $field.val().length;
                    var remaining = maxLength - length;
                    var color = remaining < 0 ? '#d63384' : remaining < maxLength * 0.1 ? '#fd7e14' : '#198754';
                    $counter.html('Characters: <span style="color: ' + color + ';">' + length + '/' + maxLength + '</span>');
                }
                
                $field.on('keyup paste input', updateCounter);
                updateCounter();
            });
        }
        
        // Добавляем счетчики для SEO полей
        addCharCounter('input[name*="meta_title"]', 60);
        addCharCounter('input[name*="meta_description"]', 160);
        addCharCounter('input[name*="og_title"]', 95);
        addCharCounter('input[name*="og_description"]', 200);
        
        // Улучшенный интерфейс для статусов
        $('select[name="status"]').change(function() {
            var status = $(this).val();
            var $publishedField = $('input[name="published_at_0"], input[name="published_at_1"]').closest('.form-row');
            
            if (status === 'scheduled') {
                $publishedField.show().find('label').text('Scheduled for:');
            } else if (status === 'published') {
                $publishedField.show().find('label').text('Published at:');
            } else {
                $publishedField.hide();
            }
        }).trigger('change');
        
        // Предупреждение при выходе с несохраненными изменениями
        var formChanged = false;
        $('form input, form textarea, form select').on('change input', function() {
            formChanged = true;
        });
        
        $('form').on('submit', function() {
            formChanged = false;
        });
        
        $(window).on('beforeunload', function() {
            if (formChanged) {
                return 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
        
    });
})(django.jQuery);
