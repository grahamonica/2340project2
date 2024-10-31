// theme.js

function toggleMode() {
    const body = document.body;
    const loginBox = document.querySelector('.login-box');
    const toggleButton = document.getElementById('toggle-mode');
    const inputs = document.querySelectorAll('input, button');

    body.classList.toggle('dark-mode');
    loginBox.classList.toggle('dark-mode');
    inputs.forEach(input => input.classList.toggle('dark-mode'));
    toggleButton.classList.toggle('dark-mode');

    // Update button text based on mode
    toggleButton.textContent = body.classList.contains('dark-mode') 
        ? 'Switch to Light Mode' 
        : 'Switch to Dark Mode';
    
    // Save the theme preference in localStorage
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// Apply the saved theme on load
window.onload = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.login-box').classList.add('dark-mode');
        const toggleButton = document.getElementById('toggle-mode');
        toggleButton.textContent = 'Switch to Light Mode';
        toggleButton.classList.add('dark-mode');
        document.querySelectorAll('input, button').forEach(input => input.classList.add('dark-mode'));
    }
};