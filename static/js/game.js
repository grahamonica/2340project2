// Drag-and-drop functionality for track arrangement
const trackList = document.getElementById("track-list");
let draggedItem = null;

trackList.addEventListener("dragstart", (e) => {
    draggedItem = e.target;
    e.target.classList.add("dragged"); // Add dragged class
    setTimeout(() => (e.target.style.visibility = "hidden"), 0); // Hide dragged item
});

trackList.addEventListener("dragend", (e) => {
    e.target.style.visibility = "visible";
    e.target.classList.remove("dragged"); // Remove dragged class
    draggedItem = null;
});

trackList.addEventListener("dragover", (e) => e.preventDefault());

trackList.addEventListener("drop", (e) => {
    e.preventDefault();
    if (
        e.target.classList.contains("track-item") &&
        draggedItem !== e.target
    ) {
        const targetRect = e.target.getBoundingClientRect();
        const targetCenter = targetRect.y + targetRect.height / 2;

        if (e.clientY > targetCenter) {
            trackList.insertBefore(draggedItem, e.target.nextSibling);
        } else {
            trackList.insertBefore(draggedItem, e.target);
        }
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
        ? "🎉 Congratulations! You arranged your top tracks correctly!"
        : "❌ Not quite! Try again or check your Spotify Wrapped for hints.";
}
