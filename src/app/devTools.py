class devTools:
    def __init__(self):
        self.EMPTY = 0
        self.FULL_BOARD = 0xFFFFFFFFFFFFFFFF

        # white
        self.WHITE_PAWNS = 0x000000000000FF00
        self.WHITE_KNIGHTS = 0x0000000000000042
        self.WHITE_BISHOPS = 0x0000000000000024
        self.WHITE_ROOKS = 0x0000000000000081
        self.WHITE_QUEEN = 0x0000000000000008
        self.WHITE_KING = 0x0000000000000010

        # black
        self.BLACK_PAWNS = 0x00FF000000000000
        self.BLACK_KNIGHTS = 0x4200000000000000
        self.BLACK_BISHOPS = 0x2400000000000000
        self.BLACK_ROOKS = 0x8100000000000000
        self.BLACK_QUEEN = 0x0800000000000000
        self.BLACK_KING = 0x1000000000000000

    def bitboard_to_array(self, bitboard):
        array = [[0 for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                if (bitboard >> (row * 8 + col)) & 1:
                    array[7 - row][col] = 1
        return array


    # chess coördination conversion (horizontal, vertical)
    def from_bitboard_to_chess_position(self, bitboard):
        position = bitboard.bit_length() - 1
        row = position // 8
        col = position % 8
        return (row, col)


    # bitboard creation (number)
    def create_bitboard(self, square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        return 1 << (rank * 8 + file)


    # chess notation conversion (letter)(number)
    def bitboard_to_square(self, bitboard):
        bit_to_square = []
        for rank in range(8):
            for file in range(8):
                bit_to_square.append(chr(file + ord('a')) + str(rank + 1))
        
        squares = []
        for i in range(64):
            if bitboard & (1 << i):
                squares.append(bit_to_square[i])
        
        return squares
    

    def print_bitboard(self, bitboard):
        board = self.bitboard_to_array(bitboard)
        for row in board:
            print(" ".join(str(cell) for cell in row))

    
