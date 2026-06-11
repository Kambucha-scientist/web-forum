document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelectorAll('[data-utc-time]').forEach(el => {
        const utcString = el.getAttribute('data-utc-time');
        const utcDate = new Date(utcString + 'Z');
        
        const options = { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false
        };
        
        el.textContent = utcDate.toLocaleString('ru-RU', options);
    });

    const voteBtns = document.querySelectorAll('.vote-btn');
    
    voteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const countSpan = this.querySelector('.vote-count');
            const button = this;
            
            // Блокируем кнопку на время запроса
            button.disabled = true;
            
            fetch('/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `post_id=${postId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем счётчик
                    countSpan.textContent = data.new_rating;
                    
                    // Переключаем класс voted
                    if (data.voted) {
                        button.classList.add('voted');
                    } else {
                        button.classList.remove('voted');
                    }
                } else {
                    alert(data.error);
                }
            })
            .catch(err => {
                console.error('Ошибка:', err);
                alert('Ошибка при голосовании');
            })
            .finally(() => {
                // Разблокируем кнопку
                button.disabled = false;
            });
        });
    });
});