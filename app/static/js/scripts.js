let currentCard = 0;
const flashcards = JSON.parse('{{ flashcards|tojson|safe }}');

function updateCard() {
    const flashcardElements = document.querySelectorAll('.flashcard');
    const front = flashcardElements[0].querySelector('.front .card-text');
    const back = flashcardElements[0].querySelector('.back .card-text');
    front.textContent = flashcards[currentCard].question;
    back.textContent = flashcards[currentCard].answer;
    document.getElementById('progress').textContent = `Card ${currentCard + 1} of ${flashcards.length}`;
    updateProgressBar();
}

function flipCard() {
    const flashcard = document.querySelectorAll('.flashcard')[0];
    flashcard.classList.toggle('flipped');
}

function prevCard() {
    if (currentCard > 0) {
        currentCard--;
        updateCard();
    }
}

function nextCard() {
    if (currentCard < flashcards.length - 1) {
        currentCard++;
        updateCard();
    }
}

function shuffleCards() {
    flashcards.sort(() => Math.random() - 0.5);
    currentCard = 0;
    updateCard();
}

function updateProgressBar() {
    const progress = ((currentCard + 1) / flashcards.length) * 100;
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
}

document.addEventListener('DOMContentLoaded', updateCard);
