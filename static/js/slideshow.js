let slideIndex = 0;
let slideInterval;
let progressBarTimer;
let totalSlides;

function showSlides() {
    const slides = document.querySelectorAll('.slide');
    const progressBar = document.getElementById('progress-bar');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const rewatchButton = document.getElementById('rewatch-button');
    const logoutButtons = document.querySelectorAll('.nav-button');
    
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

    // Show the buttons only on the last slide
    if (slideIndex === totalSlides - 1) {
        rewatchButton.style.display = 'block'; // Show rewatch button
        logoutButtons.forEach(button => button.style.display = 'block'); // Show contact and logout buttons
    } else {
        rewatchButton.style.display = 'none'; // Hide rewatch button
        logoutButtons.forEach(button => button.style.display = 'none'); // Hide contact and logout buttons
    }

    // Show/Hide navigation buttons
    prevButton.style.display = (slideIndex === 0) ? 'none' : 'block'; // Hide "Previous" button on the first slide
    nextButton.style.display = (slideIndex === totalSlides - 1) ? 'none' : 'block'; // Hide "Next" button on the last slide

    // Set a timeout to automatically move to the next slide after 5 seconds, unless it's the last slide
    if (slideIndex === totalSlides - 1) {
        // For the last slide, wait 5 seconds before showing the rewatch button
        setTimeout(() => {
            slideshowContainer.style.display = 'none';  // Hide the slideshow
            rewatchButton.style.display = 'block';     // Show the rewatch button
        }, 5000);  // Wait for the last slide to finish before hiding
    } else {
        // For all other slides, move to the next slide after 5 seconds
        slideInterval = setTimeout(() => {
            changeSlide(1);
        }, 5000);
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
