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
function playSnippet(previewUrl, element) {
    const audioPlayer = document.getElementById('audio-player');

    // Pause any currently playing audio
    if (!audioPlayer.paused && audioPlayer.src === previewUrl) {
        audioPlayer.pause();
        element.textContent = '🔊'; // Reset icon to speaker
        return;
    }

    // Set the preview URL as the audio source
    audioPlayer.src = previewUrl;

    // Play the audio
    audioPlayer.play().catch((error) => {
        console.error('Error playing audio snippet:', error);
    });

    // Change icon to indicate playback
    const allIcons = document.querySelectorAll('.speaker-icon');
    allIcons.forEach((icon) => (icon.textContent = '🔊')); // Reset all icons
    element.textContent = '⏸'; // Change to pause icon
}
