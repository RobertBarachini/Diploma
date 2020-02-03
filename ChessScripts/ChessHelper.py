import chess
import chess.pgn
import numpy as np
import math
import BoardEvaluation as be

# game = chess.pgn.Game()
# game.headers["Event"] = "Example"
# node = game.add_variation(chess.Move.from_uci("e2e4"))
# node = node.add_variation(chess.Move.from_uci("e7e5"))
# node.comment = "Comment"

def get_nn_input_array(board):
    # Each square is represented by one-hot encoding 6 piece types of 2 colors = 12 array cells
    arr = [0] * 769 # 8 squares * 8 squares * 6 piece types * 2 colors + 1 turn
    for i in range(0, 64):
        piece = board.piece_at(i)
        if piece == None:
            continue
        arr[i * 12 + (piece.piece_type - 1 + 6 * piece.color)] = 1
    arr[len(arr) - 1] = board.turn
    return arr

def get_king_mobility(board, color):
    board_turn = board.turn
    board.turn = color
    mobility = 0
    legal_moves = board.legal_moves
    king_square = board.king(color)
    for move in legal_moves:
        if move.from_square == king_square:
            mobility += 1
    board.turn = board_turn
    return mobility

def get_king_distance_from_edge(board, color):
    king_square = board.king(color)
    king_file = chess.square_file(king_square) # 0 is a file
    king_rank = chess.square_rank(king_square) # 0 is first rank
    if king_file > 3:
        king_file = 7 - king_file
    if king_rank > 3:
        king_rank = 7 - king_rank
    return min(king_file, king_rank)

def get_kings_distance_euclidean(board):
    king_white_square = board.king(True)
    king_black_square = board.king(False)
    king_white_file = chess.square_file(king_white_square) 
    king_white_rank = chess.square_rank(king_white_square)
    king_black_file = chess.square_file(king_black_square) 
    king_black_rank = chess.square_rank(king_black_square)
    x = abs(king_white_file - king_black_file)
    y = abs(king_white_rank - king_black_rank)
    return math.sqrt(x ** 2 + y ** 2)


def get_kings_distance_moves(board):
    king_white_square = board.king(True)
    king_black_square = board.king(False)
    distance = chess.square_distance(king_white_square, king_black_square)
    return distance

def get_score_from_result_string(result):
    if result == "1-0":
        return 0 # win
    elif result == "0-1":
        return 1 # loss
    else:
        return 2 # draw

def get_score_from_result_string_relative(result, perspective):
    rez = 1
    if result == "1-0":
        rez =  0 # win
    elif result == "0-1":
        rez = 1 # loss
    else:
        rez = 2 # draw

    if rez == 0:
        if perspective:
            return 0
        else:
            return 1
    # elif rez == 1:
    else:
        if perspective:
            return 1
        else:
            return 0
    # return rez

knight_board = [
    [5,4,3,2,3,2,3]
]

# Gets estimated number of moves needed for a piece at p1 to get to p2
def get_moves_from_piece(pa1, pa2):
    moves_total = 0
    p1 = pa1[1]
    p2 = pa2[1]
    sq1 = pa1[0]
    sq2 = pa2[0]
    if p1.piece_type == 1: # PAWN
        moves_total += abs(chess.square_rank(sq1) - chess.square_rank(sq2))
    elif p1.piece_type == 2: # KNIGHT
        # TODO
        moves_total = 3 # idk for now
    elif p1.piece_type == 3: # BISHOP
        rank_diff = abs(chess.square_rank(sq1) - chess.square_rank(sq2))
        file_diff = abs(chess.square_file(sq1) - chess.square_file(sq2))
        if not (rank_diff == 0 and file_diff == 0): # didn't move
            if rank_diff == file_diff:
                moves_total += 1 # diagonal
            else:
                moves_total += 2 # 2 moves
    elif p1.piece_type == 4: # ROOK
        if abs(chess.square_rank(sq1) - chess.square_rank(sq2)) != 0:
            moves_total += 1
        if abs(chess.square_file(sq1) - chess.square_file(sq2)) != 0:
            moves_total += 1   
    elif p1.piece_type == 5: # QUEEN
        if abs(chess.square_rank(sq1) - chess.square_rank(sq2)) != 0:
            moves_total += 1
        if abs(chess.square_file(sq1) - chess.square_file(sq2)) != 0:
            moves_total += 1   
    elif p1.piece_type == 6: # KING
        moves_total = chess.square_distance(sq1, sq2)   
    return moves_total

# Returns the estimation of moves needed between two position for all pieces
# b1 and b2 being the two boards
# TODO implement the case of promotions
def get_moves_from_pieces_total(b1, b2):
    # Testing boards
    # b1 = chess.Board("6k1/3R4/4K3/8/1R6/8/8/8 b - - 0 1")
    # b2 = chess.Board("8/8/7R/8/8/5K1k/8/8 b - - 0 1")
    pieces_white_1 = be.get_pieces(b1, True)
    pieces_black_1 = be.get_pieces(b1, False)
    pieces_white_2 = be.get_pieces(b2, True)
    pieces_black_2 = be.get_pieces(b2, False)
    moves_total = 0
    # Determine piece coupling relations - e.g. which pieces seem to match
    # Each list holds pieces of one piece type starting with white pieces
    piece_groups_1 = [[],[],[],[],[],[],[],[],[],[],[],[]]
    piece_groups_2 = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for p in pieces_white_1 + pieces_black_1:
        piece = b1.piece_at(p)
        piece_index = piece.piece_type + ((not piece.color) * 6) - 1
        piece_groups_1[piece_index].append([p, piece])
    for p in pieces_white_2 + pieces_black_2:
        piece = b2.piece_at(p)
        piece_index = piece.piece_type + ((not piece.color) * 6) - 1
        piece_groups_2[piece_index].append([p, piece])
    for pg1, pg2 in zip(piece_groups_1, piece_groups_2):
        while len(pg2) > 0:
            min_moves_num = float("inf")
            match_pg1 = None
            match_pg2 = None
            for p2 in pg2:
                for p1 in pg1:
                    cur_moves = get_moves_from_piece(p1, p2)
                    if cur_moves < min_moves_num:
                        min_moves_num = cur_moves
                        match_pg1 = p1[0] # matching square to remove
                        match_pg2 = p2[0]
                    if cur_moves == 0:
                        break
                if cur_moves == 0:
                    break
            moves_total += min_moves_num
            # Remove from list
            for c in range(0, len(pg1)):
                if pg1[c][0] == match_pg1:
                    del pg1[c]
                    break
            for c in range(0, len(pg2)):
                if pg2[c][0] == match_pg2:
                    del pg2[c]
                    break
        # Adjust for taken pieces
        moves_total += len(pg1) * 2


    return moves_total

# Input neurons
# board = chess.Board()
# nn_input_array = get_nn_input_array(board)

# King mobility
# board = chess.Board("6k1/3R4/8/8/8/8/8/K7 w - -")
# print(get_king_mobility(board, True))
# print(get_king_mobility(board, False))

# King distance from edge
# color = False
# board = chess.Board("7k/8/8/8/8/3R4/2K5/8 w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("8/8/8/8/8/3R4/2K5/7k w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("8/8/8/8/8/3R4/2K5/7k w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("k7/8/8/8/8/3R4/2K5/8 w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# color = True
# board = chess.Board("7K/8/8/8/8/3R4/2k5/8 w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("8/8/8/8/8/3R4/2k5/7K w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("8/8/8/8/8/3R4/2k5/7K w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))
# board = chess.Board("K7/8/8/8/8/3R4/2k5/8 w - -")
# print(board)
# print(get_king_distance_from_edge(board, color))

# Distance between kings
# board = chess.Board("7k/R7/8/3K4/8/8/8/8 w - -")
# print(board)
# print(get_kings_distance_moves(board))
# print(get_kings_distance_euclidean(board))

# Test get_moves_from_pieces_total
# get_moves_from_pieces_total(None, None)