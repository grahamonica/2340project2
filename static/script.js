// script.js
let slideIndex = 0;
showSlides();

function showSlides() {
    let slides = document.querySelectorAll(".slide");
    
    // Hide all slides
    slides.forEach(slide => {
        slide.style.display = "none";
    });
    
    // Increment the slide index
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1; }
    
    // Show the current slide
    slides[slideIndex - 1].style.display = "block";
    
    // Change slide every 4 seconds
    setTimeout(showSlides, 4000);
}
