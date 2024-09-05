function toggleDescription(id) {
    var desc = document.getElementById(id);
    desc.style.display = (desc.style.display === "none" || desc.style.display === "") ? "block" : "none";
}

function navigate(direction) {
    const lessonNumber = parseInt(window.location.pathname.match(/lesson(\d+)/)[1]);
    const nextLessonNumber = lessonNumber + direction;
    if (nextLessonNumber >= 1 && nextLessonNumber <= 4) {
        window.location.href = `lesson${nextLessonNumber}`;
    } else if (nextLessonNumber > 4) {
        window.location.href = "lesson_home";
    }
}

function exit() {
    if (confirm("Are you sure you want to exit?")) {
        window.location.href = "lesson_home";
    }
}

function adjustButtons() {
    const lessonNumber = parseInt(window.location.pathname.match(/lesson(\d+)/)[1]);

    const prevButton = document.querySelector(".navigation button:first-child");
    const nextButton = document.querySelector(".navigation button:nth-child(2)");

    // Remove "Back" button if on lesson 1
    if (lessonNumber === 1) {
        prevButton.style.display = "none";
    }

    // Change "Next" button to "Finish" if on lesson 4
    if (lessonNumber === 4) {
        nextButton.style.display = "none";
    }
}

window.onload = adjustButtons;