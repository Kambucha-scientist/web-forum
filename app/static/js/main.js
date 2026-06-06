document.addEventListener('DOMContentLoaded', function() {
    const voteBtns = document.querySelectorAll('.vote-btn');
    
    voteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const countSpan = this.querySelector('.vote-count');
            
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
                    countSpan.textContent = data.new_rating;
                    btn.disabled = true;
                    btn.style.opacity = '0.6';
                    btn.style.cursor = 'default';
                } else {
                    alert(data.error);
                }
            })
            .catch(err => console.error('Ошибка:', err));
        });
    });
});