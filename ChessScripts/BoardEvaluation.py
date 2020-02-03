import chess

piece_evaluation_type = 0 # Default : 0
board_evaluation_type = 0 # Default : 0
endgame =  True # Default : False
winning_side = 1 # Default : 0 ; 0 = no winning side ; 1 = light ; 2 = dark
winning_side_draw_loss = True # Default : True
check_for_game_over = True # : Default : True

# PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
pieces_values_basic = [1, 3, 3, 5, 9, 1000] # Standard valuations

# Piece-Square Tables obtained from https://www.chessprogramming.org/Simplified_Evaluation_Function
# # pawn
# sv_pawn = [0,  0,  0,  0,  0,  0,  0,  0,
# 50, 50, 50, 50, 50, 50, 50, 50,
# 10, 10, 20, 30, 30, 20, 10, 10,
#  5,  5, 10, 25, 25, 10,  5,  5,
#  0,  0,  0, 20, 20,  0,  0,  0,
#  5, -5,-10,  0,  0,-10, -5,  5,
#  5, 10, 10,-20,-20, 10, 10,  5,
#  0,  0,  0,  0,  0,  0,  0,  0]

# # knight
# sv_knight = [-50,-40,-30,-30,-30,-30,-40,-50,
# -40,-20,  0,  0,  0,  0,-20,-40,
# -30,  0, 10, 15, 15, 10,  0,-30,
# -30,  5, 15, 20, 20, 15,  5,-30,
# -30,  0, 15, 20, 20, 15,  0,-30,
# -30,  5, 10, 15, 15, 10,  5,-30,
# -40,-20,  0,  5,  5,  0,-20,-40,
# -50,-40,-30,-30,-30,-30,-40,-50,]

# # bishop
# sv_bishop = [-20,-10,-10,-10,-10,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5, 10, 10,  5,  0,-10,
# -10,  5,  5, 10, 10,  5,  5,-10,
# -10,  0, 10, 10, 10, 10,  0,-10,
# -10, 10, 10, 10, 10, 10, 10,-10,
# -10,  5,  0,  0,  0,  0,  5,-10,
# -20,-10,-10,-10,-10,-10,-10,-20]

# # rook
# sv_rook = [0,  0,  0,  0,  0,  0,  0,  0,
# 5, 10, 10, 10, 10, 10, 10,  5,
# -5,  0,  0,  0,  0,  0,  0, -5,
# -5,  0,  0,  0,  0,  0,  0, -5,
# -5,  0,  0,  0,  0,  0,  0, -5,
# -5,  0,  0,  0,  0,  0,  0, -5,
# -5,  0,  0,  0,  0,  0,  0, -5,
# 0,  0,  0,  5,  5,  0,  0,  0]

# # queen
# sv_queen = [-20,-10,-10, -5, -5,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5,  5,  5,  5,  0,-10,
#  -5,  0,  5,  5,  5,  5,  0, -5,
#   0,  0,  5,  5,  5,  5,  0, -5,
# -10,  5,  5,  5,  5,  5,  0,-10,
# -10,  0,  5,  0,  0,  0,  0,-10,
# -20,-10,-10, -5, -5,-10,-10,-20]

# # king middle game
# sv_king = [-30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -20,-30,-30,-40,-40,-30,-30,-20,
# -10,-20,-20,-20,-20,-20,-20,-10,
#  20, 20,  0,  0,  0,  0, 20, 20,
#  20, 30, 10,  0,  0, 10, 30, 20]

# # king end game
# sv_king_endgame = [-50,-40,-30,-20,-20,-30,-40,-50,
# -30,-20,-10,  0,  0,-10,-20,-30,
# -30,-10, 20, 30, 30, 20,-10,-30,
# -30,-10, 30, 40, 40, 30,-10,-30,
# -30,-10, 30, 40, 40, 30,-10,-30,
# -30,-10, 20, 30, 30, 20,-10,-30,
# -30,-30,  0,  0,  0,  0,-30,-30,
# -50,-30,-30,-30,-30,-30,-30,-50]

# Needed to be reshaped because python-chess squares begin differently
# np.array(be.sv_pawn).reshape(8,8)[::-1].reshape(64)
# pawn
sv_pawn = [  0,   0,   0,   0,   0,   0,   0,   0,   5,  10,  10, -20, -20,
        10,  10,   5,   5,  -5, -10,   0,   0, -10,  -5,   5,   0,   0,
         0,  20,  20,   0,   0,   0,   5,   5,  10,  25,  25,  10,   5,
         5,  10,  10,  20,  30,  30,  20,  10,  10,  50,  50,  50,  50,
        50,  50,  50,  50,   0,   0,   0,   0,   0,   0,   0,   0]

# knight
sv_knight = [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20,   0,   5,   5,
         0, -20, -40, -30,   5,  10,  15,  15,  10,   5, -30, -30,   0,
        15,  20,  20,  15,   0, -30, -30,   5,  15,  20,  20,  15,   5,
       -30, -30,   0,  10,  15,  15,  10,   0, -30, -40, -20,   0,   0,
         0,   0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50]

# bishop
sv_bishop = [-20, -10, -10, -10, -10, -10, -10, -20, -10,   5,   0,   0,   0,
         0,   5, -10, -10,  10,  10,  10,  10,  10,  10, -10, -10,   0,
        10,  10,  10,  10,   0, -10, -10,   5,   5,  10,  10,   5,   5,
       -10, -10,   0,   5,  10,  10,   5,   0, -10, -10,   0,   0,   0,
         0,   0,   0, -10, -20, -10, -10, -10, -10, -10, -10, -20]

# rook
sv_rook = [ 0,  0,  0,  5,  5,  0,  0,  0, -5,  0,  0,  0,  0,  0,  0, -5, -5,
        0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,
        0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5,  5, 10, 10,
       10, 10, 10, 10,  5,  0,  0,  0,  0,  0,  0,  0,  0]

# queen
sv_queen = [-20, -10, -10,  -5,  -5, -10, -10, -20, -10,   0,   5,   0,   0,
         0,   0, -10, -10,   5,   5,   5,   5,   5,   0, -10,   0,   0,
         5,   5,   5,   5,   0,  -5,  -5,   0,   5,   5,   5,   5,   0,
        -5, -10,   0,   5,   5,   5,   5,   0, -10, -10,   0,   0,   0,
         0,   0,   0, -10, -20, -10, -10,  -5,  -5, -10, -10, -20]

# king middle game
sv_king = [ 20,  30,  10,   0,   0,  10,  30,  20,  20,  20,   0,   0,   0,
         0,  20,  20, -10, -20, -20, -20, -20, -20, -20, -10, -20, -30,
       -30, -40, -40, -30, -30, -20, -30, -40, -40, -50, -50, -40, -40,
       -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50,
       -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30]

# king end game
sv_king_endgame = [-50, -30, -30, -30, -30, -30, -30, -50, -30, -30,   0,   0,   0,
         0, -30, -30, -30, -10,  20,  30,  30,  20, -10, -30, -30, -10,
        30,  40,  40,  30, -10, -30, -30, -10,  30,  40,  40,  30, -10,
       -30, -30, -10,  20,  30,  30,  20, -10, -30, -30, -20, -10,   0,
         0, -10, -20, -30, -50, -40, -30, -20, -20, -30, -40, -50]

def get_pieces(board, color):
    squares = board.pieces(1, color)
    for i in range(2, 7):
        squares = squares | board.pieces(i, color)
    return list(squares)

def get_pieces_sorted(board, color):
    squares = board.pieces(1, color)
    for i in range(2, 7):
        squares = squares | board.pieces(i, color)
    return sorted(list(squares))

def get_game_over_score(board, color):
    current_fen = board.fen()
    current_board = str(board)
    if board.is_game_over(claim_draw = True):  # True may be slower but covers desired functionality
        result = board.result(claim_draw = True)[:2]
        # if result == "*":
        #     print("Hmmmmm")
        # if result == "*"
        if result == "1/" or result == "*": # Draw
            if winning_side_draw_loss:
                if (winning_side == 1 and color == True) or (winning_side == 2 and color == False):
                    return float("-inf")
                else:
                    return float("inf")
            else:
                return 0
        else:
            #if (result == "0-" and color == True) or (result == "1-" and color == False):
            if result == "0-":
                return float("-inf")
            else:
                return float("inf")
    else:
        return None
    
def get_board_value_pieces_difference(board, color):
    game_over_score = get_game_over_score(board, color)
    if game_over_score != None:
        return game_over_score
    pieces_light_count = len(get_pieces(board, True)) 
    pieces_dark_count = len(get_pieces(board, False)) 
    diff = pieces_light_count - pieces_dark_count
    # Adjust score for player's color perspective
    if (diff > 0 and color == False) or (diff < 0 and color == True):
        diff *= -1
    return diff

def get_board_value_pieces_difference_2(board, color):
    # TODO: Return difference of piece values summed (BASIC)
    return None

def get_board_value_pieces_difference_3(board, color):
    # TODO: Return difference of piece values summed (Based on piece position)
    if check_for_game_over: 
        game_over_score = get_game_over_score(board, color)
        if game_over_score != None:
            return game_over_score
    board_value_my = get_pieces_value(board, color)
    board_value_oponent = get_pieces_value(board, not color)
    return board_value_my - board_value_oponent

def get_piece_value(piece_type, piece_position = -1):
    piece_index = piece_type - 1 # According to python-chess library
    if piece_evaluation_type == 1:
        # PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
        if piece_index == 0:
            return sv_pawn[piece_position]
        elif piece_index == 1:
            return sv_knight[piece_position]
        elif piece_index == 2:
            return sv_bishop[piece_position]
        elif piece_index == 3:
            return sv_rook[piece_position]
        elif piece_index == 4:
            return sv_queen[piece_position]
        elif piece_index == 5:
            if endgame:
                return sv_king_endgame[piece_position]
            else:
                return sv_king[piece_position]
    else: # Default basic piece values
        return pieces_values_basic[piece_index]

def get_pieces_value(board, color):
    pieces = get_pieces(board, color)
    total_value = 0
    for piece in pieces:
        piece_value = get_piece_value(board.piece_at(piece).piece_type, piece)
        total_value += piece_value
    return total_value

def get_board_value(board, color): # color : chess.WHITE = True 
    board_value = 0
    if board_evaluation_type == 1:
        board_value = get_board_value_pieces_difference_2(board, color)
    elif board_evaluation_type == 2:
        board_value = get_board_value_pieces_difference_3(board, color)
    else:
        board_value = get_board_value_pieces_difference(board, color)
    return board_value