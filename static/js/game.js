// Drag-and-drop functionality for track arrangement
const trackList = document.getElementById("track-list");
let draggedItem = null;

trackList.addEventListener("dragstart", (e) => {
    draggedItem = e.target;
    e.target.style.opacity = "0.5";
});

trackList.addEventListener("dragend", (e) => {
    e.target.style.opacity = "";
    draggedItem = null;
});

trackList.addEventListener("dragover", (e) => e.preventDefault());

trackList.addEventListener("drop", (e) => {
    e.preventDefault();
    if (e.target.classList.contains("track-item") && draggedItem !== e.target) {
        trackList.insertBefore(draggedItem, e.target.nextSibling);
    }
});

// Function to check if the tracks are in the correct order
function checkOrder() {
    const trackItems = document.querySelectorAll(".track-item");
    let isCorrect = true;

    trackItems.forEach((item, index) => {
        const originalIndex = item.getAttribute("data-track-index");
        if (originalIndex != index) {
            isCorrect = false;
        }
    });

    const feedback = document.getElementById("game-feedback");
    feedback.textContent = isCorrect
        ? "Congratulations! You arranged your top tracks correctly!"
        : "Not quite! Try again or check your Spotify Wrapped for hints.";
}
