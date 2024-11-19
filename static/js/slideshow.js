let slideIndex = 0;
let slideInterval;
let progressBarTimer;
let totalSlides;

function showSlides() {
    const slides = document.querySelectorAll('.slide');
    const progressBar = document.getElementById('progress-bar');
    const slideshowContainer = document.getElementById('slideshow-container');
    const rewatchButton = document.getElementById('rewatch-button');

    // Hide all slides and reset the progress bar
    slides.forEach((slide, index) => {
        slide.style.display = (index === slideIndex) ? 'block' : 'none';
        slide.classList.remove('fade');
    });

    // Fade in the current slide
    slides[slideIndex].classList.add('fade');

    // Reset and start the progress bar
    progressBar.style.width = '0%';
    clearInterval(progressBarTimer);
    progressBarTimer = setInterval(() => {
        const currentWidth = parseFloat(progressBar.style.width);
        if (currentWidth < 100) {
            progressBar.style.width = (currentWidth + 2) + '%';
        }
    }, 100);

    // Set a timeout to automatically move to the next slide after 5 seconds
    slideInterval = setTimeout(() => {
        changeSlide(1);
    }, 5000);

    // Check if the slideshow has completed
    if (slideIndex === totalSlides - 1) {
        setTimeout(() => {
            slideshowContainer.style.display = 'none';  // Hide the slideshow
            rewatchButton.style.display = 'block';     // Show the rewatch button
        }, 500);  // Wait for the last slide to finish before hiding
    }
}

function changeSlide(direction) {
    clearTimeout(slideInterval); // Stop the current slide change timeout
    clearInterval(progressBarTimer); // Stop the progress bar timer
    const slides = document.querySelectorAll('.slide');
    slideIndex = (slideIndex + direction + slides.length) % slides.length;
    showSlides();
}

// Function to rewatch the slideshow
function rewatchSlideshow() {
    slideIndex = 0;
    document.getElementById('slideshow-container').style.display = 'block';
    document.getElementById('rewatch-button').style.display = 'none';
    showSlides();
}

// Initialize the slideshow
document.addEventListener('DOMContentLoaded', () => {
    totalSlides = document.querySelectorAll('.slide').length;  // Get the total number of slides
    showSlides();
});
