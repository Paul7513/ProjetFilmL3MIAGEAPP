let left_btn = document.querySelector('.bx-chevron-left');
let right_btn = document.querySelector('.bx-chevron-right');
let cards = document.querySelector('.cards');

left_btn.addEventListener('click', () => {
    cards.scrollLeft -= 140;
});

right_btn.addEventListener('click', () => {
    cards.scrollLeft += 140;
});
