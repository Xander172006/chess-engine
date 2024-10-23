$(document).ready(function() {
    console.log('Document is ready');

    let reloadTimeout;
    let exitPressed = false;

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
                    success: function(response) {
                        console.log("Moves received:", response);
                    },
                    error: function(xhr, status, error) {
                        console.error("Error getting moves:", error);
                    }
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

            // Reset exitPressed flag for new move
            exitPressed = false;

            // if piece is pawn:
            if (moveFrom && (moveFrom.piece === 'white_pawns' || moveFrom.piece === 'black_pawns')) {
                if (moveTo && (moveTo.notation[1] === '1' || moveTo.notation[1] === '8')) {
                    exitPressed = true;
                }
            }

            // Send move information
            if (clickCounter === 2) {
                console.log(exitPressed);
                validMove = true;

                if (!exitPressed) { // Check if the exit button was pressed
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

                                    // remove highlights
                                    $('.highlight').removeClass('highlight');
                                }, 500);
                            }
                        },
                        error: function(xhr, status, error) {
                            console.error("Error:", error);
                        }
                    });
                } else {
                    // show pawn promotion modal
                    showPawnPromotionModal(moveFrom, moveTo);
                }

                clickCounter = 0;
            }
        });
    });

    function showPawnPromotionModal(moveFrom, moveTo) {
        let promotionModal = $('#pawn-promotion-modal');
        
        // Get the position of the pawn
        let pawnSquare = $(`#square-${8 - parseInt(moveFrom.notation[1])}-${moveFrom.notation[0].charCodeAt(0) - 97}`);
        let pawnPosition = pawnSquare.offset();
        
        // Set the position of the modal
        promotionModal.css({
            top: 'auto',
            left: pawnPosition.left,
            display: 'block',
        });

        // Clear previous content
        promotionModal.empty();

        // Create list elements for each promotion piece
        let promotionPieces = ['queen', 'rook', 'bishop', 'knight'];
        let promotionList = document.createElement('ul');
        promotionList.classList.add('promotion-list');
        promotionPieces.forEach(piece => {
            let listItem = document.createElement('li');
            listItem.classList.add('promotion-button');
            // Add the images to the list items
            let imgItem = document.createElement('img');
            imgItem.src = `/static/assets/pieces/${moveFrom.color}_${piece}.png`; // Adjust the path here
            imgItem.alt = `${moveFrom.color} ${piece}`;
            listItem.appendChild(imgItem);

            listItem.dataset.pieceType = piece;
            promotionList.appendChild(listItem);
        });

        // Add exit button
        let exitButton = document.createElement('li');
        exitButton.classList.add('promotion-exit-button');
        exitButton.innerText = 'X';
        promotionList.appendChild(exitButton);

        // Add confirm button
        let confirmButton = document.createElement('li');
        confirmButton.classList.add('promotion-confirm-button');
        promotionList.appendChild(confirmButton);

        promotionModal.append(promotionList);

        clearTimeout(reloadTimeout); 

        let selectedPieceType = null;

        // Add event listeners for promotion buttons
        let promotionButtons = document.querySelectorAll('.promotion-button');
        promotionButtons.forEach(button => {
            button.addEventListener('click', function() {
                selectedPieceType = this.dataset.pieceType;
                // Highlight the selected piece
                promotionButtons.forEach(btn => btn.classList.remove('selected'));
                this.classList.add('selected');
            });
        });

        // Add event listener for confirm button
        confirmButton.addEventListener('click', function() {
            if (selectedPieceType) {
                $.ajax({
                    type: 'POST',
                    url: "/make_move",
                    contentType: 'application/json',
                    data: JSON.stringify({
                        position: moveFrom.notation,
                        placement: moveTo.notation,
                        name: selectedPieceType,
                        color: moveFrom.color
                    }),
                    success: function(response) {
                        updateBoard(response); 
                    },
                    error: function(xhr, status, error) {
                        console.error("Error during pawn promotion:", error);
                    }
                });
                $('#pawn-promotion-modal').hide();
            } else {
                alert('Please select a piece to promote to.');
            }
        });

        // Add event listener for exit button
        exitButton.addEventListener('click', function() {
            $('#pawn-promotion-modal').hide();
            exitPressed = true; // Set the flag to true when the exit button is pressed
            // Reset the move state
            moveFrom = null;
            moveTo = null;
            clickCounter = 0;
        });
    }

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
                reloadTimeout = setTimeout(() => {
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
    
        let deltaX = toPosition.left - fromPosition.left;
        let deltaY = toPosition.top - fromPosition.top;
    
        // Remove highlights before starting the animation
        $('.highlight').removeClass('highlight');
    
        // Add the piece-moving class to the piece
        piece.addClass('piece-moving');
    
        // Apply the translation
        piece.css({
            transform: `translate(${deltaX}px, ${deltaY}px)`
        });
    
        setTimeout(() => {
            // Remove the translation and piece-moving class after the animation
            piece.css({
                transform: ''
            });
            piece.removeClass('piece-moving');
    
            // Remove any piece already present in the target square
            toSquare.find('.piece').remove();
    
            // Move the capturing piece to the target square
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
    
                rook.addClass('piece-moving');
                rook.css({
                    transform: `translate(${rookToPosition.left - rookFromPosition.left}px, ${rookToPosition.top - rookFromPosition.top}px)`
                });
    
                setTimeout(() => {
                    rook.css({ transform: '' });
                    rook.removeClass('piece-moving');
                    rookToSquare.append(rook);
                }, 500);
            }
    
            // Handle en passant capture
            if (data.en_passant && data.captured_pawn_position) {
                let capturedPawnSquare = $(`#square-${8 - parseInt(data.captured_pawn_position[1])}-${data.captured_pawn_position[0].charCodeAt(0) - 97}`);
                capturedPawnSquare.find('.piece').remove();
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
    
        }, 500); // Match the duration of the CSS transition
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
        let promotionModal = $('#pawn-promotion-modal');
        
        // Get the position of the pawn
        let pawnSquare = $(`#square-${8 - parseInt(data.position[1])}-${data.position[0].charCodeAt(0) - 97}`);
        let pawnPosition = pawnSquare.offset();
        
        // Set the position of the modal
        promotionModal.css({
            top: 'auto',
            left: pawnPosition.left,
            display: 'block',
        });
    
        // Clear previous content
        promotionModal.empty();
    
        // Create list elements for each promotion piece
        let promotionPieces = ['queen', 'rook', 'bishop', 'knight'];
        let promotionList = document.createElement('ul');
        promotionList.classList.add('promotion-list');
        promotionPieces.forEach(piece => {
            let listItem = document.createElement('li');
            listItem.classList.add('promotion-button');
            // Add the images to the list items
            let imgItem = document.createElement('img');
            imgItem.src = `/static/assets/pieces/${data.color}_${piece}.png`; // Adjust the path here
            imgItem.alt = `${data.color} ${piece}`;
            listItem.appendChild(imgItem);
    
            listItem.dataset.pieceType = piece;
            promotionList.appendChild(listItem);
        });
    
        // Add exit button
        let exitButton = document.createElement('li');
        exitButton.classList.add('promotion-exit-button');
        exitButton.innerText = 'X';
        promotionList.appendChild(exitButton);
    

        promotionModal.append(promotionList);
    
        clearTimeout(reloadTimeout); 
    
        let selectedPieceType = null;
    
        // Add event listeners for promotion buttons
        let promotionButtons = document.querySelectorAll('.promotion-button');
        promotionButtons.forEach(button => {
            button.addEventListener('click', function() {
                selectedPieceType = this.dataset.pieceType;
                // Highlight the selected piece
                promotionButtons.forEach(btn => btn.classList.remove('selected'));
                this.classList.add('selected');
            });
        });
    
        // Add event listener for confirm button
        confirmButton.addEventListener('click', function() {
            if (selectedPieceType) {
                $.ajax({
                    type: 'POST',
                    url: "/make_move",
                    contentType: 'application/json',
                    data: JSON.stringify({
                        position: data.position,
                        placement: data.newPosition,
                        name: selectedPieceType,
                        color: data.playerColor
                    }),
                    success: function(response) {
                        updateBoard(response); 
                    },
                    error: function(xhr, status, error) {
                        console.error("Error during pawn promotion:", error);
                    }
                });
                $('#pawn-promotion-modal').hide();
            } else {
                alert('Please select a piece to promote to.');
            }
        });
    
        // Add event listener for exit button
        exitButton.addEventListener('click', function() {
            $('#pawn-promotion-modal').hide();
            exitPressed = true; // Set the flag to true when the exit button is pressed
            // Reset the move state
            moveFrom = null;
            moveTo = null;
            clickCounter = 0;
        });
    });
});