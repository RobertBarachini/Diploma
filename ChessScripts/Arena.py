import time
import chess
import chess.pgn
import BoardEvaluation as be
# import SearchAlgorithms as sa
import ChessHelper as ch
import mcts
import os
import glob
# import mcts
# import NOVA_MCTS as mcts
# import NOVA_MCTS_6 as mcts
import NOVA_MCTS_X as mcts
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("engine/stockfish/stockfish_10_x64.exe")

# Arena config
config_endgame = ["KQvk", "KRvk", "KRRvk"]
#config_endgame = ["KRvk"]
# config_endgame = ["KBBvk"]

config_dtz = ["5", "11"]
# config_dtz = ["5"]
#config_dtz = ["11"]

config_white_as = ["MCTS_basic", "MCTS_mobility", "MCTS_all"]
# config_white_as = ["MCTS_basic", "MCTS_all"]
# config_white_as = ["MCTS_all"]

config_black_as = ["same", "stockfish"]
# config_black_as = ["same"]
# config_black_as = ["stockfish"]

games_per_arena = 50 # 5, 10, 30, 50, 100
start_counting_games_at = 1 # to continue where you left off
max_games = 50 # 30, 50, 100
root_folder = "PGN\\MCTS_X_1"
stockfish_time_limit = 5 # 0.5, 1, 5, 10
mcts._Debug = True
# mcts._NODE_TYPE_SELECTION = mcts._NODE_BY_FAKTOR

def get_config_name(endgame, dtz, white, black):
    return endgame + " " + dtz + " " + white + " " + black

def get_game_count(directory):
    folder_match = os.path.join(directory,"*.pgn")
    files = glob.glob(folder_match)
    max_num = len(files)
    return max_num

def play_game(endgame, dtz, white, black):
    game_name = get_config_name(endgame, dtz, white, black)
    game_directory = os.path.join(root_folder, game_name)
    game_count = get_game_count(game_directory) + 1
    max_moves = int(dtz)
    if game_count >= max_games + 1:
        return
    if not os.path.exists(game_directory):
        os.makedirs(game_directory)
    print(game_name + " ;; " + str(game_count))

    starting_fen = ""
    if dtz == "5": # 5
        mcts.max_playouts = 500 # 500
        if endgame == "KQvk": # KQvk
            starting_fen = "6k1/8/4K3/8/8/8/5Q2/8 w - -"
        elif endgame == "KRvk": # KRvk
            starting_fen = "6k1/3R4/4K3/8/8/8/8/8 w - -"
        elif endgame == "KRRvk": # KRRvk
            starting_fen = "8/6k1/8/2R5/1R6/8/5K2/8 w - -"
        elif endgame == "KBBvk": # KBBvk
            starting_fen = "k7/8/4B3/1KB5/8/8/8/8 w - -"
        elif endgame == "KBNvk": # KBNvk
            starting_fen = "k7/2K5/3NB3/8/8/8/8/8 w - -"
    else: # dtz == config_dtz[1]: # 11
        mcts.max_playouts = 1100
        if endgame == "KQvk": # KQvk
            starting_fen = "8/8/8/3k4/8/2QK4/8/8 w - -"
        elif endgame == "KRvk": # KRvk
            starting_fen = "3k4/8/1RK5/8/8/8/8/8 w - -"
        elif endgame == "KRRvk": # KRRvk
            starting_fen = "8/8/8/4k3/8/8/RK6/R7 w - -"
        elif endgame == "KBBvk": # KBBvk
            starting_fen = "1k6/8/8/2KB4/3B4/8/8/8 w - -"
        elif endgame == "KBNvk": # KBNvk
            starting_fen = "1k6/8/4B3/2K5/8/5N2/8/8 w - - "

    starting_board = chess.Board(starting_fen)
    board = chess.Board(starting_fen)
    print("Starting board:")
    print(board)

    # mcts

    move = 1
    mcts.playMoneCarlo_init(chess.Board(board.fen()))
    best_move = None
    while not board.is_game_over(claim_draw = True):
        if get_game_count(game_directory) >= max_games:
            return
        time_start = time.time()
        #best_move, score = sa.get_best_move(board)
        if board.turn == True:
            if white == "MCTS_basic":
                mcts._OPT_SIMULATION = False
            elif white == "MCTS_mobility":
                mcts._OPT_SIMULATION = True
                mcts._OPT_TREE_MATE = False
                mcts._OPT_SPECIFIC_HERISTIC = False
                mcts._OPT_DETECT_CAPTURING_PIECE = False
                mcts._OPT_MOBILITY = True 
                mcts._OPT_KING_EDGE = False
                mcts._OPT_DISTANCE_BETWEEN_KINGS = False
            else: # All
                mcts._OPT_SIMULATION = True
                mcts._OPT_TREE_MATE = True
                mcts._OPT_SPECIFIC_HERISTIC = False
                mcts._OPT_DETECT_CAPTURING_PIECE = True
                mcts._OPT_MOBILITY = True 
                mcts._OPT_KING_EDGE = True
                mcts._OPT_DISTANCE_BETWEEN_KINGS = True
            # best_move, wins, playouts = mcts.playMoneCarlo(chess.Board(board.fen()))
            # best_move, wins, playouts = mcts.playMoneCarlo_move(best_move)
            best_move, wins, playouts = mcts.get_best_move()
            # mcts.push_move(best_move)
        else:
            if black == "same":
                if white == "MCTS_basic":
                    mcts._OPT_SIMULATION = False    
                elif white == "MCTS_mobility":
                    mcts._OPT_SIMULATION = True
                    mcts._OPT_TREE_MATE = False
                    mcts._OPT_SPECIFIC_HERISTIC = False
                    mcts._OPT_DETECT_CAPTURING_PIECE = False
                    mcts._OPT_MOBILITY = True 
                    mcts._OPT_KING_EDGE = False
                    mcts._OPT_DISTANCE_BETWEEN_KINGS = False
                else: # All
                    mcts._OPT_SIMULATION = True
                    mcts._OPT_TREE_MATE = True
                    mcts._OPT_SPECIFIC_HERISTIC = False
                    mcts._OPT_DETECT_CAPTURING_PIECE = True
                    mcts._OPT_MOBILITY = True 
                    mcts._OPT_KING_EDGE = True
                    mcts._OPT_DISTANCE_BETWEEN_KINGS = True
                # best_move, wins, playouts = mcts.playMoneCarlo(chess.Board(board.fen()))
                # best_move, wins, playouts = mcts.playMoneCarlo_move(best_move)
                best_move, wins, playouts = mcts.get_best_move()
                # mcts.push_move(best_move)
            elif black == "stockfish":
                result = engine.play(chess.Board(board.fen()), chess.engine.Limit(time=stockfish_time_limit))
                print("Result:", result.move)
                print("Eval:", result)
                best_move = result.move
                print(board)

        time_end = time.time()
        print("Move " + str(move) + " in " + str(round(time_end - time_start, 3)), "s")
        print(board.fen())
        # Added mcts.push_move ...
        mcts.push_move(best_move)
        board.push(best_move)
        print(board)
        print()
        move += 1
        if move > max_moves:
           break
    print()
    print(board)
    print(board.fen())
    print()
    result_pgn = chess.pgn.Game.from_board(board)
    result_pgn.result = board.result(claim_draw = True)
    print(result_pgn)
    # Added for parallel terminals
    game_count = get_game_count(game_directory) + 1
    filename_final = os.path.join(game_directory, str(game_count) + ".pgn")
    with open(filename_final, "w") as output_file:
        output_file.write(str(result_pgn))
    print()
    print("GAME OVER")    

def play_all_configs():
    for endgame in config_endgame:
        for dtz in config_dtz:
            for white in config_white_as:
                for black in config_black_as:
                    for i in range(0, games_per_arena):
                        # game_count = start_counting_games_at + i
                        play_game(endgame, dtz, white, black)


play_all_configs()
#get_game_count("PGN\\test")

# END
engine.quit()
input("Press any key to continue")