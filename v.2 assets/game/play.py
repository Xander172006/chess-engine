from board import board
from pieces import pieces
from moves import moves
from rules import rules


class chessGame():
    def __init__(self):
        self.board = board()
        self.moves = moves(self.board)
        self.rules = rules(self.board)
    
    def play(self):
            print("=== Simple Bitboard Chess ===")
            print("Enter moves in format: from_square to_square (e.g., 'e2 e4')")
            print("Type 'quit' to exit, 'moves' to see available moves")

            while not self.rules.is_checkmate():
                self.board.print_board(highlight_moves=True)

                player = "White" if self.board.white_to_move else "Black"
                
                # Check if current player is in check
                if self.moves.is_king_in_check(self.board.white_to_move):
                    print(f"🚨 CHECK! {player} king is under attack! 🚨")
                
                move_input = input(f"{player} move: ").strip().lower()

                if move_input == 'quit':
                    print("Thanks for playing!")
                    break
                elif move_input == 'moves':
                    moves = self.moves.generate_all_moves()
                    if moves:
                        print(f"Available moves: {', '.join([f'{f}-{t}' for f, t in moves])}")
                    else:
                        print("No available moves!")
                    continue

                parts = move_input.split()
                if len(parts) != 2:
                    print("Invalid format! Use: from_square to_square (e.g., 'e2 e4')")
                    continue

                from_square, to_square = parts

                if not self.rules.is_valid_square(from_square) or not self.rules.is_valid_square(to_square):
                    print("Invalid square! Use format like 'e2' or 'h7'")
                    continue

                # First check if the move is in the list of possible moves
                legal_moves = self.moves.generate_all_moves()
                if (from_square, to_square) not in legal_moves:
                    print("Illegal move! Try again.")
                    continue

                # Then check if the move is actually legal (doesn't leave king in check)
                if not self.moves.is_move_legal(from_square, to_square):
                    # Check if the current player is in check
                    current_player_in_check = self.moves.is_king_in_check(self.board.white_to_move)
                    if current_player_in_check:
                        print("You are in check! You must move your king to safety or block the attack.")
                    else:
                        print("That move would put your king in check! Try another move.")
                    continue

                if self.moves.make_move(from_square, to_square):
                    print(f"Move made: {from_square} -> {to_square}")
                else:
                    print("Move failed! Try again.")


                winner = self.rules.get_winner()
                if winner:
                    self.display_board()
                    print(f"\n🎉 Game Over! {winner} wins! 🎉")


if __name__ == "__main__":
    game = chessGame()
    game.play()
