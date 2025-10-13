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

                legal_moves = self.moves.generate_all_moves()
                if (from_square, to_square) not in legal_moves:
                    print("Illegal move! Try again.")
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
