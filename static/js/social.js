function toggleLike(postId) {
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Helper function to retrieve CSRF token
        },
    })
        .then((response) => response.json())
        .then((data) => {
            const likeButton = document.querySelector(`.like-button[onclick="toggleLike('${postId}')"]`);
            const likesCount = document.getElementById(`likes-count-${postId}`);

            if (data.liked) {
                likeButton.innerHTML = '❤️ Liked';
            } else {
                likeButton.innerHTML = '🤍 Like';
            }
            likesCount.textContent = `${data.likes_count} likes`;
        })
        .catch((error) => console.error('Error liking post:', error));
}

// Helper function to get CSRF token from cookies
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}
