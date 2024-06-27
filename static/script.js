document.addEventListener('DOMContentLoaded', function() {
    let squares = document.querySelectorAll('.square');
    let currentHighlightedSquare = null;

    squares.forEach(square => {
        square.addEventListener('click', () => {
            if (currentHighlightedSquare) {
                currentHighlightedSquare.style.backgroundColor = '';
            }

            square.style.backgroundColor = '#dfce9f';
            currentHighlightedSquare = square;

            // undo highlight if clicked again
            square.addEventListener('click', () => {
                square.style.backgroundColor = '';
                currentHighlightedSquare = null;
            });
        });
    });
});


