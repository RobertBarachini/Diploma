import chess
import chess.pgn
import chess.syzygy
import chess.gaviota
import glob
import os
import matplotlib.pyplot as plt
import ChessHelper as ch
import math

# Init tablebase
tablebase_dtz = chess.syzygy.open_tablebase("syzygy")
tablebase_gaviota = chess.gaviota.open_tablebase("Gaviota")
metric_options = ["dtz", "dtm"]
metric_setup = metric_options[1]

def get_dtz(board):
    dtz = tablebase_dtz.probe_dtz(board)
    # Handle errors?
    return dtz

def get_dtm(board):
    dtm = tablebase_gaviota.probe_dtm(board)
    return dtm
    
def analyze_game(filename):
    pgn = open(filename)
    game = chess.pgn.read_game(pgn)
    result = game.headers["Result"]
    board = game.board()
    init_dtz = get_dtz(board)
    init_dtm = get_dtm(board)
    print(filename)
    print(board)
    print(board.fen())
    print("Result:", result)
    print("Board wdl:", tablebase_dtz.probe_wdl(board))
    print("Init dtz:", init_dtz)
    print("Init dtm:", init_dtm)

    # Adjust to dtm
    if metric_setup == "dtm":
        init_dtz = init_dtm

    counter = init_dtz
    dtz_mem = [init_dtz]
    for move in game.mainline_moves():
        board.push(move)
        new_dtz = 0
        # Adjust to dtm
        if metric_setup == "dtm":
            new_dtz = get_dtz(board)
        else:
            new_dtz = get_dtm(board)
        dtz_mem.append(new_dtz)
        counter -= 1
        # print("New dtz:", new_dtz)
        # print("Expected dtz:", counter)
        # print("")
        if counter == 0:
            break
    print("------------------------------------")
    print("")
    return [dtz_mem, result]

def write_to_file(contents, filename):
    with open(filename, "w") as text_file:
        text_file.write(contents)

def save_game(game, filename):
    str_builder = []
    for dtz_val in game[0]:
        str_builder.append(str(dtz_val))
        str_builder.append(" ")
    str_builder.append("\n")
    str_builder.append(game[1])
    contents = ''.join(str_builder)
    write_to_file(contents, filename)

def get_average_difference_from_perfect_game(perfect, average):
    total = 0
    for dtz in zip(perfect, average):
        diff = abs(dtz[0] - dtz[1])
        total += diff
    return total / len(perfect)

def analyze_games(folder):
    folder_match = os.path.join(folder,"*.pgn")
    files = glob.glob(folder_match)
    games = [[], []]
    for file in files:
        game = analyze_game(file)
        dtz_filename = file.replace(".pgn", ".csv")
        save_game(game, dtz_filename)
        # # dtz is stored as first element
        # # add only games that are perfect or longer than dtz
        # if len(game) >= game[0]: 
        #     games.append(game)
        games[0].append(game[0])
        games[1].append(game[1])
    return games

def draw_graph_absolute_dtz(games, plot_name, source_path):
    dtz = games[0][0][0]
    average_game = [0] * (dtz + 1)
    average_game_visits = [0] * (dtz + 1)
    # games.append([11, 8, 3, 0])
    for game in games[0]:
        counter = 0
        for dtz_val in game:
            average_game[counter] += dtz_val
            average_game_visits[counter] += 1
            counter += 1
    # average_game[:] = [x / len(games) for x in average_game]
    avg_game_temp = average_game
    average_game = []
    counter = 0
    for dtz_val in avg_game_temp:
        visits = average_game_visits[counter]
        if visits == 0:
            break
        else:
            average_game.append(dtz_val / visits)

    average_game_abs = [abs(x) for x in average_game]
    counter = 1
    plt.grid(True)
    plt.xlim(dtz, 0)
    wins = 0
    draws = 0
    losses = 0
    total = 0
    # games[1] = ["1/2-1/2", "1-0", "0-1"]

    for game in zip(games[0], games[1]):
        game_abs = [abs(x) for x in game[0]]
        xs = list(reversed(list(range(dtz + 1 - len(game_abs), dtz + 1))))
        result = game[1]
        result_val = ch.get_score_from_result_string(result)
        color = "orange"
        if result_val == 0:
            color = "green"
            wins += 1
        elif result_val == 1:
            color = "red"
            losses += 1
        else:
            color = "orange"
            draws += 1
        total += 1
        # plt.plot(xs, game_abs, label = "n" + str(counter), color=color, linewidth=0.5)
        plt.plot(xs, game_abs, label = "_nolegend_", color=color, linewidth=0.5)
        counter += 1
    xs = list(reversed(list(range(0, dtz + 1))))
    plt.plot(xs, xs, label =  metric_setup + " (optimal)", color="cyan", linewidth=3)
    avg_dtz = get_average_difference_from_perfect_game(xs, average_game_abs)
    plt.plot(xs, average_game_abs, label = metric_setup + " (avg.) ; dev: " + str(round(avg_dtz, 2)), color="blue", linewidth=3)
    average_filename = os.path.join(source_path, "average.csv")
    average_result = str(wins) + "/" + str(wins + draws + losses)
    save_game([average_game_abs, average_result], average_filename)
    plt.xlabel("Perfect game " + metric_setup)
    plt.ylabel("Current " + metric_setup)
    plt.plot([],[], label="Wins: " + str(wins) , color="green")
    plt.plot([],[], label="Draws: " + str(draws), color="orange")
    plt.plot([],[], label="Losses: " +str(losses), color="red")
    plt.title(plot_name)
    plt.legend()
    plt.savefig(os.path.join(source_path, "plot_" + plot_name + ".pdf")) #, bbox_inches='tight')
    # plt.show()
    plt.clf()

def analyze_all_subfolders(root_folder):
    subfolders = list(reversed(list(os.walk(root_folder))))
    subfolders.pop()
    for folder in subfolders:
        if "plots" in folder[0]:
            continue
        source_path = str(folder[0]) #os.path.join(root_folder, folder)
        plot_name = str(os.path.basename(os.path.normpath(source_path)))
        games = analyze_games(source_path)
        draw_graph_absolute_dtz(games, plot_name, source_path)

# source_path = "PGN/arena_3/KRvk 5 MCTS_all same"
# plot_name = os.path.basename(os.path.normpath(source_path))
# games = analyze_games(source_path)
# draw_graph_absolute_dtz(games)

if __name__ == "__main__":
    analyze_all_subfolders("PGN\\MCTS_X_1")

    # print(get_dtm(chess.Board("6k1/8/4K3/8/8/8/5Q2/8 w - -")))