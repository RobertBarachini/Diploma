import random
import time
import chess
import math
import BoardEvaluation as be
import ChessHelper as ch
import json
import os

# EXPERIMENTAL FEATURES - Not the main program

# TODO / IDEAS
# - in addition to using depth when choosing the best move after simulation we could calculate
#   the rought number of moves needed to reach the end position at which the simulation stopped
#   from the original position - for kings - distance in squares, queens, rooks, bishops = max 2 moves
#   ... we would then use the number of moves to estimate how reasonable the final "mate" position is
#   starting from our current node - which means that we would discard mates which are very far away
#   from current position but got a lot of attention during the simulation phases

# - parallel - run the program with arguments - add parameter with number of workers e.g. 64 where each
#   child node would be its own process and use up a worker ... if we ran a "get best move" on a position
#   with 30 legal moves we would start 30 processes of rbts.py with input parameters which would then act as
#   a parent node... by doing so we would use up 30 workers and use the remaining 70 workers and distribute
#   them equally between the child preocesses - let's say each of the 30 child processes would get the
#   ability process 2 of its child nodes in parallel - the results and states would then be returned
#   by reading standard output asynchronously and the child processes would terminate upon completion
#   we could also log how many processes are active and distribute workers accordingly - in the end we would
#   choose the optiomal node the same way it is chosen now - we could also append the generated JSON from
#   terminated child processes with their own simulation trees to our own tree and preserve the calculated
#   progress. 

class mcts_node:
    # node_id = -1
    # fen = ""
    # turn = False
    # parent = None
    # move = None
    # children = []
    # visits = 0
    # score = 0
    # terminal = False
    # expanded = False

    def __init__(self):
        None

    def __init__(self, node_id, fen, turn, parent, move):
        self.node_id = -1
        self.fen = ""
        self.turn = False
        self.parent = None
        self.move = None
        self.children = []
        self.visits = 0
        self.score = 0 # used in formula
        self.wins = 0 # used to count number of wins
        self.terminal = False
        self.expanded = False
        # sum of depths at which a win was achieved
        self.depth_sum = 0 
        # Depth from current node where search was started
        self.depth = 0
        
        self.node_id = node_id
        self.fen = fen
        self.turn = turn
        self.parent = parent
        self.move = move


class mcts:
    # New random seed
    random.seed()

    # Algorithm settings
    _C = 100#math.sqrt(2)#1 #math.sqrt(2)
    max_playouts = 200 # 200
    max_simulation_moves = -1
    max_game_moves = -1
    select_expanded_mode = 0 # 0 == pick first child ; 1 == pick at random ; 2 pick heuristically
    max_moves_endgame = 32 # KRK
    def Init_Basic(self):
        self.print_every_n = 10
        self.game_moves = 0
        self.node_root = None
        self.node_current = None
        self.nodes_count = 0
        # Each element is a list of meta_data_single elements
        # One object per move
        self.meta_data = []
        # Each element is a list of elements where every element is an object with
        # variables created at the end of the four steps - one object per simulation
        self.meta_data_single = []

        # Default weights used in select_simulation_move()
        self.weight_mobility = 1
        self.weight_distance_king = 1
        self.weight_king_edge = 1
    
    # Debug settings
    _Debug = False
    _generate_json = True

    # Default construstor
    def __init__(self):
        self.Init_Basic()

    # Init object before starting
    def playMoneCarlo_init(self, board):
        self.Init_Basic()
        self.node_root = mcts_node(self.nodes_count, board.fen(), board.turn, None, None) 
        self.node_current = self.node_root
        self.nodes_count = 1

    # Return best move
    def get_best_move(self):
        can_print = False
        b = chess.Board(self.node_current.fen)
        if b.is_game_over(claim_draw=False):
            print("GAME OVER WHEN GETTING BEST MOVE")
            return
        if self.node_root == None:
            self.playMoneCarlo_init(b)
            self.nodes_count += 1
        # Do n-playouts
        self.iterate(self.max_playouts)
        # Select best move based on children of the current node
        best_nodes = []
        best_metric = float("-inf") 
        # TODO add others ways of selecting best move
        if can_print:
            print("SELECTING BEST MOVE")
        maximize_metric = False
        if maximize_metric == False:
            best_metric = float("inf")
        for child in self.node_current.children:
            avg_win_depth = float("inf")
            if child.score != 0:
                avg_win_depth = child.depth_sum / child.score
            chosen_metric = avg_win_depth * (child.score + 1) / (child.visits + 1)
            if can_print:
                print(str(child.score) + " / " + str(child.visits) + " : " + str(child.move) + " : " + str(chosen_metric) + " : avg. win depth: " + str(avg_win_depth))
            if chosen_metric == best_metric:
                best_nodes.append(child)
            elif (maximize_metric and chosen_metric > best_metric) or (maximize_metric == False and chosen_metric < best_metric):
                best_metric = chosen_metric
                best_nodes = [child]
        best_node = best_nodes[random.randrange(0, len(best_nodes))]
        if can_print:
            for potential_best in best_nodes:
                print(str(potential_best.move))
            print("Chosen:" + str(best_node.move))

        # Save json
        if self._generate_json:
            if can_print:
                print("Saving JSON of the current node ...")
            self.save_json(self.node_current, "rbts_last_move.json")
            if can_print:
                print("JSON Saved")

        # TODO CHECK WHAT TO RETURN
        return best_node            

    def iterate(self, count):
        for i in range(0, count):
            if i % self.print_every_n == 0:
                print("    (" + str(i + 0) + ")")
            self.iterate_single()

    # One completion of the 4 MCTS steps
    # TODO Print information
    def iterate_single(self):
        print_steps = False
        # Step 1
        if print_steps:
            print("Step 1")
        selected_node = self.step_selection(self.node_current)
        # Step 2
        if print_steps:
            print("Step 2")
        self.step_expansion(selected_node)
        selected_node_child = self.step_select_expanded(selected_node)
        # Step 3
        if print_steps:
            print("Step 3")
        simulation_object = self.step_simulation(selected_node)
        # Step 4
        if print_steps:
            print("Step 4")
        self.step_backpropagation(selected_node_child, simulation_object)
        # Save metadata
        self.update_metadata()

    def construct_meta_object(self):
        obj = {}
        obj["fen"] = self.node_current.fen
        obj["turn"] = self.node_current.turn
        obj["visits"] = self.node_current.visits
        obj["score"] = self.node_current.score
        obj["wins"] = self.node_current.wins
        obj["node_id"] = self.node_current.node_id
        return obj
    
    def update_metadata(self):
        obj = self.construct_meta_object()
        self.meta_data_single.append(obj)

    # Used for making graphs and such
    def save_metadata(self, filepath):
        final_obj = {}
        final_obj["meta_data"] = self.meta_data
        final_obj["max_playouts"] = self.max_playouts
        final_obj["max_simulation_moves"] = self.max_simulation_moves
        final_obj["max_game_moves"] = self.max_game_moves
        final_obj["select_expanded_node"] = self.select_expanded_mode
        final_obj["max_moves_endgame"] = self.max_moves_endgame
        final_obj["game_moves"] = self.game_moves
        final_obj["nodes_count"] = self.nodes_count
        final_obj["fen_start"] = self.node_root.fen
        final_obj["fen_end"] = self.node_current.fen
        with open(filepath, 'w') as output_file:
            json.dump(final_obj, output_file)

    # Push move if you wish to add to the tree
    # if move is not in possible raise exception
    def push_move(self, move):
        self.meta_data.append(self.meta_data_single)
        self.meta_data_single = []
        if self.node_current.expanded == False:
            self.step_expansion(self.node_current)
        for child in self.node_current.children:
            if child.move.from_square == move.from_square and child.move.to_square == move.to_square:
                self.node_current = child
                return
        print("Pushing move: ", move)
        print("Children:", len(self.node_current.children))
        for child in self.node_current.children:
            print(child.move)     
        raise Exception("Move is not valid.")
        
    # Default function for calculating the balancing formula
    # TODO - add ways of changing 0 visits = infinity
    def get_UCB1_value(self, node):
        node_visits = node.visits
        node_score = node.score
        parent_visits = node.parent.visits
        node_visits += 1
        node_score += 1
        parent_visits += 1
        #
        UCB1_avg = node_score / node_visits
        UCB1_balance = self._C * math.sqrt(math.log(parent_visits) / node_score)
        child_UCB1 = UCB1_avg + UCB1_balance
        return child_UCB1

    # MCTS Step 1
    # Selects new leaf node and returns it
    def step_selection(self, node):
        current = node
        while len(current.children) != 0:
            # print(current.node_id)
            best_nodes = []
            best_value = float("-inf")
            for child in current.children:
                new_value = self.get_UCB1_value(child)
                if new_value == best_value:
                    best_nodes.append(child)
                elif new_value > best_value:
                    best_value = new_value
                    best_nodes = [child]
            current = best_nodes[random.randrange(0, len(best_nodes))]
        return current
    
    # MCTS Step 2
    # Expands the previously unexpended leaf node
    def step_expansion(self, node):
        if node.expanded:
            return
        b = chess.Board(node.fen)
        legal_moves = b.legal_moves
        node.expanded = True
        for legal_move in legal_moves:
            b.push(legal_move)
            self.nodes_count += 1
            new_node = mcts_node(self.nodes_count, b.fen(), b.turn, node, legal_move)
            new_node.depth = node.depth + 1
            node.children.append(new_node)
            b.pop() 

    # MCTS Step 2 - select child of expanded node
    def step_select_expanded(self, node):
        selected_node = node # if no suitable children found return the node itself
        if self.select_expanded_mode == 0 and len(node.children) > 0: # pick first child
            selected_node = node.children[0]
        elif self.step_select_expanded == 1 and len(node.children) > 0: # pick random child
            selected_node = node.children[random.randrange(0, len(node.children))]
        elif self.step_select_expanded == 2:
            None # TODO heuristically pick which child of a leaf node to simulate
        return selected_node
        
    # MCTS Step 3
    # Returns score of a simulation - positive if win, negative if loss
    def step_simulation(self, node):
        # TODO implement different ways of simulation
        # 1 - Default random
        # 2 - Heuristics ...
        
        return_obj = {}

        can_print = False
        # 1 Default random
        moves_made = 0
        legal_moves_total_count = 0
        b = chess.Board(node.fen)
        b_start = chess.Board(node.fen)
        perspective = b.turn
        if can_print:
            print(b)
            print(str(b.fen))
            print()
        while b.is_game_over(claim_draw=True) == False:            
            legal_moves = list(b.legal_moves)
            legal_moves_total_count += len(legal_moves)
            selected_move = self.select_simulation_move(legal_moves, b)
            b.push(selected_move)
            moves_made += 1

            if can_print:
                print(b)
                print(str(b.fen))
                print(str(selected_move))
                print()
            # if moves_made >= 30:
            #     break

        if can_print:
            print("Moves made:" + str(moves_made))
            print("Legal moves count:" + str(legal_moves_total_count))
            print("")
        moves_to_final_pos = ch.get_moves_from_pieces_total(b_start, b)
        return_obj["moves_to_pos"] = moves_to_final_pos
        result_str = str(b.result())
        # result = ch.get_score_from_result_string(result_str)
        result = ch.get_score_from_result_string_relative(result_str, perspective)
        # print("Result" + str(result))
        rez = -1
        if result == 0:
            rez = 1
            if perspective: # white
                if can_print:
                    print("victory")
                    print(b)
                    print(b.fen())
                    print("Min moves:" + str(moves_to_final_pos))

        else:
            rez = -1
        
        return_obj["score"] = rez
        return_obj["end_at_depth"] = moves_made + node.depth
        return_obj["moves_made"] = moves_made

        return return_obj            

    # MCTS Step 4
    # Backpropagates the score of a simulation from the desired node to current root node
    def step_backpropagation(self, node, simulation_object):
        score = simulation_object["score"]
        end_at_depth_relative = simulation_object["end_at_depth"] - self.node_current.depth
        moves_made = simulation_object["moves_made"]
        current = node
        add_score = True # Turn
        score_abs = abs(score)
        while True: #current.parent != None:
            # If relative win was achieved for the color
            if (add_score and score > 0) or (add_score == False and score < 0):
                #current.score += score_abs
                # EDIT rbts_3 - moves scaled
                current.wins += score_abs
                current.score += self.get_moves_score(moves_made)
                current.depth_sum += end_at_depth_relative
                # if node.turn:
                #     print("BACKPROP WHITE")
            current.visits += 1                
            if current is self.node_current:
                break
            current = current.parent
            add_score = not add_score

    # Returns a scaled number from 0 to 1 depending on number of moves
    # made in the simulation step where max moves are chosen as preset
    # and 0 is maximum number of moves and 1 is optimal
    def get_moves_score(self, moves_made):
        # max_moves_endgame
        return 1 - (min(moves_made, self.max_moves_endgame) / self.max_moves_endgame)

    # Select best move for Step 3 Simulation
    # board serves as context and is used for calculating heuristics
    def select_simulation_move(self, legal_moves, board):
        mode = 1
        best_move = legal_moves[0]
        # Select random move from legal moves
        if mode == 0:
            best_move = legal_moves[random.randrange(0, len(legal_moves))]
        # Combination of different heuristic values - 1
        elif mode == 1:
            best_score = float("-inf")
            best_moves = []
            # Determine the weaker side based on board pieces
            # By design our current endgame objective focuses on white mating black
            # so weaker_side = False 
            weaker_side = False 
            check_one_move_mate = True
            # current edit - check previous versions
            for move in legal_moves:
                # if check_one_move_mate:
                #     b.push(move)
                #     result = ch.get_score_from_result_string_relative(board.result(claim_draw=False), not b.turn)
                #     if result == 0 and b.turn == weaker_side:
                #         return move
                #     b.pop()
                new_score = 0
                # 1 - weaker king mobility
                component_mobility = 0
                # weight_mobility = 1 # 1
                component_mobility = ch.get_king_mobility(board, weaker_side)
                component_mobility = component_mobility / 8 # normalize
                # Invert ; mobility = 0 = best if weaker_side is our opponent
                if weaker_side == board.turn:
                    component_mobility = 1 - component_mobility 
                # 2 - distance between kings
                component_distance_king = 0
                # weight_distance_king = 1 # 1
                component_distance_king = ch.get_kings_distance_moves(board)
                component_distance_king = component_distance_king / 7 # normalize
                # Invert
                if weaker_side == board.turn:
                    component_distance_king = 1 - component_distance_king
                # 3 - weaker king distance to edge
                component_king_edge = 0
                # weight_king_edge = 1 # 1
                component_king_edge = ch.get_king_distance_from_edge(board, weaker_side)
                component_king_edge = component_king_edge / 3 # normalize
                # Invert
                if weaker_side == board.turn:
                    component_king_edge = 1 - component_king_edge
                # 4 - clustering ???
                # 5 - king attacked
                # CALCULATE FINAL COMBINATION
                new_score = component_mobility * self.weight_mobility + component_distance_king * self.weight_distance_king + component_king_edge + self.weight_king_edge
                if new_score == best_score:
                    best_moves.append(move)
                elif new_score > best_score:
                    best_moves = [move]
                    best_score = new_score
            best_move = best_moves[random.randrange(0, len(best_moves))]
        return best_move

    # Save JSON of a node
    def save_json(self, node, filepath):
        new_json = self.construct_json(node)
        #print(str(json.dump    s(new_json, indent=4)))
        with open(filepath, "w") as output_file:
            output_file.write(str(json.dumps(new_json, indent=4)))

    # Construct JSON object based on a node object structure
    def construct_json(self, node, jobject = None):
        # At root
        if jobject == None:
            jobject = json.loads("{}")
        # Add current node properties
        jobject["id"] = node.node_id
        jobject["wins"] = node.score
        jobject["playouts"] = node.visits
        jobject["fen"] = node.fen
        jobject["children"] = []
        jobject["move"] = str(node.move)
        jobject["parent"] = None
        jobject["turn"] = node.turn
        if node.parent != None:
            jobject["parent"] = node.parent.node_id
        # Add children
        # TODO add a limiter which ads only n-best children to each node
        for child in node.children:
            child_jobject = self.construct_json(child)
            jobject["children"].append(child_jobject)
        return jobject

if __name__ == "__main__":
    b = chess.Board("4k3/1R6/4K3/8/8/8/8/8 w - -")
    mcts_object = mcts()
    mcts_object.playMoneCarlo_init(b)
    best_move = mcts_object.get_best_move()
    print(b)
    print(b.fen)
    print(str(best_move.move))
    print(chess.Board(best_move.fen))
    print(best_move.fen)
    print("END_SCRIPT")
