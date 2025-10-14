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

        # Knight pos evaluation table
        self.knight_pst = [
            [-50, -40, -30, -30, -30, -30, -40, -50],  
            [-40, -20,   0,   0,   0,   0, -20, -40],  
            [-30,   0,  10,  15,  15,  10,   0, -30],  
            [-30,   5,  15,  20,  20,  15,   5, -30],  
            [-30,   0,  15,  20,  20,  15,   0, -30], 
            [-30,   5,  10,  15,  15,  10,   5, -30],  
            [-40, -20,   0,   5,   5,   0, -20, -40],  
            [-50, -40, -30, -30, -30, -30, -40, -50]   
        ]

        # white king pos evaluation table
        self.white_king_pst = [
            [ 20,  30,  10,   0,   0,  10,  30,  20],  
            [-10, -10, -20, -30, -30, -20, -10, -10],  
            [-30, -40, -50, -60, -60, -50, -40, -30],  
            [-50, -60, -70, -80, -80, -70, -60, -50],  
            [-70, -80, -90,-100,-100, -90, -80, -70],  
            [-80, -90,-100,-110,-110,-100, -90, -80],  
            [-90,-100,-110,-120,-120,-110,-100, -90],  
            [-100,-110,-120,-130,-130,-120,-110,-100]  
        ]

        # black king pos evaluation table
        self.black_king_pst = [
            [-100,-110,-120,-130,-130,-120,-110,-100],
            [-90,-100,-110,-120,-120,-110,-100, -90], 
            [-80, -90,-100,-110,-110,-100, -90, -80], 
            [-70, -80, -90,-100,-100, -90, -80, -70], 
            [-50, -60, -70, -80, -80, -70, -60, -50], 
            [-30, -40, -50, -60, -60, -50, -40, -30], 
            [-10, -10, -20, -30, -30, -20, -10, -10], 
            [ 20,  30,  10,   0,   0,  10,  30,  20]  
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
    

    def get_king_positional_value(self, is_white=True):
        positional_value = 0

        if is_white:
            kings = self.board.white_king
            pst = self.white_king_pst
        else:
            kings = self.board.black_king
            pst = self.black_king_pst

        temp_kings = kings
        while temp_kings:
            square = (temp_kings & -temp_kings).bit_length() - 1
            temp_kings &= temp_kings - 1

            row, col = divmod(square, 8)
            positional_value += pst[row][col]

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
        knight_positional = self.get_knight_positional_value(is_white)
        king_positional = self.get_king_positional_value(is_white)

        material_value += knight_positional
        material_value += king_positional
        return material_value
        

    def evaluate(self):
        white_total = self.count_positional(True) 
        black_total = self.count_positional(False)
        
        return white_total - black_total
    

    def get_material_balance(self):
        """Calculate material balance including positional factors"""
        white_total = self.count_positional(True)  # Use positional instead of just material
        black_total = self.count_positional(False)
        total_material = white_total + black_total

        if total_material == 0:
            return 50.0 
        
        white_percentage = (white_total / total_material) * 100
        return round(white_percentage, 1)
    

    def get_evaluation_display(self):
        """Get a formatted string showing the evaluation"""
        white_total = self.count_positional(True)
        black_total = self.count_positional(False)

        advantage = white_total - black_total
        percentage = self.get_material_balance()
        
        if advantage > 0:
            return f"White advantage: +{advantage/100:.2f} ({percentage:.1f}%)"
        elif advantage < 0:
            return f"Black advantage: +{abs(advantage)/100:.2f} ({100-percentage:.1f}%)"
        else:
            return f"Equal position ({percentage:.1f}%)"
