document.addEventListener("DOMContentLoaded", function() {
    // Hamburger menu toggle
    const hamburger = document.querySelector('.header .nav-bar .nav-list .hamburger');
    const mobile_menu = document.querySelector('.header .nav-bar .nav-list ul');
    const menu_item = document.querySelectorAll('.header .nav-bar .nav-list ul li a');
    const header = document.querySelector('.header.container');

    if (hamburger && mobile_menu && header) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            mobile_menu.classList.toggle('active');
        });

        document.addEventListener('scroll', () => {
            var scroll_position = window.scrollY;
            if (scroll_position > 250) {
                header.style.backgroundColor = '#29323c';
            } else {
                header.style.backgroundColor = 'transparent';
            }
        });

        menu_item.forEach((item) => {
            item.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                mobile_menu.classList.toggle('active');
            });
        });
    }

    // Dynamic word cycling
    const words = ["Future", "Success", "Goals", "Dreams"];
    let index = 0;

    function cycleWords() {
        const dynamicWordElement = document.getElementById("dynamic-word");

        if (dynamicWordElement) {
            // Fade out the current word
            dynamicWordElement.style.opacity = 0;

            setTimeout(() => {
                // Change the word after fade out
                dynamicWordElement.textContent = words[index];

                // Fade in the new word
                dynamicWordElement.style.opacity = 1;

                // Move to the next word in the array
                index = (index + 1) % words.length;
            }, 1000); // Matches the fade out duration
        }
    }

    setInterval(cycleWords, 4000); // Change word every 4 seconds to match the animation duration
});
