$(document).ready(function() {
    console.log('Document is ready');

    function showStoredModal(modalId, storageKey) {
        let shouldShow = localStorage.getItem(storageKey);
        if (shouldShow === 'true') {
            $(modalId).show();
        }
    }

    // Show modals on page load if stored
    showStoredModal('#invalid-move-modal', 'showInvalidMoveModal');
    showStoredModal('#wrong-turn-modal', 'showWrongTurnModal');
    showStoredModal('#king-danger-modal', 'showKingDangerModal');

    // Attach click event listeners for close buttons
    $('#close-invalid-move-modal').click(function() {
        $('#invalid-move-modal').hide();
        localStorage.setItem('showInvalidMoveModal', 'false');
    });

    $('#close-wrong-turn-modal').click(function() {
        $('#wrong-turn-modal').hide();
        localStorage.setItem('showWrongTurnModal', 'false');
    });

    $('#close-king-danger-modal').click(function() {
        $('#king-danger-modal').hide();
        localStorage.setItem('showKingDangerModal', 'false');
    });

    const socket = io();
    let squares = document.querySelectorAll('.square');
    let moveFrom = null;
    let moveTo = null;
    let clickCounter = 0;
    let validMove = true;

    const pieceSymbols = [
        '♟', '♞', '♝', '♜', '♛', '♚',
    ];

    // Retrieve and display stored notations
    let storedNotations = JSON.parse(localStorage.getItem('notations')) || [];
    storedNotations.forEach(notation => {
        let list_notations = document.getElementById('list-notations');
        let li = document.createElement('li');
        li.innerText = notation;
        list_notations.appendChild(li);
    });

    // Handle player color
    let playerTurn = document.getElementById('turn');
    playerTurn.style.color = playerTurn.innerText === 'white' ? 'white' : 'black';
    playerTurn.style.fontSize = '20px';

    // Add event listener to each square
    squares.forEach(square => {
        square.addEventListener('click', () => {
            let squareId = square.id;
            let rowIndex = squareId.split('-')[1];
            let colIndex = squareId.split('-')[2];

            let rowLetter = String.fromCharCode(97 + parseInt(colIndex));
            let colNumber = 8 - parseInt(rowIndex);
            let notation = `${rowLetter}${colNumber}`;

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
                    data.moves.forEach(move => {
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

            // Send move information
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
                        if (validMove) {
                            // Move the piece in the DOM
                            let fromSquare = $(`#square-${8 - parseInt(moveFrom.notation[1])}-${moveFrom.notation[0].charCodeAt(0) - 97}`);
                            let toSquare = $(`#square-${8 - parseInt(moveTo.notation[1])}-${moveTo.notation[0].charCodeAt(0) - 97}`);
                            let piece = fromSquare.find('.piece');
                            
                            setTimeout(() => {
                                piece.attr('data-piece-name', moveFrom.piece);
                                piece.attr('data-piece-color', moveFrom.color);
                    
                                piece.detach().css({ transform: '' });
                                toSquare.append(piece);
                    
                                // remove highlights
                                $('.highlight').removeClass('highlight');
                            }, 500);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error("Error:", error);
                    }
                });

                clickCounter = 0;
            }
        });
    });

    // Update the board with new positions
    function updateBoard(pieces) {
        $('.piece').remove();
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

    // Reset the board
    $('#reset-board-btn').on('click', function() {
        resetBoard();
    });

    function resetBoard() {
        $.ajax({
            type: 'POST',
            url: "/reset_board",
            success: function(response) {
                updateBoard(response);
                localStorage.clear();
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

    // Show the move event
    socket.on('move-made', function(data) {
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
    
            // Handle castling move
            if (data.castling) {
                let rookFromSquare, rookToSquare;
                if (data.castling === 'kingside') {
                    rookFromSquare = $(`#square-${8 - parseInt(data.position[1])}-7`);
                    rookToSquare = $(`#square-${8 - parseInt(data.position[1])}-5`);
                } else if (data.castling === 'queenside') {
                    rookFromSquare = $(`#square-${8 - parseInt(data.position[1])}-0`);
                    rookToSquare = $(`#square-${8 - parseInt(data.position[1])}-3`);
                }
    
                let rook = rookFromSquare.find('.piece');
                let rookFromPosition = rookFromSquare.offset();
                let rookToPosition = rookToSquare.offset();
    
                rook.css({
                    transform: `translate(${rookToPosition.left - rookFromPosition.left}px, ${rookToPosition.top - rookFromPosition.top}px)`
                });
    
                setTimeout(() => {
                    rook.detach().css({ transform: '' });
                    rookToSquare.append(rook);
                }, 500);
            }
    
            // Update notation with captured piece indication
            let chessPiece = data.name;
            let icon = '';
    
            switch (chessPiece) {
                case 'white_pawns':
                case 'black_pawns':
                    icon = pieceSymbols[0];
                    break;
                case 'white_knights':
                case 'black_knights':
                    icon = pieceSymbols[1];
                    break;
                case 'white_bishops':
                case 'black_bishops':
                    icon = pieceSymbols[2];
                    break;
                case 'white_rooks':
                case 'black_rooks':
                    icon = pieceSymbols[3];
                    break;
                case 'white_queen':
                case 'black_queen':
                    icon = pieceSymbols[4];
                    break;
                case 'white_king':
                case 'black_king':
                    icon = pieceSymbols[5];
                    break;
                default:
                    break;
            }
    
            let notation = `${icon}${data.placement}`;
            if (data.captured_piece) {
                notation += 'x';
            }
    
            storedNotations.push(notation);
            localStorage.setItem('notations', JSON.stringify(storedNotations));
    
            let list_notations = document.getElementById('list-notations');
            let li = document.createElement('li');
            li.innerText = notation;
            list_notations.appendChild(li);
        }, 1000);
    });

    // Show invalid move event pop up
    socket.on('invalid-move', function(data) {
        validMove = false;
        $('#invalid-move-modal').show();

        let message = data.message || "Invalid move.";
        let invalidMoveMessage = document.querySelector('.invalid-move-message');

        if (invalidMoveMessage) {
            invalidMoveMessage.innerText = message;
        } else {
            console.error("Error: .invalid-move-message element not found.");
        }

        setTimeout(() => {
            $('#invalid-move-modal').hide();
            localStorage.setItem('showInvalidMoveModal', 'false');
        }, 5000);

        localStorage.setItem('showInvalidMoveModal', 'true');
    });

    // Show wrong turn event pop up
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

        setTimeout(() => {
            $('#wrong-turn-modal').hide();
            localStorage.setItem('showWrongTurnModal', 'false');
        }, 1000);

        localStorage.setItem('showWrongTurnModal', 'true');
    });

    // Show king in danger event pop up
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

        setTimeout(() => {
            $('#king-danger-modal').hide();
            localStorage.setItem('showKingDangerModal', 'false');
        }, 1000);

        localStorage.setItem('showKingDangerModal', 'true');
    });

    socket.on('pawn-promotion', function(data) {
        console.log('pawn-promoting');
        $('#pawn-promotion-modal').show(); // Show the promotion modal
    
        let promotionModal = document.getElementById('pawn-promotion-modal');
        promotionModal.innerHTML = 'promotion modal'; // Replace this with the actual HTML for promotion options
    
        // Make sure to remove any existing setTimeouts that cause page reloads.
        clearTimeout(reloadTimeout); // If you have a global variable reloadTimeout, clear it.
    
        // Add event listeners for promotion buttons
        let promotionButtons = document.querySelectorAll('.promotion-button');
        promotionButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Handle the promotion choice and update game state
                handlePawnPromotion(this.dataset.pieceType); // Function to handle promotion logic
                $('#pawn-promotion-modal').hide(); // Close the modal
                
                // Send the promotion move to the server
                $.ajax({
                    type: 'POST',
                    url: "/make_move",
                    contentType: 'application/json',
                    data: JSON.stringify({
                        position: data.position, // Original position of the pawn
                        placement: data.newPosition, // New position after promotion
                        name: this.dataset.pieceType, // The new piece type (e.g., queen, rook, etc.)
                        color: data.color // Color of the pawn
                    }),
                    success: function(response) {
                        // Handle successful move response
                        updateBoard(response); // Ensure the board updates with the new state
                    },
                    error: function(xhr, status, error) {
                        console.error("Error during pawn promotion:", error);
                    }
                });
            });
        });
    });
});