class Evaluator():
    def __init__(self, board, pieces):
        self.board = board
        self.pieces = pieces

        self.piece_values = {
            'P': 100,
            'N': 300,
            'B': 300,
            'R': 500,
            'Q': 900,
            'K': 0,
        }

        self.starting_material = 3900

        self.knight_pst =  self.knight_pst = [
            [-50, -40, -40, -40, -40, -40, -40, -50],
            [-40, -20,   0,   0,   0,   0, -20, -40], 
            [-40,   0,  10,  20,  20,  10,   0, -40],
            [-40,   0,  20,  25,  25,  20,   0, -40],
            [-40,   0,  20,  25,  25,  20,   0, -40],
            [-40,   0,  10,  20,  20,  10,   0, -40],
            [-40, -20,   0,   0,   0,   0, -20, -40],
            [-50, -40, -40, -40, -40, -40, -40, -50]
        ]


    def get_knight_positional_value(self, is_white=True):
        positional_value = 0

        if is_white:
            knights = self.board.white_knights
        else:
            knights = self.board.black_knights

        temp_knights = knights
        while temp_knights:
            square = (temp_knights & -temp_knights).bit_length() - 1
            temp_knights &= temp_knights - 1

            row, col = divmod(square, 8)
            
            if is_white:
                # 7-row to mirror for white
                positional_value += self.knight_pst[7-row][col]
            else:
                positional_value += self.knight_pst[row][col]

        return positional_value
        

    def count_material(self, is_white=True):
        """Count total material value for one side"""
        material_value = 0
        
        if is_white:
            material_value += bin(self.board.white_pawns).count('1') * self.piece_values['P']
            material_value += bin(self.board.white_knights).count('1') * self.piece_values['N']
            material_value += bin(self.board.white_bishops).count('1') * self.piece_values['B']
            material_value += bin(self.board.white_rooks).count('1') * self.piece_values['R']
            material_value += bin(self.board.white_queen).count('1') * self.piece_values['Q']
        else:
            material_value += bin(self.board.black_pawns).count('1') * self.piece_values['P']
            material_value += bin(self.board.black_knights).count('1') * self.piece_values['N']
            material_value += bin(self.board.black_bishops).count('1') * self.piece_values['B']
            material_value += bin(self.board.black_rooks).count('1') * self.piece_values['R']
            material_value += bin(self.board.black_queen).count('1') * self.piece_values['Q']
            
        return material_value
    

    def count_positional(self, is_white=True):
        """Count material value including positional bonuses"""
        material_value = self.count_material(is_white)
        knight_postional = self.get_knight_positional_value(is_white)
        material_value += knight_postional
        return material_value
        

    def evaluate(self):
        white_material = self.count_material(True)
        black_material = self.count_material(False)

        return white_material - black_material
    

    def get_material_balance(self):
        white_material = self.count_material(True)
        black_material = self.count_material(False)
        total_material = white_material + black_material

        if total_material == 0:
            return 50.0 
        
        white_percentage = (white_material / total_material) * 100
        return round(white_percentage, 1)
    

    def get_evaluation_display(self):
        """Get a formatted string showing the evaluation"""
        white_material = self.count_material(True)
        black_material = self.count_material(False)
        
        white_positional = self.get_knight_positional_value(True)
        black_positional = self.get_knight_positional_value(False)
        
        white_total = white_material + white_positional
        black_total = black_material + black_positional

        advantage = white_total - black_total
        percentage = self.get_material_balance()
        
        if advantage > 0:
            return f"White advantage: +{advantage/100:.1f} pawns ({percentage}%)"
        elif advantage < 0:
            return f"Black advantage: +{abs(advantage)/100:.1f} pawns ({100-percentage}%)"
        else:
            return f"Material equal ({percentage}%)"
