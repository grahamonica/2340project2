let slideIndex = 0;
let slideInterval;
let progressBarTimer;
let totalSlides;
let lineInterval;

// function showSlides() {
//     const slides = document.querySelectorAll('.slide');
//     const progressBar = document.getElementById('progress-bar');
//     const prevButton = document.getElementById('prev-button');
//     const nextButton = document.getElementById('next-button');
//     const rewatchButton = document.getElementById('rewatch-button');
//     const logoutButtons = document.querySelectorAll('.nav-button');

//     // Hide all slides and reset the progress bar
//     slides.forEach((slide, index) => {
//         slide.style.display = (index === slideIndex) ? 'block' : 'none';
//         slide.classList.remove('fade');
//     });

//     // Fade in the current slide
//     slides[slideIndex].classList.add('fade');

//     // Handle line-by-line animation
//     const currentSlide = slides[slideIndex];
//     const lines = currentSlide.querySelectorAll('.line');
//     lines.forEach(line => line.classList.remove('visible')); // Reset all lines
//     let currentLineIndex = 0;

//     clearInterval(lineInterval); // Clear any previous line intervals

//     const timePerLine = 1000; // Time in ms for each line to appear
//     const extraTime = 1500; // Extra time to wait after the last line appears

//     if (lines.length > 0) {
//         lineInterval = setInterval(() => {
//             if (currentLineIndex < lines.length) {
//                 lines[currentLineIndex].classList.add('visible');
//                 currentLineIndex++;
//             } else {
//                 clearInterval(lineInterval); // Stop once all lines are visible

//                 // If it's not the last slide, schedule the slide change after extra time
//                 if (slideIndex !== totalSlides - 1) {
//                     slideInterval = setTimeout(() => {
//                         changeSlide(1);
//                     }, extraTime);
//                 }
//             }
//         }, timePerLine);
//     }

//     // Handle progress bar and timer for slides without lines
//     if (lines.length === 0 && !currentSlide.classList.contains('game-slide')) {
//         progressBar.style.width = '0%';
//         clearInterval(progressBarTimer);

//         // Progress bar logic
//         progressBarTimer = setInterval(() => {
//             const currentWidth = parseFloat(progressBar.style.width);
//             if (currentWidth < 100) {
//                 progressBar.style.width = (currentWidth + 2) + '%';
//             }
//         }, 100);

//         // Automatically move to the next slide after 5 seconds (only if it's not the last slide)
//         if (slideIndex !== totalSlides - 1) {
//             slideInterval = setTimeout(() => {
//                 changeSlide(1);
//             }, 5000);
//         }
//     } else {
//         // Stop progress bar for game slide
//         progressBar.style.width = '0%';
//         clearInterval(progressBarTimer);
//         clearTimeout(slideInterval);
//         startGame(); // Start game logic
//     }

//     // Show the buttons only on the last slide
//     if (slideIndex === totalSlides - 1) {
//         rewatchButton.style.display = 'block'; // Show rewatch button
//         logoutButtons.forEach(button => button.style.display = 'block'); // Show contact and logout buttons
//     } else {
//         rewatchButton.style.display = 'none'; // Hide rewatch button
//         logoutButtons.forEach(button => button.style.display = 'none'); // Hide contact and logout buttons
//     }

//     // Show/Hide navigation buttons
//     prevButton.style.display = (slideIndex === 0) ? 'none' : 'block'; // Hide "Previous" button on the first slide
//     nextButton.style.display = (slideIndex === totalSlides - 1) ? 'none' : 'block'; // Hide "Next" button on the last slide
// }

function updateSlideVisibility(slides) {
    slides.forEach((slide, index) => {
        slide.style.display = (index === slideIndex) ? 'block' : 'none';
        slide.classList.remove('fade');
    });
    slides[slideIndex].classList.add('fade');
}

function handleLineAnimation(currentSlide) {
    const lines = currentSlide.querySelectorAll('.line');
    lines.forEach(line => line.classList.remove('visible'));
    
    if (lines.length === 0) return null;

    let currentLineIndex = 0;
    return setInterval(() => {
        if (currentLineIndex < lines.length) {
            lines[currentLineIndex].classList.add('visible');
            currentLineIndex++;
        } else {
            clearInterval(lineInterval);
            if (slideIndex !== totalSlides - 1) {
                slideInterval = setTimeout(() => changeSlide(1), 1500);
            }
        }
    }, 1000);
}

function updateProgressBar(currentSlide) {
    const progressBar = document.getElementById('progress-bar');
    if (currentSlide.classList.contains('game-slide')) {
        progressBar.style.width = '0%';
        return null;
    }

    return setInterval(() => {
        const currentWidth = parseFloat(progressBar.style.width);
        if (currentWidth < 100) {
            progressBar.style.width = (currentWidth + 2) + '%';
        }
    }, 100);
}

// Code smells refactor #1
function showSlides() {
    const slides = document.querySelectorAll('.slide');
    const currentSlide = slides[slideIndex];
    
    updateSlideVisibility(slides);
    
    clearInterval(lineInterval);
    clearInterval(progressBarTimer);
    clearTimeout(slideInterval);
    
    lineInterval = handleLineAnimation(currentSlide);
    progressBarTimer = updateProgressBar(currentSlide);
    
    updateNavigationButtons(slideIndex === totalSlides - 1);
}

function changeSlide(direction) {
    clearTimeout(slideInterval); // Stop the current slide change timeout
    clearInterval(progressBarTimer); // Stop the progress bar timer
    clearInterval(lineInterval); // Stop the line-by-line interval

    const slides = document.querySelectorAll('.slide');
    slideIndex = (slideIndex + direction + slides.length) % slides.length;

    // If going back after the slideshow finishes, disable timer
    if (slides[slideIndex].classList.contains('game-slide') || slideIndex === totalSlides - 1) {
        clearTimeout(slideInterval); // Ensure no timer restarts
    }

    showSlides();
}

// Function to rewatch the slideshow
function rewatchSlideshow() {
    slideIndex = 0;
    document.getElementById('slideshow-container').style.display = 'block';
    document.getElementById('rewatch-button').style.display = 'none';
    showSlides();
}

// Function to check Spotify authentication and redirect if not authenticated
function checkSpotifyAuth() {
    fetch('/spotify/check-auth/')  // Backend endpoint to verify Spotify tokens
        .then(response => {
            if (response.status === 401) {
                // If not authenticated, redirect to Spotify login
                window.location.href = '/spotify/login/';
            }
        })
        .catch(error => {
            console.error('Error checking Spotify authentication:', error);
        });
}

// Initialize the slideshow
document.addEventListener('DOMContentLoaded', () => {
    totalSlides = document.querySelectorAll('.slide').length; // Get the total number of slides

    // Check Spotify authentication on load
    checkSpotifyAuth();

    showSlides();
});
