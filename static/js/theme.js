// theme.js

// Function to initialize theme toggles
// Theme toggle logic
const body = document.body;
document.getElementById('toggle-dark-light').addEventListener('click', () => {
    body.className = body.classList.contains('light-mode') ? 'dark-mode' : 'light-mode';
});

document.getElementById('toggle-christmas').addEventListener('click', () => {
    body.className = 'christmas-mode';
});

document.getElementById('toggle-halloween').addEventListener('click', () => {
    body.className = 'halloween-mode';
});