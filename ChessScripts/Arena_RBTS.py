import time
import chess
import chess.pgn
import BoardEvaluation as be
# import SearchAlgorithms as sa
import ChessHelper as ch
import os
import glob
import RBTS_3_moves as mcts
import chess.engine
import itertools
import sys

engine = chess.engine.SimpleEngine.popen_uci("engine/stockfish/stockfish_10_x64.exe")
starting_fen = "8/8/8/3k4/8/2QK4/8/8 w - -"
dtm = 11
max_games = 50 # 100
games_results = []
steps = [0, 0.1, 0.5, 1, 5, 10]
games_per_config = 50 # 50
root_folder = "PGN\\RBTS_3_5_test_3" 
stockfish_time_limit = 5 # 0.5, 1, 5, 10
description = ""
playouts = 200

def get_config_name(weights):
    name = ""
    for w in weights:
        wstr = str(w).replace(",", ".").replace(".", "p")
        name += wstr + "_"
    name = name[:-1]
    return name

def get_config_name_full(weights, gameiter):
    name = ""
    for w in weights:
        wstr = str(w).replace(",", ".").replace(".", "p")
        name += wstr + "_"
    name += "v" + str(gameiter)
    return name

def get_game_count(directory):
    folder_match = os.path.join(directory,"*.pgn")
    files = glob.glob(folder_match)
    max_num = len(files)
    return max_num

def play_game(weights, game_count):
    game_name = get_config_name(weights)
    game_directory = os.path.join(root_folder, game_name)
    game_count = get_game_count(game_directory) + 1
    max_moves = int(dtm)
    if game_count >= max_games + 1:
        return
    if not os.path.exists(game_directory):
        os.makedirs(game_directory)
    starting_board = chess.Board(starting_fen)
    board = chess.Board(starting_fen)
    print(game_name + " ;; " + str(game_count))
    print("Starting board:")
    print(board)
    # mcts
    move = 1
    best_move = None
    mcts_object = mcts.mcts()
    mcts_object.playMoneCarlo_init(board)
    mcts_object.max_playouts = playouts
    # Set weights
    mcts_object.weight_distance_king = weights[0]
    mcts_object.weight_king_edge = weights[1]
    mcts_object.weight_mobility = weights[2]
    mcts_object.print_every_n = 50
    while not board.is_game_over(claim_draw = True):
        if get_game_count(game_directory) >= max_games:
            return
        time_start = time.time()
        #best_move, score = sa.get_best_move(board)
        if board.turn == True:
            best_node = mcts_object.get_best_move()
            best_move = best_node.move
            print("Alg best move:", best_move)
        else:
            result = engine.play(chess.Board(board.fen()), chess.engine.Limit(time=stockfish_time_limit))
            best_move = result.move
            print("Stockfish best move:", best_move)
            # print("Result:", result.move)
            # print("Eval:", result)
            # print(board)
        time_end = time.time()
        print("Move " + str(move) + " in " + str(round(time_end - time_start, 3)), "s")
        print(board.fen())
        # Added mcts.push_move ...
        board.push(best_move)
        print(board)
        print()
        mcts_object.push_move(best_move)
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

def play_games():
    # [mobility, dist, ...]
    weights = [0, 0, 0]
    witerations = list(itertools.product(steps, repeat=len(weights)))
    ilen = len(witerations) # = len(steps) ^ len(weights)
    print("Total iterations: " + str(ilen))
    for wi in witerations:
        weights = list(wi)
        if weights == [0, 0, 0]:
            continue
        for i in range(1, games_per_config + 1):
            play_game(weights, i)
    
if __name__ == "__main__":
    print("Main")
    play_games()
    print("END_SCRIPT")

engine.quit()