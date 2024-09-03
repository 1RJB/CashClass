let currentCardIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
    if (flashcards.length > 0) {
        updateCard();
        updateProgressBar();
    } else {
        document.getElementById('flashcard-container').innerHTML = '<p>No flashcards available. Please add new flashcards.</p>';
    }
});

function updateCard() {
    const questionElement = document.getElementById('flashcard-question');
    const answerElement = document.getElementById('flashcard-answer');

    questionElement.textContent = flashcards[currentCardIndex].question;
    answerElement.textContent = flashcards[currentCardIndex].answer;

    const flashcard = document.querySelector('.flashcard');
    flashcard.classList.remove('flipped');
}

function flipCard() {
    const flashcard = document.querySelector('.flashcard');
    flashcard.classList.toggle('flipped');
}

function prevCard() {
    if (currentCardIndex > 0) {
        currentCardIndex--;
        updateCard();
        updateProgressBar();
    }
}

function nextCard() {
    if (currentCardIndex < flashcards.length - 1) {
        currentCardIndex++;
        updateCard();
        updateProgressBar();
    }
}

function updateProgressBar() {
    const progressText = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const current = currentCardIndex + 1;
    const total = flashcards.length;
    const progressPercent = (current / total) * 100;

    progressText.textContent = `Card ${current} of ${total}`;
    progressBar.style.width = `${progressPercent}%`;
}
