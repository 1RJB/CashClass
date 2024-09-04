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