$(document).ready(function() {
    const socket = io();
    let squares = document.querySelectorAll('.square');
    let moveFrom = null;
    let moveTo = null;
    let clickCounter = 0;
    let validMove = true;

    piece_symbols = [
        '♟', '♞', '♝', '♜', '♛', '♚',
    ]

    // Retrieve and display stored notations
    let storedNotations = JSON.parse(localStorage.getItem('notations')) || [];
    storedNotations.forEach(notation => {
        console.log(notation);

        let list_notations = document.getElementById('list-notations');
        let li = document.createElement('li');
        li.innerText = notation;
        list_notations.appendChild(li);
    });

    // handle player color
    let playerTurn = document.getElementById('turn');
    playerTurn.style.color = playerTurn.innerText === 'white' ? 'white' : 'black';
    playerTurn.style.fontSize = '20px';

    // -------------- move request --------------

    // Add event listener to each square
    squares.forEach(square => {
        square.addEventListener('click', () => {
            let squareId = square.id;
            let rowIndex = squareId.split('-')[1];
            let colIndex = squareId.split('-')[2];

            let rowLetter = String.fromCharCode(97 + parseInt(colIndex));
            let colNumber = 8 - parseInt(rowIndex);
            let notation = `${rowLetter}${colNumber}`;

            console.log(notation);

            let pieceElement = square.querySelector('.piece');
            let pieceName = pieceElement ? pieceElement.dataset.pieceName : null;
            let pieceColor = pieceElement ? pieceElement.dataset.pieceColor : null;

            if (clickCounter === 0) {
                moveFrom = {
                    notation: notation,
                    piece: pieceName,
                    color: pieceColor
                };

                $.ajax({
                    type: 'POST',
                    url: "/get-moves",
                    contentType: 'application/json',
                    data: JSON.stringify({
                        position: moveFrom.notation,
                        name: moveFrom.piece,
                        color: moveFrom.color
                    }),
                });

                socket.on('received-moves', function(data) {
                    console.log("Moves received:", data['moves']);

                    // highlight the received moves
                    data['moves'].forEach(move => {
                        let square = $(`#square-${8 - parseInt(move[1])}-${move[0].charCodeAt(0) - 97}-frontlayer`);
                        square.addClass('highlight');
                    });
                });

            } else if (clickCounter === 1) {
                moveTo = {
                    notation: notation,
                    piece: pieceName,
                    color: pieceColor
                };
            }

            clickCounter++;

            // send move information
            if (clickCounter === 2) {
                validMove = true;

                $.ajax({
                    type: 'POST',
                    url: "/make_move",
                    contentType: 'application/json',
                    data: JSON.stringify({
                        position: moveFrom.notation,
                        placement: moveTo.notation,
                        name: moveFrom.piece,
                        color: moveFrom.color,
                    }),
                    success: function(response) {
                        console.log("Move has been created");

                        if (validMove) {
                            // Store the moveTo notation in localStorage
                            chessPiece = moveFrom.piece;
                            icon = ''

                            console.log(chessPiece);
                            if (chessPiece == 'white_pawns' || chessPiece == 'black_pawns') {
                                icon = piece_symbols[0];
                            } else if (chessPiece == 'white_knights' || chessPiece == 'black_knights') {
                                icon = piece_symbols[1];
                            } else if (chessPiece == 'white_bishops' || chessPiece == 'black_bishops') {
                                icon = piece_symbols[2];
                            } else if (chessPiece == 'white_rooks' || chessPiece == 'rooks') {
                                icon = piece_symbols[3];
                            } else if (chessPiece == 'white_queen' || chessPiece == 'black_queen') {
                                icon = piece_symbols[4];
                            } else if (chessPiece == 'white_king' || chessPiece == 'black_king') {
                                icon = piece_symbols[5];
                            }



                            storedNotations.push(`${icon}${moveTo.notation}`);
                            localStorage.setItem('notations', JSON.stringify(storedNotations));

                            let list_notations = document.getElementById('list-notations');
                            let li = document.createElement('li');
                            li.innerText = moveTo.notation;
                            list_notations.appendChild(li);
                        }

                        // automatic reload after move
                        setTimeout(() => {
                            location.reload();
                        }, 500);
                    },
                    error: function(xhr, status, error) {
                        console.error("Error:", error);
                    }
                });

                clickCounter = 0;
            }
        });
    });

    // -------------- position adjustments --------------

    // update the position
    function updateBoard(pieces) {
        // Clear all squares
        $('.piece').remove();

        // Update squares with new pieces
        for (let piece in pieces) {
            let positions = pieces[piece];
            for (let row = 0; row < positions.length; row++) {
                for (let col = 0; col < positions[row].length; col++) {
                    if (positions[row][col]) {
                        let square = $(`#square-${row}-${col}`);
                        square.append(`<div class="piece ${piece}" data-piece-name="${piece}" data-piece-color="${piece.startsWith('white') ? 'white' : 'black'}"></div>`);
                    }
                }
            }
        }
    }

    // reset board
    $('#reset-board-btn').on('click', function() {
        resetBoard();
    });

    // reset board position
    function resetBoard() {
        $.ajax({
            type: 'POST',
            url: "/reset_board",
            success: function(response) {
                console.log("Board has been reset");
                updateBoard(response);

                localStorage.clear();
                // remove li elements
                let list_notations = document.getElementById('list-notations');
                while (list_notations.firstChild) {
                    list_notations.removeChild(list_notations.firstChild);
                }

                setTimeout(() => {
                    location.reload();
                }, 500);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
            }
        });
    }

    // -------------- move interaction --------------

    // show the move event
    socket.on('move-made', function(data) {
        console.log("Move made:", data);

        let fromSquare = $(`#square-${8 - parseInt(data.position[1])}-${data.position[0].charCodeAt(0) - 97}`);
        let toSquare = $(`#square-${8 - parseInt(data.placement[1])}-${data.placement[0].charCodeAt(0) - 97}`);

        let piece = fromSquare.find('.piece');
        let fromPosition = fromSquare.offset();
        let toPosition = toSquare.offset();

        piece.attr('data-piece-name', data.name);
        piece.attr('data-piece-color', data.color);

        piece.css({
            transform: `translate(${toPosition.left - fromPosition.left}px, ${toPosition.top - fromPosition.top}px)`
        });

        setTimeout(() => {
            piece.detach().css({ transform: '' });
            toSquare.append(piece);
        }, 1000);
    });

    // -------------- error popups --------------

    // show invalid move event pop up
    socket.on('invalid-move', function(data) {
        validMove = false;
        $('#invalid-move-modal').show();

        $('#close-invalid-move-modal').on('click', function() {
            $('#invalid-move-modal').hide();
        });

        let message = data.message || "Invalid move."; // Default message if data.message is undefined
        let invalidMoveMessage = document.querySelector('.invalid-move-message');

        if (invalidMoveMessage) {
            invalidMoveMessage.innerText = message;
        } else {
            console.error("Error: .invalid-move-message element not found.");
        }

        setTimeout(() => {
            $('#invalid-move-modal').hide();
        }, 5000);
    });


    // show wrong turn event pop up
    socket.on('wrong-turn', function(data) {
        validMove = false;
        $('#wrong-turn-modal').show();
        let playerColor = document.getElementById('player-color');
        playerColor.classList.remove('player-color-black', 'player-color-white');

        if (data.color === 'white') {
            playerColor.innerText = 'black';
            playerColor.classList.add('player-color-black');
        } else {
            playerColor.innerText = 'white';
            playerColor.classList.add('player-color-white');
        }

        $('#close-wrong-turn-modal').on('click', function() {
            $('#wrong-turn-modal').hide();
        });

        setTimeout(() => {
            $('#wrong-turn-modal').hide();
        }, 1000);
    });

    // show king in danger event pop up
    socket.on('king-danger', function(data) {
        validMove = false;
        $('#king-danger-modal').show();
        let playerColor = document.getElementById('player-color');
        playerColor.classList.remove('player-color-black', 'player-color-white');

        if (data.color === 'white') {
            playerColor.innerText = 'black';
            playerColor.classList.add('player-color-black');
        } else {
            playerColor.innerText = 'white';
            playerColor.classList.add('player-color-white');
        }

        $('#close-king-danger-modal').on('click', function() {
            $('#king-danger-modal').hide();
        });

        setTimeout(() => {
            $('#king-danger-modal').hide();
        }, 1000);
    });
});
