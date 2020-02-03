import chess
import chess.engine
import time
import math
import random
import BoardEvaluation as be
import ChessHelper as ch
import json
import os

# GLOBAL variables ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# simulation optimisation options
_Debug = True # print progress info and create variables for easier understanding
_generate_json = True
_DebugTree = False # printing detailed progress of tree nodes
max_playouts = 200 # 200 # 500 # 1000 # (how many playouts/simulations we run, before we play the actual move)
_C = math.sqrt(2) # 1 # 2 # 10 # 100 # 1000 # 0.1   # constant for tree balancing formula
max_simulation_moves = 0 # max. moves in single simulation (0 - skip this condition)
_CLAIM_DRAW = False # for chess.board library - comparison of this task is sufficient - and much faster (False is not considered to be over by the fifty-move rule or threefold repetition)

(_NODE_BY_WINS, _NODE_BY_PLAYOUTS, _NODE_BY_FAKTOR, _NODE_BY_SIM_STEPS) = range(4) # best node for play in tree node selection type in MonteCarlo alghorithem
# _NODE_BY_WINS - node with max. wins is best node for play
# _NODE_BY_PLAYOUTS - node with max. playouts is best node for play
# _NODE_BY_FAKTOR - node with max. value of formula (wins / playouts) is best node for play
# _NODE_BY_SIM_STEPS - node with max. value of formula (wins/simulatin steps)/ playouts is best node for play
_NODE_TYPE_SELECTION = _NODE_BY_SIM_STEPS


_OPT_TREE_MATE = True # detecting mate in one move and forced moves (opponent has only one next move which leeds to win)- when we chosoe next actual move in tree

_OPT_SIMULATION = False # False - random moves, True - below we activate more granual optimization options,
_OPT_SPECIFIC_HERISTIC = False # to enable specific heuristic for specific end game configuration
_OPT_DETECT_CAPTURING_PIECE = True # when one opponent has only a king, we avoid stupid moves
_OPT_MOBILITY = True # optimize pieces mobility 
_OPT_KING_EDGE = True # weaker king runs from edge
_OPT_DISTANCE_BETWEEN_KINGS = True # optimize distance between kings

# _DEBUG_SIM = True # print debugging simulation function (start board position, end board position)
# _DEBUG_SIM2 = True # print deep debugging  simulation function (each actual move in simulation)
# _DEBUG_SIM3 = True # print deep debugging  simulation function  (detailed testing moves in simulation before we find next actual move)

_DEBUG_SIM = False # print debugging simulation function (start board position, end board position)
_DEBUG_SIM2 = False# print deep debugging  simulation function (each actual move in simulation)
_DEBUG_SIM3 = False # print deep debuging  simulation function  (detailed testing moves in simulation before we find next actual move)

_DEBUG_ACTUAL_MOVE_CHILDS = True # print children before making actual move  
max_game_moves = 0 # how many actual final moves are allowed - (0 - skip this condition)
max_time_for_find_move = 0  # time in seconds to find best current move (0 - skip this condition)
max_game_time = 0 # max. seconds per game (0 - skip this condition)
_game_moves_num = 0 # number of moves in game
_root_tree_node = None # root node of tree
_game_type = None 
_play_node = None
(KRk, KQk, KRRk, KPPk, KBBk, KBNk) = range(6) # game types
(_ROOT, _DEPTH, _BREADTH) = range(3)
(_END_GAME, _TIME, _STEPS) = range(3) # Rules for stopping the simulation
(_SIM_MOVE_END_GAME, _SIM_MOVE_MOBILITY, _SIM_MOVE_RANDOM, _SIM_BACKTRACE_STUPID_MOVES, _SIM_KING_DISTANCE, _SIM_ONLY_ONE_MOVE) = range(6)  # Rules for last move in simulation
(_SEPERATED_BY_FILE, _SEPERATED_BY_RANK) = range(2)

(_TO_LOSE, _TO_WIN) = range(2) # branch type in tree - decisive branch that leeds us to win or lose


# obsolete OLD simulation code
_OPT_BACKTRACE_STUPID_MOVES = True # some moves decrease mobility, but we don't wish to check that instead we play a move and then make the check and backtrace if previous move was really stupid (offered - captured piece)
_OPT_MATE = True # next move is mate
# end obsolete OLD simulation code

_node_id = 0 # global ID for nodes in tree - each node gets unique number ID - for easier development/representation/visualization

_tree_min_level = 0
_tree_max_level = 0

# find game type from board
def get_game_type(board):
	game_type = None
	black_pieces_sq = be.get_pieces(board, chess.BLACK)
	if len(black_pieces_sq) == 1:
		white_pieces_sq = be.get_pieces(board, chess.WHITE)
		w_p = 0
		w_n = 0
		w_b = 0
		w_r = 0
		w_q = 0
		for sq in white_pieces_sq:
			piece_type = board.piece_type_at(sq)
			if piece_type == chess.PAWN:
				w_p += 1
			elif piece_type == chess.KNIGHT :
				w_n += 1
			elif piece_type == chess.BISHOP  :
				w_b += 1
			elif piece_type == chess.ROOK  :
				w_r += 1
			elif piece_type == chess.QUEEN  :
				w_q += 1
		if (w_p == 0) and (w_n == 0) and  (w_b == 0) and  (w_r == 1) and  (w_q == 0):
			game_type = KRk
		elif (w_p == 0) and (w_n == 0) and  (w_b == 0) and  (w_r == 0) and  (w_q == 1):
			game_type = KQk
	return game_type


# when game ends, get value points for node
def get_win_value(board_turn, result, propagate_node_turn):
	if result=='1-0': # win for white
		if (propagate_node_turn == False): # white node
			win = 1
		else:   # black node
			win = 0
	elif result=='0-1': # win for black
		if (propagate_node_turn == False): # white node
			win = 0
		else:   # black node
			win = 1
	else:
		#win = 0.5
		#draw or game was interrupted or time limit expired, max steps exceded - WHITE lose - special for end game with white material advantage
		if (propagate_node_turn == False): # white node
			win = 0  # no points for draw for white
		else: # black node
			win = 1  #
	return win

arrCenterManhattanDistance = [
  6, 5, 4, 3, 3, 4, 5, 6,
  5, 4, 3, 2, 2, 3, 4, 5,
  4, 3, 2, 1, 1, 2, 3, 4,
  3, 2, 1, 0, 0, 1, 2, 3,
  3, 2, 1, 0, 0, 1, 2, 3,
  4, 3, 2, 1, 1, 2, 3, 4,
  5, 4, 3, 2, 2, 3, 4, 5,
  6, 5, 4, 3, 3, 4, 5, 6
]

# get euclidean distance between 2 sqares
def get_distance_euclidean(sq1, sq2):  
	sq1_file = chess.square_file(sq1) 
	sq1_rank = chess.square_rank(sq1)
	sq2_file = chess.square_file(sq2) 
	sq2_rank = chess.square_rank(sq2)
	x = abs(sq1_file - sq2_file)
	y = abs(sq1_rank - sq2_rank)
	distance = math.sqrt(x ** 2 + y ** 2)
	return distance

# is sgare on edge of board
def is_square_on_edge(sq1):  
	sq1_file = chess.square_file(sq1) 
	sq1_rank = chess.square_rank(sq1)
	on_file = (sq1_file == 0) or (sq1_file == 7)
	on_rank = (sq1_rank == 0) or (sq1_rank == 7)
	if on_file:
		edge_on = _SEPERATED_BY_FILE
	else:
		edge_on = _SEPERATED_BY_RANK
	return on_file or on_rank, edge_on


# calculate euclidean king distance, and if distece is 2, we return file or rank number of opposite king - which helps us to force OP king to the edge
def get_kings_distance_euclidean_opposition(board, revert):  
	if revert: # when we simulate our move, we just a move and we must switch sides, to get proper value of opposite king
		PS_king_square = board.king(not board.turn)
		OP_king_square = board.king(board.turn)
	else:
		PS_king_square = board.king(board.turn)
		OP_king_square = board.king(not board.turn)
	PS_king_file = chess.square_file(PS_king_square) 
	PS_king_rank = chess.square_rank(PS_king_square)
	OP_king_file = chess.square_file(OP_king_square) 
	OP_king_rank = chess.square_rank(OP_king_square)
	x = abs(PS_king_file - OP_king_file)
	y = abs(PS_king_rank - OP_king_rank)
	distance = math.sqrt(x ** 2 + y ** 2)
	if 2 == distance:
		if 2 == x:
			seperated_by = _SEPERATED_BY_FILE
			seperated_num = OP_king_file
		else:
			seperated_by = _SEPERATED_BY_RANK
			seperated_num = OP_king_rank
	else:
		seperated_by = None
		seperated_num = None
	return distance, seperated_by, seperated_num


def backpropagate_lose(node_to_lose):
	node_to_lose.branch_type = _TO_LOSE
	if node_to_lose.parent != None: # if parent exists and all other moves lead to loss, then it's a win for parent
		b_propagate_win = True
		for child in node_to_lose.parent.children:
			if child.branch_type != _TO_LOSE:
				b_propagate_win = False
				break
		if b_propagate_win:
			backpropagate_win(node_to_lose.parent) # parent has a win if all his children lead to loss


def backpropagate_win(node_to_win):
	node_to_win.branch_type = _TO_WIN
	if node_to_win.parent != None:
		backpropagate_lose(node_to_win.parent)  # every child win move is loss for parent

class mctree(object):
	def __init__(self, fen, node_id = None, move_uci = None, is_game_over = None, result = None, turn = None):
		self.node_id = node_id # unique number ID for each node in tree
		self.simulation_steps = 0 # for wins in simulation, we add number of moves
		self.fen = fen
		self.is_game_over = is_game_over # when we generate all moves for parent node, we already have board and information for end_game, so we just save this for later and use it in playouts
		self.result = result # board.result *, 1-0, 0-1, 1/2-1/2
		if move_uci == None:
			move_uci = 'root'
		self.move_uci = move_uci
		if (move_uci == 'root') or (turn == None):
			board = chess.Board(fen)
			turn = board.turn
			self.node_id = 0
		self.turn = turn # True(black move) - white to play next move, False(white move) - black to play next move
		if self.is_game_over:
			self.end_game_value = get_win_value(self.turn, self.result, self.turn)
		else:
			self.end_game_value = None
		self.wins = 0
		self.playouts = 0
		self.num_back_propagate_reason_end_game = 0
		self.num_back_propagate_reason_time = 0
		self.num_back_propagate_reason_steps = 0
		self.played_node = None # True - actually played move
		self.children = []
		self.parent = None
		self.branch_type = None # branch type in tree - decisive branch that leads us to a win or a loss
		self.tree_deep_level = 0
		if _Debug:
			if self.turn:
				self.player = 'black'
			else:
				self.player = 'white'

	def __repr__(self): # Object representation
		board = chess.Board(self.fen)
		if _Debug:
			sRet = '{}. {} ({} / {}){} \n{}\n'.format(self.node_id, self.move_uci, self.wins, self.playouts, self.player, str(board))
		else:
			sRet = '{}. {} ({} / {}) \n{}\n'.format(self.node_id, self.move_uci, self.wins, self.playouts, str(board))
		sRet = sRet +'A B C D E F G H\n'
		if (len(self.children) == 0):
			sRet = sRet + ' leaf'
		else:
			sRet = sRet + ' ('
			for child in self.children:
				if ((child.wins > 0) or (child.playouts > 0)):
					if _Debug:
						sRet = sRet + ' '+'{}. {} ({} / {}) {} - sim. steps {}  ::'.format(child.node_id, child.move_uci, child.wins, child.playouts, child.player, child.simulation_steps)
					else:
						sRet = sRet + ' '+'{}. {} ({} / {}) - sim. steps {}  ::'.format(child.node_id, child.move_uci, child.wins, child.playouts, child.simulation_steps)
				else:
					if _Debug:
						sRet = sRet + ' '+'{}. {} {} - sim. steps {}  ::'.format(child.node_id, child.move_uci, self.player, child.simulation_steps)
					else:
						sRet = sRet + ' '+'{}. {} - sim. steps {}  ::'.format(child.node_id, child.move_uci, child.simulation_steps)
			sRet = sRet + ')'
		return sRet
	def expand(self, node_id):
		i_gen_childs = 0
		decisive_win_node = None	# if we have a winning move
		if (len(self.children) == 0):
			board = chess.Board(self.fen)
			# if _Debug:
			# 	print('Expanding this board')
			# 	print(board)
			# 	print('A B C D E F G H\n')
			# 	print(board.legal_moves)					
			for move in board.legal_moves:
				node_id += 1
				board.push(move)
				child = mctree(board.fen(), node_id, move.uci(), board.is_game_over(claim_draw = _CLAIM_DRAW), board.result(claim_draw = _CLAIM_DRAW), not self.turn)
				self.children.append(child)
				self.children[len(self.children)-1].parent = self # link added child to parent
				child.tree_deep_level = child.parent.tree_deep_level + 1
				if (_OPT_TREE_MATE):
					if child.end_game_value != None:
						if 1 == child.end_game_value:
							decisive_win_node = child
							backpropagate_win(child)
						elif 0 == child.end_game_value:
							backpropagate_lose(child)
				# if child.end_game_value == 1:
				# 	if _DebugSpecial:
				# 		print(board)
				# 		print('A B C D E F G H\n')
				# 	decisive_win_node = child
				board.pop()
				i_gen_childs += 1
		return node_id, decisive_win_node

def display_tree(node, level=0):
	color = None
	if node.turn == False:
		color = 'W' # uci from white
	else:
		color = 'B' # uci from black
	value = ''
	if _OPT_SIMULATION:
		if (node.end_game_value != None):
			value = 'end_game_value='+str(node.end_game_value)
	if (node.playouts > 0):
		print("  "*level,'{}. {} {} ({} / {}) {}'.format(node.node_id, node.move_uci, color, node.wins, node.playouts, value))
	else:
		print("  "*level, '{}. {} {} {}'.format(node.node_id, node.move_uci, color, value))
	level += 1
	for child in node.children:
		display_tree(child, level)  # recursive call

def print_played_moves(root_node, board, time_start):
	b_end = False
	s_moves = ''
	i_moves = 0
	node_parent = root_node
	while not b_end:
		n_move = None
		for child in node_parent.children:
			if (child.played_node == True):
				n_move = child
		if (n_move != None):
			node_parent = n_move
			if n_move.turn == False: # white move
				i_moves += 1
				s_moves = s_moves + '\n {}. {} '.format(i_moves, n_move.move_uci)
			else: # black move
				s_moves = s_moves + ' {} '.format(n_move.move_uci)
		else:
			b_end = True
	print(s_moves)
	i_dif =  time.time() - time_start
	i_min = int(i_dif / 60)
	i_sec = int(i_dif - (60 * i_min))
	print('{}:{} (min:sec) elapsed from game start '.format(i_min, i_sec))
	print(board)
	print('A B C D E F G H\n')


def print_played_moves_tmp(root_node):
	b_end = False
	s_moves = ''
	i_moves = 0
	node_parent = root_node
	while not b_end:
		n_move = None
		for child in node_parent.children:
			if (child.played_node == True):
				n_move = child
				break
		if (n_move != None):
			node_parent = n_move
			i_moves += 1
			if n_move.turn == False: # white move
				s_moves = s_moves + '\n {}. {} '.format(i_moves, n_move.move_uci)
			else: # black move
				if s_moves == '':
					s_moves = s_moves + '\n {}.      {} '.format(i_moves, n_move.move_uci)
				else:	
					s_moves = s_moves + ' {} '.format(n_move.move_uci)
		else:
			b_end = True
	print(s_moves)

def print_children(node_parent, print_level):
	if print_level:
		s_moves = ''
		n_value = 0
		s_uci = ''
		print(' For parent: {}. {} {} / {};  v= {}\n'.format(node_parent.node_id, node_parent.move_uci, node_parent.wins, node_parent.playouts, get_node_value(node_parent)))
		for child in node_parent.children:
			tmp_value = get_node_value(child)
			if tmp_value > n_value:
				n_value = tmp_value
				s_uci = child.move_uci
			if child.playouts>0:
				s_moves = s_moves + '{}. {} {} / {}; v= {}\n'.format(child.node_id, child.move_uci, child.wins, child.playouts, get_node_value(child))
			for child2 in child.children:
				if child2.playouts>0:
					s_moves = s_moves + '       {}. {} {} / {}; v= {}\n'.format(child2.node_id, child2.move_uci, child2.wins, child2.playouts, get_node_value(child2))
				for child3 in child2.children:
					if child3.playouts>0:
						s_moves = s_moves + '               {}. {} {} / {}; v= {}\n'.format(child3.node_id, child3.move_uci, child3.wins, child3.playouts, get_node_value(child3))
		print(s_moves)
		print('Current best:', s_uci, n_value)

def backPropagate(win, node_L, node_M, propagate_reason, simulation_steps): # from bottom node node_L up to grand...parent node_M
	bEnd = False
	# node_L.simulation_steps = simulation_steps #  from each node we have only one simulation, number of steps to end the game is important
	tmp_node = node_L
	while not bEnd:
		# if _Debug:
		# 	if ((tmp_node.move_uci == 'a7h7') or (tmp_node.move_uci == 'a7g7')) and (win == 1):
		# 		global _DEBUG_SIM
		# 		global _DEBUG_SIM2
		# 		global _DEBUG_SIM3
		# 		_DEBUG_SIM = True # print debuging simulation function (start bord position, end bord position)
		# 		_DEBUG_SIM2 = True# print deep debuging  simulation function (each actual move in simulation)
		# 		_DEBUG_SIM3 = True # print deep debuging  simulation function  (detailed testing moves in simulation before we find next actual move)
		tmp_node.playouts +=1
		tmp_node.wins += win
		if 1 == win: # only when we win we are interested in steps
			tmp_node.simulation_steps += simulation_steps
		simulation_steps += 1 # each level up the tree, we add one move
		if (_END_GAME == propagate_reason):
			tmp_node.num_back_propagate_reason_end_game += 1
		if (_TIME == propagate_reason):
			tmp_node.num_back_propagate_reason_time += 1
		if (_STEPS == propagate_reason):
			tmp_node.num_back_propagate_reason_steps += 1
		# if (tmp_node.node_id == node_M.node_id):
		if ("root" == tmp_node.move_uci): # propagate to root - original is propagate to node_M
			bEnd = True
		else:
			tmp_node = tmp_node.parent
			if (win != 0.5): # draw
				if (1 == win): # win for child is loss for parent
					win = 0
				else:
					win = 1
	print_children(node_M, _DebugTree)


def debug_print_board(board, message, steps, print_level):
	if print_level:
		if board.turn:
			player = 'BLACK played last move'
		else:
			player = 'WHITE played last move'
		print("                      ", message, board.turn, "Steps:", steps, player)
		print(board)
		print('A B C D E F G H\n')

# TODO - move to ChessHelper library
def get_king_distance_from_edges(board, color):
	king_square = board.king(color)
	king_file = chess.square_file(king_square) # 0 is a file
	king_rank = chess.square_rank(king_square) # 0 is first rank
	if king_file > 3:
		king_file = 7 - king_file
	if king_rank > 3:
		king_rank = 7 - king_rank
	return king_file, king_rank # file a-h, rank 1-8

# simulation/playout chose random  moves for each side localy; don't build nodes in tree
def simulation_gen(node_C, deep_level):
	# start_time = time.time()
	# if _Debug:
	# 	if (node_C.move_uci == 'a7a6') or (node_C.move_uci == 'a7a4'):
	# 		print('debug')	
	be.board_evaluation_type = 1 # TODO place this in main code
	reason_for_simulation_stop = None
	win = 0
	steps = 0
	stack = 0 # number of moves on board stack
	b_end = False
	board = chess.Board(node_C.fen)
	debug_print_board(board,"sim start position", steps, _DEBUG_SIM)
	winning_move = None
	while not b_end:
		steps += 1
		if board.is_game_over(claim_draw = _CLAIM_DRAW):
			reason_for_simulation_stop = _END_GAME
			win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
			b_end = True
		if not b_end: # push next move
			if (_OPT_SIMULATION == True):
				king_distance = ch.get_kings_distance_euclidean(board)
				PS_king_square = board.king(board.turn)
				# OP_king_square = board.king(not board.turn)
				# PS_king_mobility = ch.get_king_mobility(board, board.turn)
				PS_legal_moves = list(board.legal_moves)
				if 1 == board.legal_moves.count(): # only one move - just make the move
					board.push(PS_legal_moves[0])
					debug_print_board(board,"only move", steps, _DEBUG_SIM2)
					stack += 1
				else:                                                          # PS_  playing side (side to decide next move),  OT_  other side
					PS_king_square = board.king(board.turn)
					OP_king_square = board.king(not board.turn)
					be.piece_evaluation_type = 0 # (basic pieces value)
					PS_pieces_value = be.get_pieces_value(board, board.turn)
					OP_pieces_value = be.get_pieces_value(board, not board.turn)
					PS_pieces_num = len(be.get_pieces(board, board.turn)) # number of pieces for PS
					OP_pieces_num = len(be.get_pieces(board, not board.turn)) # number of pieces for OP
					PS_king_from_edge_num = ch.get_king_distance_from_edge(board, board.turn)
					# OP_king_from_edge_num = ch.get_king_distance_from_edge(board, not board.turn)
					# loop_PS_king_from_edge_num = PS_king_from_edge_num #
					PS_king_from_edge_file_num, PS_king_from_edge_rank_num = get_king_distance_from_edges(board, board.turn)
					# OP_king_from_edge_file_num, OP_king_from_edge_rank_num = get_king_distance_from_edges(board, not board.turn)
					loop_PS_king_from_edge_file_num = PS_king_from_edge_file_num #
					loop_PS_king_from_edge_rank_num = PS_king_from_edge_rank_num #

					PS_king_mobility_num = ch.get_king_mobility(board, board.turn)
					OP_king_mobility_num = ch.get_king_mobility(board, not board.turn)
					loop_PS_king_mobility_num = PS_king_mobility_num
					#loop_OP_king_mobility_num = OP_king_mobility_num
					loop_OP_king_mobility_num = 10 
					# OP_board_value = be.get_board_value(board, not board.turn)
					PS_b_run = True
					PS_i = 0
					PS_acceptable_moves = [] # acceptable moves
					PS_king_moves = []
					PS_mobility_moves = []
					PS_king_from_edge = []
					PS_capture_moves = [] # moves which capture opponent's piece
					# simulate PS moves
					winning_move = None
					queen_promotion = None
					b_can_OP_king_capture = False
					if _OPT_DETECT_CAPTURING_PIECE:
						if PS_pieces_num > 1: # we must have more than a king, to be afraid of capturing a piece
							b_can_OP_king_capture, capture_sqare = can_OP_king_capture_any_PS_piece(board, board.turn, PS_king_square, OP_king_square)
					# if b_can_OP_king_capture:
					# 	debug_print_board(board,"piece can be captured", steps, _DEBUG_SIM3)		
					while PS_b_run and (PS_i < (len(PS_legal_moves))):
						PS_move = PS_legal_moves[PS_i]
						PS_b_bad_move = False
						board.push(PS_move)
						if _DEBUG_SIM2:
							debug_print_board(board,"PS_move sim", steps, _DEBUG_SIM3)
						if board.is_game_over(claim_draw = _CLAIM_DRAW):
							# is it a win for PS - we can just stop
							PS_win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), board.turn)
							if PS_win == 1:
								PS_b_run = False
								winning_move = PS_move
							else: # avoid draw - stalemate
								PS_b_bad_move = True
						if _OPT_DETECT_CAPTURING_PIECE and not PS_b_bad_move:
							if PS_pieces_num > 1: # we must have more than a king, to be afraid of capturing a piece
								tmp_piece_square = PS_move.to_square
								if tmp_piece_square != PS_king_square:
									if not is_save_from_king_capture(tmp_piece_square, PS_king_square, OP_king_square):
										PS_b_bad_move = True
						if	not PS_b_bad_move:
							if PS_move.promotion == 5:
								# PS_b_run = False we dont't stop
								# stack += 1
								queen_promotion = PS_move
							else: # for PS move we play all opponent's moves to check if it's not or bad move
								max_OP_from_edge = 0
								
								# simulate OP moves
								# OP_legal_moves = list(board.legal_moves)
								# OP_b_run = True
								# OP_i = 0
								# while OP_b_run and (OP_i < (len(OP_legal_moves))):
								# 	OP_move = OP_legal_moves[OP_i]
								# 	board.push(OP_move)
								# 	# debug_print_board(board,"OP_move sim")
								# 	if board.is_game_over(claim_draw = _CLAIM_DRAW):
								# 		win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
								# 		if win == 1:
								# 			PS_b_bad_move = True # win for opponent is a bad move
								# 			OP_b_run = False # we can skip testing other OP moves, we already see that is a bad move for PS
								# 	else:
								# 		tmp_PS_pieces_value = be.get_pieces_value(board, board.turn)
								# 		if tmp_PS_pieces_value < PS_pieces_value:
								# 			PS_b_bad_move = True # opponent captures PS piece - bad move
								# 			OP_b_run = False # we can skip testing other OP moves, we already see that is bad move for PS
								# 	if PS_pieces_value > OP_pieces_value: # only when we have advantage we are interested in king edge distance
								# 		tmp_OP_king_from_edge = ch.get_king_distance_from_edge(board, not board.turn)
								# 		if tmp_OP_king_from_edge > max_OP_from_edge:
								# 			max_OP_from_edge = tmp_OP_king_from_edge
								# 	board.pop()
								# 	OP_i += 1
								if not PS_b_bad_move:
									if _DEBUG_SIM2:
										debug_print_board(board,"PS_move sim", steps, _DEBUG_SIM3)
									PS_acceptable_moves.append(PS_move)
									tmp_OP_pieces_num = len(be.get_pieces(board, board.turn))
									if tmp_OP_pieces_num < OP_pieces_num: # we capture oppenent's piece
										PS_capture_moves.append(PS_move)
									# if _OPT_KING_EDGE:	 # TODO 1-2 pawns - close to pawns
									# 	tmp_PS_king_from_edge_num = ch.get_king_distance_from_edge(board, not board.turn)
									# 	if PS_pieces_value < OP_pieces_value: # PS have disadvantage
									# 		if tmp_PS_king_from_edge_num > loop_PS_king_from_edge_num:
									# 			PS_king_from_edge = [PS_move] # if we have better move inside the loop, we initialize array moves
									# 			loop_PS_king_from_edge_num = tmp_PS_king_from_edge_num
									# 		elif tmp_PS_king_from_edge_num == loop_PS_king_from_edge_num:
									# 			PS_king_from_edge.append(PS_move) # add move to array
									# 	else: # PS advantage - try to push king to the edge;
									# 		if max_OP_from_edge < OP_king_from_edge_num: # with this move we can lower opponent's distance to the edge
									# 			PS_king_from_edge.append(PS_move) # add move to array
									if _OPT_KING_EDGE:	 # TODO 1-2 pawns - close to pawns
										if PS_pieces_value < OP_pieces_value: # PS have disadvantage
											tmp_PS_king_from_edge_file_num, tmp_PS_king_from_edge_rank_num = get_king_distance_from_edges(board, not board.turn)
											if (tmp_PS_king_from_edge_file_num + tmp_PS_king_from_edge_rank_num) > (loop_PS_king_from_edge_file_num + loop_PS_king_from_edge_rank_num):
												PS_king_from_edge = [PS_move] # if we have better move inside the loop, we initialize array moves
												loop_PS_king_from_edge_rank_num = tmp_PS_king_from_edge_rank_num
												loop_PS_king_from_edge_file_num = tmp_PS_king_from_edge_file_num
											elif  (tmp_PS_king_from_edge_file_num + tmp_PS_king_from_edge_rank_num) == (loop_PS_king_from_edge_file_num + loop_PS_king_from_edge_rank_num):
												PS_king_from_edge.append(PS_move) # add move to array
										# for winning side we should play all the possible moves, to  calculate proper valued edge moves - that is expensive - we are relying on king mobility evaluation
										# else: # PS advantage - try to push king to the edge;
										# 	tmp_OP_king_from_edge_file_num, tmp_OP_king_from_edge_rank_num = get_king_distance_from_edges(board, board.turn)
										# 	if max_OP_from_edge < OP_king_from_edge_num: # with this move we can lower opponent's distance to edge
										# 		PS_king_from_edge.append(PS_move) # add move to array
									if _OPT_MOBILITY:
										if PS_pieces_value < OP_pieces_value: # PS has disadvantage - we are interested in our mobility
											if not (_OPT_KING_EDGE and (PS_pieces_num == 1)): # if we have only a king - we prefer using edge - run to the center
												tmp_PS_king_mobility_num = ch.get_king_mobility(board, not board.turn)
												if tmp_PS_king_mobility_num > loop_PS_king_mobility_num:	 # maximize PS king mobility
													PS_mobility_moves = [PS_move]
													loop_PS_king_mobility_num = tmp_PS_king_mobility_num
												elif tmp_PS_king_mobility_num == loop_PS_king_mobility_num:
													PS_mobility_moves.append(PS_move)
										else:  # PS has advantage - we are interested in opponent's mobility to lower
											PS_to_square = PS_move.to_square
											to_file = chess.square_file(PS_to_square)
											to_rank = chess.square_rank(PS_to_square)
											PS_from_square = PS_move.from_square
											from_file = chess.square_file(PS_from_square)
											from_rank = chess.square_rank(PS_from_square)
											PS_piece_type = board.piece_type_at(PS_to_square)
											b_rook_queen = (chess.ROOK == PS_piece_type) or (chess.QUEEN == PS_piece_type)
											b_avoid_move = False
											if b_rook_queen: # for rook or queen avoid edges - not good moves for lowering mobility - move to edge if mate is covered higher in code
												if to_file == from_file:
													b_avoid_move = (to_rank==0) or (to_rank==7)
												elif to_rank == from_rank:
													b_avoid_move = (to_file==0) or (to_file==7)
												# we don't have detection of capturing piece in next move, we avoid a move close to the king
												OP_king_square = board.king(board.turn)
												PS_king_square = board.king(not board.turn)
												distance_to_OP_king = chess.square_distance(PS_to_square, OP_king_square) # distance between new PS piece and oposite king
												distance_to_PS_king = chess.square_distance(PS_to_square, PS_king_square) # distance between new PS piece and PS king
												if distance_to_OP_king <= 1 and distance_to_PS_king > 1: # avoid moving next to opposite king if our king is not near guarding our piece
													b_avoid_move = True
											if _OPT_DISTANCE_BETWEEN_KINGS: 
												if (chess.KING == PS_piece_type): # avoid mobility moves for king - we cover this in _OPT_DISTANCE_BETWEEN_KINGS
													b_avoid_move = True
											# if (chess.KING == PS_piece_type): # avoid mobility moves if distance increases
											# 	tmp_king_distance = ch.get_kings_distance_euclidean(board)
											# 	if (tmp_king_distance > king_distance):
											# 		b_avoid_move = True
											if not b_avoid_move:
												tmp_OP_king_mobility_num = max(ch.get_king_mobility(board, board.turn), 2) # 2 is also excellent
												if (tmp_OP_king_mobility_num < max(loop_OP_king_mobility_num, 2)):	 # minimizing opponent king mobility
													PS_mobility_moves = [PS_move]
													loop_OP_king_mobility_num = max(tmp_OP_king_mobility_num, 2)
												elif max(tmp_OP_king_mobility_num,2) == max(loop_OP_king_mobility_num,2):
													PS_mobility_moves.append(PS_move)
									if _OPT_DISTANCE_BETWEEN_KINGS:
										if PS_king_square != board.king(not board.turn):
											tmp_king_distance = ch.get_kings_distance_euclidean(board)
											if PS_pieces_value < OP_pieces_value: # PS has disadvantage
												if not (_OPT_KING_EDGE and (PS_pieces_num == 1)): # if we have only king - we prefer using edge - run to the center
													if (tmp_king_distance > king_distance): # check second condition !!!
														PS_king_moves.append(PS_move)
											else:
												if (tmp_king_distance < king_distance): # check second condition !!!
													tmp_OP_king_mobility_num = max(ch.get_king_mobility(board, board.turn), 2) # 2 is also excellent
													if  max(tmp_OP_king_mobility_num,2) == max(loop_OP_king_mobility_num,2):	# with king move we can not ruin mobility
														if (tmp_king_distance > 2) and (PS_pieces_value>=1005): # avoid opposition if you have stronger pieces than pawns
															PS_king_moves.append(PS_move)
												# else:
												# 	tmp_OP_king_mobility_num = max(ch.get_king_mobility(board, board.turn), 2) # 2 is also excellent
												# 	if  max(tmp_OP_king_mobility_num,2) == max(loop_OP_king_mobility_num,2):	# with king move we can not ruin mobility
												# 		PS_king_moves.append(PS_move)
						board.pop() # pop PS move
						PS_i += 1
					# we must now decide OP's actual move
					debug_print_board(board,"PS_move sim", steps, _DEBUG_SIM2)
					if winning_move != None:
						board.push(winning_move)
						debug_print_board(board,"winning move", steps, _DEBUG_SIM2)
						stack += 1
					elif queen_promotion != None:
						board.push(queen_promotion)
						debug_print_board(board,"queen_promotion move", steps, _DEBUG_SIM2)
						stack += 1
					else:
						debug_print_board(board,"decide actual simulation move", steps, _DEBUG_SIM2)
						# TODO - make random choices if we have more than one possible move
						b_mobility_move = len(PS_mobility_moves) > 0
						b_king_move = len(PS_king_moves) > 0
						b_king_edge = len(PS_king_from_edge) > 0
						if b_can_OP_king_capture and b_mobility_move: 
							# TODO - check if all mobility moves can save piece to be captured - otherwise perform additional filtering on available mobility moves for capture_sqare (move from)
							b_king_move = False
							b_king_edge = False
							#b_mobility_move = len(PS_mobility_moves) > 0
						if b_mobility_move and b_king_move and b_king_edge: 
							r = random.randrange(0,3)
							if r == 0:
								b_king_move = False	
								b_king_edge = False										
							elif r == 1:
								b_mobility_move = False
								b_king_edge = False										
							else:
								b_mobility_move = False
								b_king_move = False	
						else:
							if b_mobility_move and b_king_move: 
								r = random.randrange(0,2)
								if r == 0:
									b_mobility_move = False
								else:
									b_king_move = False
							elif b_mobility_move and b_king_edge: 
								r = random.randrange(0,2)
								if r == 0:
									b_mobility_move = False
								else:
									b_king_edge = False
							elif b_king_move and b_king_edge: 
								r = random.randrange(0,2)
								if r == 0:
									b_king_move = False
								else:
									b_king_edge = False
						if b_mobility_move: # do mobility move
							# if PS_pieces_value < OP_pieces_value: # PS have disadvantage
							if (len(PS_mobility_moves) > 1) and (len(PS_king_from_edge) > 0): # if we have more mobility moves than one, and we can move king from edge, we use this move
								r = random.randrange(0, len(PS_king_from_edge))
								board.push(PS_king_from_edge[r])
								debug_print_board(board,"actual move - king runs to center", steps, _DEBUG_SIM2)
								stack += 1
							else:
								r = random.randrange(0, len(PS_mobility_moves))
								board.push(PS_mobility_moves[r])
								debug_print_board(board,"actual mobility move", steps, _DEBUG_SIM2)
								stack += 1
							# else: # PS has advantage
							# 	r = random.randrange(0, len(PS_mobility_moves))
							# 	board.push(PS_mobility_moves[r])
							# 	debug_print_board(board,"actual mobility move")
							# 	stack += 1
						elif b_king_move: # do king distance move
							r = random.randrange(0, len(PS_king_moves))
							board.push(PS_king_moves[r])
							debug_print_board(board,"actual king distance move", steps, _DEBUG_SIM2)
							stack += 1
						elif b_king_edge: # do king edge move
							r = random.randrange(0, len(PS_king_from_edge))
							board.push(PS_king_from_edge[r])
							debug_print_board(board,"actual king edge move", steps, _DEBUG_SIM2)
							stack += 1
						elif len(PS_acceptable_moves) > 0: # do acceptable move
							r = random.randrange(0, len(PS_acceptable_moves))
							board.push(PS_acceptable_moves[r])
							debug_print_board(board,"actual acceptable move, steps", steps, _DEBUG_SIM2)
							stack += 1
						else: # :( random move
							r = random.randrange(0, len(PS_legal_moves))
							board.push(PS_legal_moves[r])
							debug_print_board(board,"random move", steps, _DEBUG_SIM2)
							stack += 1
			else: # just a random move
				n_leg_m = board.legal_moves.count()
				if (0==n_leg_m):
					b_end = True
					debug_print_board(board,"no moves ??", steps, _DEBUG_SIM2)
				else:
					if n_leg_m==1:
						legal_moves = list(board.legal_moves)
						board.push(legal_moves[0])
						stack += 1
						debug_print_board(board,"one move", steps, _DEBUG_SIM2)
					else:
						legal_moves = list(board.legal_moves)
						r = random.randrange(0, n_leg_m)
						board.push(legal_moves[r])
						debug_print_board(board,"random moves ", steps, _DEBUG_SIM2)
						stack += 1
		if max_simulation_moves != 0: 
			if stack > max_simulation_moves:
				reason_for_simulation_stop = _STEPS
				win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
				b_end = True
	debug_print_board(board,"end simulation ", steps, _DEBUG_SIM)
	return win, stack, reason_for_simulation_stop

def is_save_from_king_capture(PS_rook_square, PS_king_square, OP_king_square):
	b_safe = True
	pom = chess.square_distance(PS_rook_square, OP_king_square)
	if pom == 1:
		pom = chess.square_distance(PS_rook_square, PS_king_square)
		if pom > 1:
			b_safe = False
	return b_safe

# only works if only one piece of this type is on the board
def get_piece_square(board, piece_typ, trn):
	piece_list = list(board.pieces(piece_typ, trn))
	return piece_list[0] 

# works only when OP has only a king - check for undefended piece
# TODO - test this code
def can_OP_king_capture_any_PS_piece(board, trn, PS_king_square, OP_king_square):
	b_CanCapture = False
	capure_sqare = None # in which square is a piece to be captured by OP king
	if PS_king_square == None: # if parameter is None, we find PS king's square
		PS_king_square = board.king(board.turn)
	if OP_king_square == None: # if parameter is None, we find PS king's square
		OP_king_square = board.king(not board.turn)	
	if _game_type == KRk:
		PS_piece_sqare = get_piece_square(board, chess.ROOK, trn)
		b_CanCapture = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
		if b_CanCapture:
			capure_sqare = PS_piece_sqare
	elif _game_type == KQk:
		PS_piece_sqare = get_piece_square(board, chess.QUEEN, trn)
		b_CanCapture = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
		if b_CanCapture:
			capure_sqare = PS_piece_sqare
	else:	  # if we don't have known end game, we check all the pieces
		PS_pieces_sqares = list(board.pieces(chess.QUEEN, trn))
		for PS_piece_sqare in PS_pieces_sqares:
			b_CanCapture  = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
			if b_CanCapture: # first pice OP king can capture
				capure_sqare = PS_piece_sqare
				break
		if not b_CanCapture: # check another piece
			PS_pieces_sqares = list(board.pieces(chess.ROOK, trn))
			for PS_piece_sqare in PS_pieces_sqares:
				b_CanCapture  = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
				if b_CanCapture: # first pice OP king can capture
					capure_sqare = PS_piece_sqare
					break
		if not b_CanCapture: # check another piece
			PS_pieces_sqares = list(board.pieces(chess.BISHOP, trn))
			for PS_piece_sqare in PS_pieces_sqares:
				b_CanCapture  = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
				if b_CanCapture: # first pice OP king can capture
					capure_sqare = PS_piece_sqare
					break
		if not b_CanCapture: # check another piece
			PS_pieces_sqares = list(board.pieces(chess.KNIGHT, trn))
			for PS_piece_sqare in PS_pieces_sqares:
				b_CanCapture  = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
				if b_CanCapture: # first pice OP king can capture
					capure_sqare = PS_piece_sqare
					break
		if not b_CanCapture: # check another piece
			PS_pieces_sqares = list(board.pieces(chess.PAWN, trn))
			for PS_piece_sqare in PS_pieces_sqares:
				b_CanCapture  = not is_save_from_king_capture(PS_piece_sqare, PS_king_square, OP_king_square)
				if b_CanCapture: # first pice OP king can capture
					capure_sqare = PS_piece_sqare
					break
	return b_CanCapture, capure_sqare

# check if kings are separated by guarding piece (for example rook)
# return True - piece is between both kings, second parameter is distance by rank or file from eperating_piece to OP_king - this helps to find closest move to restrict OP king's movments, last return is type separation by rank/file
def are_kings_seperated(seperating_piece_square, PS_king_square, OP_king_square):
	if chess.square_file(PS_king_square) < chess.square_file(seperating_piece_square):
		if chess.square_file(seperating_piece_square) < chess.square_file(OP_king_square):
			return True, (chess.square_file(OP_king_square) - chess.square_file(seperating_piece_square)), _SEPERATED_BY_FILE
	elif chess.square_file(PS_king_square) > chess.square_file(seperating_piece_square):
		if chess.square_file(seperating_piece_square) > chess.square_file(OP_king_square):
			return True, (chess.square_file(seperating_piece_square) - chess.square_file(OP_king_square)), _SEPERATED_BY_FILE
	if chess.square_rank(PS_king_square) < chess.square_rank(seperating_piece_square):
		if chess.square_rank(seperating_piece_square) < chess.square_rank(OP_king_square):
			return True, (chess.square_rank(OP_king_square) - chess.square_rank(seperating_piece_square)), _SEPERATED_BY_RANK
	elif chess.square_rank(PS_king_square) > chess.square_rank(seperating_piece_square):
		if (chess.square_rank(seperating_piece_square) > chess.square_rank(OP_king_square)):
			return True, (chess.square_rank(seperating_piece_square) - chess.square_rank(OP_king_square)),  _SEPERATED_BY_RANK
	return 	False, 8, None # 8 is distance wider than board width


# QUEEN 
def simulation_KQk(node_C, deep_level):	
	be.board_evaluation_type = 1 
	reason_for_simulation_stop = None
	win = 0
	steps = 0
	stack = 0 # number of moves on board stack
	b_end = False
	board = chess.Board(node_C.fen)
	debug_print_board(board,"sim start position", steps, _DEBUG_SIM)
	# we can afford to get pieces value outside of the loop - there is only one extra piece, and if it is removed from the board it's the end of the simulated game
	PS_pieces_value = be.get_pieces_value(board, board.turn)
	OP_pieces_value = be.get_pieces_value(board, not board.turn)
	b_PS_stronger = PS_pieces_value > OP_pieces_value
	winning_move = None
	if _OPT_MOBILITY:
		PS_king_square = board.king(board.turn)
		OP_king_square = board.king(not board.turn)                  # OP_  other side 
		if b_PS_stronger:
			PS_queen_square = get_piece_square(board, chess.QUEEN, board.turn)
		else:
			PS_queen_square = get_piece_square(board, chess.QUEEN, not board.turn)
		# b_loop_seperated_kings, loop_distance = are_kings_seperated(PS_queen_square, PS_king_square, OP_king_square)
	sepereted_by = None # we set this when we first manage to seperate kings with queen
	while not b_end:
		steps += 1
		debug_print_board(board,"sim position", steps, _DEBUG_SIM3)
		if board.is_game_over(claim_draw = _CLAIM_DRAW):
			reason_for_simulation_stop = _END_GAME
			win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
			b_end = True
		else: # find and push next move
			PS_legal_moves = list(board.legal_moves)
			PS_king_square = board.king(board.turn)
			OP_king_square = board.king(not board.turn)
			if 1 == board.legal_moves.count(): # only one move - just make the move
				board.push(PS_legal_moves[0])
				debug_print_board(board,"only move", steps, _DEBUG_SIM2)
				stack += 1
			else:     # PS_  playing side (side to decide next move),    
				PS_acceptable_moves = [] # acceptable moves 
				PS_king_moves = []
				PS_mobility_moves = []		
				PS_seperate_moves = [] # moves which seperate kings		
				PS_opposition_force = [] # opposition - force move to get OP's king closer to edge
				PS_king_from_edge = [] 
				king_distance, loop_seperated_by, loop_seperated_num = get_kings_distance_euclidean_opposition(board, False)
				loop_distance_to_OP_king = king_distance
				oposition_move = None
				if b_PS_stronger: # --------------------------------------------------------------------------- STRONGER SIDE ---------------------
					# OP_king_square = board.king(not board.turn)                  # OP_  other side 
					# loop_CMDQ = arrCenterManhattanDistanceQueen[OP_king_square]
					b_get_to_queen = False
					PS_queen_square = get_piece_square(board, chess.QUEEN, board.turn)
					loop_queen_to_PS_king_distance = get_distance_euclidean(PS_queen_square, PS_king_square)
					queen_to_OP_king_distance = chess.square_distance(OP_king_square, PS_queen_square)
					loop_queen_to_OP_king_distance = 0
					OP_king_mobility_num = ch.get_king_mobility(board, not board.turn)
					if OP_king_mobility_num == 2:
						if chess.square_distance(PS_king_square, PS_queen_square)>1:
							b_get_to_queen = True
					loop_OP_king_mobility_num = OP_king_mobility_num
					c_loop_OP_king_mobility_num = loop_OP_king_mobility_num
					move_to_OP_king_distance = None # max. move if we must move queen far from OP's king
					b_OP_king_on_edge, edge_OP_king = is_square_on_edge(OP_king_square)
					b_loop_split_kings = False
					if _OPT_MOBILITY:
						if b_OP_king_on_edge: # only when OP's king is at the edge, we are interested in a lower distance to OP king
							b_loop_split_kings, loop_distance_to_OP_king, pom_seperated_by = are_kings_seperated(PS_queen_square, PS_king_square, OP_king_square) # are kings separated
							if edge_OP_king != pom_seperated_by: # if we dont have same separation (file/rank) between kings and OP edge - it's not split
								b_loop_split_kings = False
							if pom_seperated_by != None:
								sepereted_by = pom_seperated_by
								before_distance_to_OP_king = loop_distance_to_OP_king
					loop_king_distance = king_distance
					loop_mv_distance = 10	
					for PS_move in PS_legal_moves:
						board.push(PS_move)
						debug_print_board(board,"check all moves", steps, _DEBUG_SIM3)
						b_safe_move = True
						if board.is_game_over(claim_draw = _CLAIM_DRAW):
							# is it win for PS - we can just stop
							PS_win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), board.turn)
							if PS_win == 1:
								board.pop() # pop PS move
								winning_move = PS_move	
								break					
							else: # awoid draw - stalemate
								b_safe_move = False
						tmp_queen_square = get_piece_square(board, chess.QUEEN, not board.turn)
						tmp_PS_king_square = board.king(not board.turn)
						if _OPT_DETECT_CAPTURING_PIECE:
							if not is_save_from_king_capture(tmp_queen_square, tmp_PS_king_square, OP_king_square):
								b_safe_move = False
						if b_safe_move: 
							if PS_king_square != board.king(not board.turn): # we have king move
								if sepereted_by ==_SEPERATED_BY_FILE:
									xtmp_queen_file = chess.square_file(tmp_queen_square)
									xtmp_king_file = chess.square_file(tmp_PS_king_square)
									if xtmp_queen_file == xtmp_king_file:
										b_safe_move = False
								else: # rank check
									xtmp_queen_rank = chess.square_rank(tmp_queen_square)
									xtmp_king_rank = chess.square_rank(tmp_PS_king_square)
									if xtmp_queen_rank == xtmp_king_rank:
										b_safe_move = False
						if b_safe_move:
							PS_acceptable_moves.append(PS_move)
							b_tmp_split_kings = True # we use this in _OPT_MOBILITY and _OPT_DISTANCE_BETWEEN_KINGS
							tmp_king_distance, tmp_seperated_by, tmp_seperated_num = get_kings_distance_euclidean_opposition(board, True)
							if _OPT_MOBILITY: # this must run first, then _OPT_DISTANCE_BETWEEN_KINGS
								b_skip_king = False
								if _OPT_DISTANCE_BETWEEN_KINGS: # if we have this enabled, king moves are already covered 
									if PS_king_square != board.king(not board.turn):
										b_skip_king = True
								if not b_skip_king: # not a king move
									tmp_OP_king_mobility_num = ch.get_king_mobility(board, board.turn)
									if c_loop_OP_king_mobility_num == 0: # avoid draw
										if tmp_OP_king_mobility_num <= 2: # is it sufficient - or should calculate rank / file for queen on OP king position
											PS_mobility_moves = [PS_move]
									elif b_OP_king_on_edge: # OP king is on the edge
										b_tmp_split_kings, tmp_distance_to_OP_king, pom_seperated_by = are_kings_seperated(PS_move.to_square, PS_king_square, OP_king_square)
										if b_loop_split_kings: # we already split kings, and OP king at the edge - we check file / rank distance - need to lower it
											if tmp_distance_to_OP_king < loop_distance_to_OP_king:
												PS_mobility_moves = [PS_move]
												loop_distance_to_OP_king = tmp_distance_to_OP_king	 
										else: # we dont't have splitting
											if loop_distance_to_OP_king == None:
												loop_distance_to_OP_king = 10
											if b_tmp_split_kings:
												if tmp_distance_to_OP_king <= loop_distance_to_OP_king: # we need 1 move (some state already added some moves, so we just keep the last)
													PS_mobility_moves = [PS_move]
													loop_distance_to_OP_king = tmp_distance_to_OP_king	 
												# elif tmp_distance_to_OP_king == loop_distance_to_OP_king:
												# 	PS_mobility_moves.append(PS_move)
									else:
										if tmp_OP_king_mobility_num < loop_OP_king_mobility_num:	 # minimize OP king mobility
											PS_mobility_moves = [PS_move]
											loop_OP_king_mobility_num = tmp_OP_king_mobility_num
											loop_mv_distance = chess.square_distance(PS_move.from_square, PS_move.to_square)
										elif tmp_OP_king_mobility_num == loop_OP_king_mobility_num:
											# we avoid king moves to avoid jumping from one side of the king to the other
											tmp_mv_distance = chess.square_distance(PS_move.from_square, PS_move.to_square)
											if tmp_mv_distance < loop_mv_distance:
												loop_mv_distance = tmp_mv_distance
												PS_mobility_moves = [PS_move]
											elif tmp_mv_distance == loop_mv_distance:
												PS_mobility_moves.append(PS_move)
							if _OPT_DISTANCE_BETWEEN_KINGS:
								if PS_king_square != board.king(not board.turn):
									if b_loop_split_kings: # we already split kings, and OP king on edge - we check file / rank distance to lower
										b_tmp_split_kings, tmp_distance_to_OP_king, pom_seperated_by = are_kings_seperated(PS_queen_square, PS_move.to_square, OP_king_square)
										if b_tmp_split_kings: # avoid to step on split line
											# we minimize PS king distance to OP king
											tmp_king_distance, tmp_seperated_by, tmp_seperated_num = get_kings_distance_euclidean_opposition(board, False)
											if tmp_king_distance < loop_distance_to_OP_king:
												PS_seperate_moves = [PS_move]
												loop_distance_to_OP_king = tmp_king_distance
											elif tmp_king_distance == loop_distance_to_OP_king:
												PS_seperate_moves.append(PS_move)
									else: 
										# if (tmp_king_distance > 2): # going into opposition is not an option - we must force opponent to step into opposition
										if b_get_to_queen:
											tmp_queen_to_PS_king_distance = get_distance_euclidean(PS_queen_square, PS_move.to_square)
											if tmp_queen_to_PS_king_distance < loop_queen_to_PS_king_distance:
												PS_king_moves = [PS_move]
												loop_queen_to_PS_king_distance = tmp_queen_to_PS_king_distance
											elif tmp_queen_to_PS_king_distance == loop_queen_to_PS_king_distance:
												PS_king_moves.append(PS_move)
										else:
											if (tmp_king_distance < loop_king_distance): 
												PS_king_moves = [PS_move]
												loop_king_distance = tmp_king_distance
											elif (tmp_king_distance == loop_king_distance): 
												PS_king_moves.append(PS_move)										
						board.pop() # pop PS move
				else:   # ------------------------------------------------------------------------------------- WEAKER SIDE ---------------------
					loop_PS_cmd = arrCenterManhattanDistance[PS_king_square]
					loop_PS_king_mobility_num = ch.get_king_mobility(board, board.turn)
					loop_queen_square = get_piece_square(board, chess.QUEEN, not board.turn)
					b_loop_split_kings, loop_distance_to_PS_king, loop_seperated_by = are_kings_seperated(loop_queen_square, OP_king_square, PS_king_square)
					for PS_move in PS_legal_moves:
						board.push(PS_move)
						debug_print_board(board,"check all moves", steps, _DEBUG_SIM3)
						if board.is_game_over(claim_draw = _CLAIM_DRAW):
							# is it a win for PS - we can just stop
							PS_win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), board.turn)
							if PS_win == 1:
								board.pop() # pop PS move
								winning_move = PS_move	
								break					
						PS_acceptable_moves.append(PS_move)
						if _OPT_KING_EDGE:
							tmp_PS_king_square = board.king(not board.turn)
							tmp_loop_PS_cmd = arrCenterManhattanDistance[tmp_PS_king_square]
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance != 2): # avoid opposition
								if b_loop_split_kings: # if kings are separated by queen, we try to get closer to queen's line
									b_tmp_split_kings, tmp_distance_to_PS_king, tmp_seperated_by = are_kings_seperated(loop_queen_square, OP_king_square, tmp_PS_king_square) # we revert kings, because we are interested in queen's distance to our king
									if tmp_distance_to_PS_king < loop_distance_to_PS_king:
										PS_king_from_edge = [PS_move]
										loop_distance_to_PS_king = tmp_distance_to_PS_king
									elif tmp_distance_to_PS_king == loop_distance_to_PS_king:
										PS_king_from_edge.append(PS_move)
								else:
									if (tmp_loop_PS_cmd < loop_PS_cmd): # lower numbers near the center of the board 
										PS_king_from_edge = [PS_move] # if we have better move inside loop, we initialize array moves
										loop_PS_cmd = tmp_loop_PS_cmd
									elif  (tmp_loop_PS_cmd == loop_PS_cmd):
										PS_king_from_edge.append(PS_move) # add move to array
							else:
								oposition_move = PS_move
						if _OPT_MOBILITY:
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance != 2): # avoid opposition
								tmp_PS_king_mobility_num = ch.get_king_mobility(board, not board.turn)
								if tmp_PS_king_mobility_num > loop_PS_king_mobility_num:	 # maximize PS king mobility
									PS_mobility_moves = [PS_move]
									loop_PS_king_mobility_num = tmp_PS_king_mobility_num
								elif tmp_PS_king_mobility_num == loop_PS_king_mobility_num:
									PS_mobility_moves.append(PS_move)	
						if _OPT_DISTANCE_BETWEEN_KINGS:
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance > king_distance): 
								PS_king_moves.append(PS_move)
						board.pop() # pop PS move
				# we must now decide OP actual move
				debug_print_board(board,"PS_move to decide actual move", steps, _DEBUG_SIM2)
				if winning_move != None:
					board.push(winning_move)
					debug_print_board(board,"winning move", steps, _DEBUG_SIM2)
					stack += 1
				else:
					debug_print_board(board,"decide actual simulation move", steps, _DEBUG_SIM2)
					# TODO - make random choices if we have more than one possible choice to move
					b_mobility_move = len(PS_mobility_moves) > 0
					b_king_move = len(PS_king_moves) > 0
					b_king_edge = len(PS_king_from_edge) > 0 
					b_opposition_force = len(PS_opposition_force) > 0
					b_seperate_move = len(PS_seperate_moves) > 0    # TODO we have separation and only PS_seperate_moves, then we must run from the king !!!
					
					if b_PS_stronger:
						if b_OP_king_on_edge and b_mobility_move: # we first restrict moving king from edge
							if b_loop_split_kings: 
								if loop_distance_to_OP_king == 1:
									b_mobility_move = False # 
								else:
									b_king_move = False # 
							else:
								b_king_move = False # 
						elif b_get_to_queen:
							b_mobility_move = False
						else:
							if b_mobility_move and b_king_move:
								if queen_to_OP_king_distance < 3 and king_distance > 2:
									b_mobility_move = False
								else:
									if loop_OP_king_mobility_num < OP_king_mobility_num and (OP_king_mobility_num > 2):
										b_king_move = False # if we have lower king mobility - we prefer this
									else:
										b_mobility_move = False # same or equal OP king mobility, prefer king move
							if b_seperate_move and  (not b_opposition_force) and (not b_king_edge) and (not b_king_move) and (not b_mobility_move):
								if (move_to_OP_king_distance != None):
									PS_seperate_moves = [move_to_OP_king_distance] # we must run from OP king
								elif len(PS_seperate_moves) > 1: # tempo move - we choose move closest to current position
									min_distance = 20
									node_min = None
									for mv in PS_seperate_moves:
										tmp_distance = chess.square_distance(mv.from_square, mv.to_square)
										if tmp_distance < min_distance:
											min_distance = tmp_distance
											node_min = mv
									if node_min != None:
										PS_seperate_moves =[node_min]
						if b_opposition_force: # primary move
							b_mobility_move = False
							b_king_move = False
							b_king_edge = False
							b_seperate_move = False
					else:
						if _OPT_KING_EDGE and not b_king_edge: # we are forced to take opposition
							if oposition_move != None:
								b_king_edge = True
								PS_king_from_edge = [oposition_move]
						b_opposition_force = False
						if b_king_edge: # edge is more important if we have only king
							b_mobility_move = False
							b_king_move = False
						elif b_king_move:	
							b_mobility_move = False
					if b_opposition_force:
						r = random.randrange(0, len(PS_opposition_force))
						board.push(PS_opposition_force[r])
						debug_print_board(board,"actual move - opposition force move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_seperate_move:
						r = random.randrange(0, len(PS_seperate_moves))
						board.push(PS_seperate_moves[r])
						debug_print_board(board,"actual move - sepperation/mobility move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_mobility_move: # do mobility move
						# if PS_pieces_value < OP_pieces_value: # PS have disadvantage
						if (len(PS_mobility_moves) > 1) and (len(PS_king_from_edge) > 0): # if we have more mobility moves than one, and we can move king from edge, we use this move
							r = random.randrange(0, len(PS_king_from_edge))
							board.push(PS_king_from_edge[r])
							debug_print_board(board,"actual move - king runs to center", steps, _DEBUG_SIM2)
							stack += 1
						else:
							r = random.randrange(0, len(PS_mobility_moves))
							board.push(PS_mobility_moves[r])
							debug_print_board(board,"actual mobility move", steps, _DEBUG_SIM2)
							stack += 1
					elif b_king_move: # do king distance move
						r = random.randrange(0, len(PS_king_moves))
						board.push(PS_king_moves[r])
						debug_print_board(board,"actual king distance move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_king_edge: # do king edge move
						r = random.randrange(0, len(PS_king_from_edge))
						board.push(PS_king_from_edge[r])
						debug_print_board(board,"actual king edge move", steps, _DEBUG_SIM2)
						stack += 1
					elif len(PS_acceptable_moves) > 0: # do acceptable move
						r = random.randrange(0, len(PS_acceptable_moves))
						board.push(PS_acceptable_moves[r])
						debug_print_board(board,"actual acceptable move, steps", steps, _DEBUG_SIM2)
						stack += 1
					else: # :( random move
						r = random.randrange(0, len(PS_legal_moves))
						board.push(PS_legal_moves[r])
						debug_print_board(board,"random move", steps, _DEBUG_SIM2)
						stack += 1
		b_PS_stronger = not b_PS_stronger
		if max_simulation_moves != 0: 
			if stack > max_simulation_moves:
				reason_for_simulation_stop = _STEPS
				win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
				b_end = True
	debug_print_board(board,"End simulation reason= {} ;  moves={} ".format(reason_for_simulation_stop, stack), steps, _DEBUG_SIM)
	return win, stack, reason_for_simulation_stop

def simulation_KRk(node_C, deep_level):	
	# start_time = time.time()
	# if _Debug:
	# 	if (node_C.move_uci == 'a7a6') or (node_C.move_uci == 'a7a4'):
	# 		print('debug')	
	be.board_evaluation_type = 1 
	reason_for_simulation_stop = None
	win = 0
	steps = 0
	stack = 0 # number of moves on board stack
	b_end = False
	board = chess.Board(node_C.fen)
	debug_print_board(board,"sim start position", steps, _DEBUG_SIM)
	# we can afford to get pieces values outside loop - there is only one extra piece, and if it is removed from the board it's end of the simulated game
	PS_pieces_value = be.get_pieces_value(board, board.turn)
	OP_pieces_value = be.get_pieces_value(board, not board.turn)
	b_PS_stronger = PS_pieces_value > OP_pieces_value
	winning_move = None
	if _OPT_MOBILITY:
		PS_king_square = board.king(board.turn)
		OP_king_square = board.king(not board.turn) # OP_  other side 
		if b_PS_stronger:
			PS_rook_square = get_piece_square(board, chess.ROOK, board.turn)
		else:
			PS_rook_square = get_piece_square(board, chess.ROOK, not board.turn)
		# b_loop_seperated_kings, loop_distance = are_kings_seperated(PS_rook_square, PS_king_square, OP_king_square)
	sepereted_by = None # we set this when we first manage to seperate kings with rook
	while not b_end:
		steps += 1
		debug_print_board(board,"sim position", steps, _DEBUG_SIM3)
		if board.is_game_over(claim_draw = _CLAIM_DRAW):
			reason_for_simulation_stop = _END_GAME
			win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
			b_end = True
		else: # find and push next move
			PS_legal_moves = list(board.legal_moves)
			PS_king_square = board.king(board.turn)
			OP_king_square = board.king(not board.turn)
			if 1 == board.legal_moves.count(): # only one move - just make the move
				board.push(PS_legal_moves[0])
				debug_print_board(board,"only move", steps, _DEBUG_SIM2)
				stack += 1
			else:     # PS_  playing side (side to decide next move),    
				PS_acceptable_moves = [] # acceptable moves 
				PS_king_moves = []
				PS_mobility_moves = []		
				PS_seperate_moves = [] # moves which seperate kings		
				PS_opposition_force = [] # opposition - force move to get OP king closer to edge
				PS_king_from_edge = [] 
				king_distance, loop_seperated_by, loop_seperated_num = get_kings_distance_euclidean_opposition(board, False)
				oposition_move = None
				b_can_OP_king_capture = False
				if b_PS_stronger: # --------------------------------------------------------------------------- STRONGER SIDE ---------------------
					OP_king_square = board.king(not board.turn)                  # OP_  other side 
					PS_rook_square = get_piece_square(board, chess.ROOK, board.turn)
					rook_to_OP_king_distance = chess.square_distance(OP_king_square, PS_rook_square)
					loop_rook_to_OP_king_distance = 0
					move_to_OP_king_distance = None # max. move if we must move rook far from OP king
					if _OPT_MOBILITY:
						b_loop_split_kings, loop_distance_to_OP_king, pom_seperated_by = are_kings_seperated(PS_rook_square, PS_king_square, OP_king_square) # are kings seperated
						if pom_seperated_by != None:
							sepereted_by = pom_seperated_by
						before_distance_to_OP_king = loop_distance_to_OP_king
					loop_king_distance = king_distance	
					if _OPT_DETECT_CAPTURING_PIECE:
						b_can_OP_king_capture, capture_sqare = can_OP_king_capture_any_PS_piece(board, board.turn, PS_king_square, OP_king_square)					
					if b_can_OP_king_capture:
						debug_print_board(board,"piece can be captured", steps, _DEBUG_SIM3)		
					for PS_move in PS_legal_moves:
						board.push(PS_move)
						debug_print_board(board,"check all moves", steps, _DEBUG_SIM3)
						b_safe_move = True
						if board.is_game_over(claim_draw = _CLAIM_DRAW):
							# is it a win for PS - we can just stop
							PS_win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), board.turn)
							if PS_win == 1:
								board.pop() # pop PS move
								winning_move = PS_move	
								break					
							else: # avoid draw - stalemate
								b_safe_move = False
						tmp_rook_square = get_piece_square(board, chess.ROOK, not board.turn)
						tmp_PS_king_square = board.king(not board.turn)
						if _OPT_DETECT_CAPTURING_PIECE:
							if not is_save_from_king_capture(tmp_rook_square, tmp_PS_king_square, OP_king_square):
								b_safe_move = False
						if sepereted_by != None: # if we already seperated kings, we don't allow our king to step on the same line as the rook
							if PS_king_square != board.king(not board.turn): # we have a king move
								if sepereted_by ==_SEPERATED_BY_FILE:
									xtmp_rook_file = chess.square_file(tmp_rook_square)
									xtmp_king_file = chess.square_file(tmp_PS_king_square)
									if xtmp_rook_file == xtmp_king_file:
										b_safe_move = False
								else: # rank check
									xtmp_rook_rank = chess.square_rank(tmp_rook_square)
									xtmp_king_rank = chess.square_rank(tmp_PS_king_square)
									if xtmp_rook_rank == xtmp_king_rank:
										b_safe_move = False
						if b_safe_move:
							PS_acceptable_moves.append(PS_move)
							b_tmp_split_kings = True # we use this in _OPT_MOBILITY and _OPT_DISTANCE_BETWEEN_KINGS
							tmp_king_distance, tmp_seperated_by, tmp_seperated_num = get_kings_distance_euclidean_opposition(board, True)
							if _OPT_MOBILITY: # this must run first, then _OPT_DISTANCE_BETWEEN_KINGS
								b_skip_king = False
								if _OPT_DISTANCE_BETWEEN_KINGS: # if we have this enabled, king moves are already covered 
									if PS_king_square != board.king(not board.turn):
										b_skip_king = True
								if not b_skip_king:
									b_tmp_split_kings, tmp_distance_to_OP_king, pom_seperated_by = are_kings_seperated(tmp_rook_square, tmp_PS_king_square, OP_king_square)
									if b_tmp_split_kings:
										if tmp_distance_to_OP_king < loop_distance_to_OP_king:
											PS_seperate_moves = [PS_move]
											loop_distance_to_OP_king = tmp_distance_to_OP_king
										elif tmp_distance_to_OP_king == loop_distance_to_OP_king:
											PS_seperate_moves.append(PS_move)
											if rook_to_OP_king_distance == 1: # we must run from OP king
												tmp_rook_to_OP_king_distance = chess.square_distance(OP_king_square, tmp_rook_square)
												if tmp_rook_to_OP_king_distance > loop_rook_to_OP_king_distance:
													loop_rook_to_OP_king_distance = tmp_rook_to_OP_king_distance
													move_to_OP_king_distance = PS_move

									if tmp_king_distance == 2: # check if this opposition can force to move OP king closer to edge files are colomns, ranks are rows
										if PS_king_square == board.king(not board.turn): # we moved stronger piece (not king)
											PS_to_square = PS_move.to_square
											if tmp_seperated_by ==_SEPERATED_BY_FILE:
												to_file_num = chess.square_file(PS_to_square)
												if tmp_seperated_num == to_file_num:
													PS_opposition_force = [PS_move]
											else: # _SEPERATED_BY_RANK
												to_rank_num = chess.square_rank(PS_to_square)
												if tmp_seperated_num == to_rank_num:
													PS_opposition_force = [PS_move]
							if _OPT_DISTANCE_BETWEEN_KINGS:
								if PS_king_square != board.king(not board.turn):
									if b_tmp_split_kings: # default is True, only when _OPT_MOBILITY optimization is on can set to False, if PS king move step on the line and ruin separation of the kings
										if (tmp_king_distance > 2): # going into opposition is not an option - we must force opponent to step into opposition
											if (tmp_king_distance < loop_king_distance): 
												PS_king_moves = [PS_move]
												loop_king_distance = tmp_king_distance
											elif (tmp_king_distance == loop_king_distance):
												PS_king_moves.append(PS_move)										
						board.pop() # pop PS move
				else:   # ------------------------------------------------------------------------------------- WEAKER SIDE ---------------------
					loop_PS_cmd = arrCenterManhattanDistance[PS_king_square]
					loop_PS_king_mobility_num = ch.get_king_mobility(board, board.turn)
					loop_rook_square = get_piece_square(board, chess.ROOK, not board.turn)
					b_loop_split_kings, loop_distance_to_PS_king, loop_seperated_by = are_kings_seperated(loop_rook_square, OP_king_square, PS_king_square)
					for PS_move in PS_legal_moves:
						board.push(PS_move)
						debug_print_board(board,"check all moves", steps, _DEBUG_SIM3)
						if board.is_game_over(claim_draw = _CLAIM_DRAW):
							# is it a win for PS - we can just stop
							PS_win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), board.turn)
							if PS_win == 1:
								board.pop() # pop PS move
								winning_move = PS_move	
								break					
						PS_acceptable_moves.append(PS_move)
						if _OPT_KING_EDGE:
							tmp_PS_king_square = board.king(not board.turn)
							tmp_loop_PS_cmd = arrCenterManhattanDistance[tmp_PS_king_square]
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance != 2): # avoid opposition
								if b_loop_split_kings: # if kings are seperated by rook, we try to get closer to rook line
									b_tmp_split_kings, tmp_distance_to_PS_king, tmp_seperated_by = are_kings_seperated(loop_rook_square, OP_king_square, tmp_PS_king_square) # we revert kings, because we are interested in rook distance to our king
									if tmp_distance_to_PS_king < loop_distance_to_PS_king:
										PS_king_from_edge = [PS_move]
										loop_distance_to_PS_king = tmp_distance_to_PS_king
									elif tmp_distance_to_PS_king == loop_distance_to_PS_king:
										PS_king_from_edge.append(PS_move)
								else:
									if (tmp_loop_PS_cmd < loop_PS_cmd): # lower numbers are near the center of the board 
										PS_king_from_edge = [PS_move] # if we have better move inside the loop, we initialize array moves
										loop_PS_cmd = tmp_loop_PS_cmd
									elif  (tmp_loop_PS_cmd == loop_PS_cmd):
										PS_king_from_edge.append(PS_move) # add move to array
							else:
								oposition_move = PS_move
						if _OPT_MOBILITY:
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance != 2): # avoid oposition
								tmp_PS_king_mobility_num = ch.get_king_mobility(board, not board.turn)
								if tmp_PS_king_mobility_num > loop_PS_king_mobility_num:	 # maximize PS king mobility
									PS_mobility_moves = [PS_move]
									loop_PS_king_mobility_num = tmp_PS_king_mobility_num
								elif tmp_PS_king_mobility_num == loop_PS_king_mobility_num:
									PS_mobility_moves.append(PS_move)	
						if _OPT_DISTANCE_BETWEEN_KINGS:
							tmp_king_distance = ch.get_kings_distance_euclidean(board)
							if (tmp_king_distance > king_distance): 
								PS_king_moves.append(PS_move)
						board.pop() # pop PS move
				# we must now decide OP actual move
				debug_print_board(board,"PS_move to decide actual move", steps, _DEBUG_SIM2)
				if winning_move != None:
					board.push(winning_move)
					debug_print_board(board,"winning move", steps, _DEBUG_SIM2)
					stack += 1
				else:
					debug_print_board(board,"decide actual simulation move", steps, _DEBUG_SIM2)
					# TODO - make random choices if we have more than one possible choice to move
					b_mobility_move = len(PS_mobility_moves) > 0
					b_king_move = len(PS_king_moves) > 0
					b_king_edge = len(PS_king_from_edge) > 0 
					b_opposition_force = len(PS_opposition_force) > 0
					b_seperate_move = len(PS_seperate_moves) > 0    # TODO we have separation and only PS_seperate_moves, then we must run from the king !!!
					
					if b_PS_stronger:
						if b_can_OP_king_capture and b_mobility_move: 
							# TODO - check if all mobility moves can save piece to be captured - otherwise perform additional filtering on available mobility moves for capture_sqare (move from)
							b_king_move = False
							b_king_edge = False
							#b_mobility_move = len(PS_mobility_moves) > 0						
						if b_seperate_move and  (not b_opposition_force) and (not b_king_edge) and (not b_king_move) and (not b_mobility_move):
							if (move_to_OP_king_distance != None):
								PS_seperate_moves = [move_to_OP_king_distance] # we must run drom OP king
							elif len(PS_seperate_moves) > 1: # tempo move - we chose move closest to current position
								min_distance = 20
								node_min = None
								for mv in PS_seperate_moves:
									tmp_distance = chess.square_distance(mv.from_square, mv.to_square)
									if tmp_distance < min_distance:
										min_distance = tmp_distance
										node_min = mv
								if node_min != None:
									PS_seperate_moves =[node_min]
						if b_opposition_force: # primary move
							b_mobility_move = False
							b_king_move = False
							b_king_edge = False
							b_seperate_move = False
						else:
							if b_king_move and (before_distance_to_OP_king == loop_distance_to_OP_king): # loop distance to king did not change, so we chose king move
								b_mobility_move = False
								b_seperate_move = False
								b_king_edge = False
							elif loop_distance_to_OP_king < before_distance_to_OP_king: # we lowered distance of rook to OP king
								b_seperate_move = True
								b_mobility_move = False
								b_king_move = False
								b_king_edge = False
							else:
								pass 
					else:
						if _OPT_KING_EDGE and not b_king_edge: # we are forced to take opposition
							if oposition_move != None:
								b_king_edge = True
								PS_king_from_edge = [oposition_move]
						b_opposition_force = False
						if b_king_edge: # edge is more important if we have only a king
							b_mobility_move = False
							b_king_move = False
						elif b_king_move:	
							b_mobility_move = False
					if b_opposition_force:
						r = random.randrange(0, len(PS_opposition_force))
						board.push(PS_opposition_force[r])
						debug_print_board(board,"actual move - opposition forced move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_seperate_move:
						r = random.randrange(0, len(PS_seperate_moves))
						board.push(PS_seperate_moves[r])
						debug_print_board(board,"actual move - seperation/mobility move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_mobility_move: # do mobility move
						# if PS_pieces_value < OP_pieces_value: # PS have disadvantage
						if (len(PS_mobility_moves) > 1) and (len(PS_king_from_edge) > 0): # if we have more mobility moves than one, and we can move king from edge, we use this move
							r = random.randrange(0, len(PS_king_from_edge))
							board.push(PS_king_from_edge[r])
							debug_print_board(board,"actual move - king runs to center", steps, _DEBUG_SIM2)
							stack += 1
						else:
							r = random.randrange(0, len(PS_mobility_moves))
							board.push(PS_mobility_moves[r])
							debug_print_board(board,"actual mobility move", steps, _DEBUG_SIM2)
							stack += 1
						# else: # PS has advantage
						# 	r = random.randrange(0, len(PS_mobility_moves))
						# 	board.push(PS_mobility_moves[r])
						# 	debug_print_board(board,"actual mobility move")
						# 	stack += 1
					elif b_king_move: # do king distance move
						r = random.randrange(0, len(PS_king_moves))
						board.push(PS_king_moves[r])
						debug_print_board(board,"actual king distance move", steps, _DEBUG_SIM2)
						stack += 1
					elif b_king_edge: # do king edge move
						r = random.randrange(0, len(PS_king_from_edge))
						board.push(PS_king_from_edge[r])
						debug_print_board(board,"actual king edge move", steps, _DEBUG_SIM2)
						stack += 1
					elif len(PS_acceptable_moves) > 0: # do acceptable move
						r = random.randrange(0, len(PS_acceptable_moves))
						board.push(PS_acceptable_moves[r])
						debug_print_board(board,"actual acceptable move, steps", steps, _DEBUG_SIM2)
						stack += 1
					else: # :( random move
						r = random.randrange(0, len(PS_legal_moves))
						board.push(PS_legal_moves[r])
						debug_print_board(board,"random move", steps, _DEBUG_SIM2)
						stack += 1
		b_PS_stronger = not b_PS_stronger
		if max_simulation_moves != 0: 
			if stack > max_simulation_moves:
				reason_for_simulation_stop = _STEPS
				win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
				b_end = True
	debug_print_board(board,"End simulation reason= {} ;  moves={} ".format(reason_for_simulation_stop, stack), steps, _DEBUG_SIM)
		
	return win, stack, reason_for_simulation_stop

def simulation_random(node_C, deep_level):	
	reason_for_simulation_stop = None
	win = 0
	steps = 0
	stack = 0 # number of moves on board stack
	b_end = False
	board = chess.Board(node_C.fen)
	debug_print_board(board,"simulation_random start position", steps, _DEBUG_SIM)
	while not b_end:
		steps += 1
		if board.is_game_over(claim_draw = _CLAIM_DRAW):
			reason_for_simulation_stop = _END_GAME
			win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
			b_end = True
		if not b_end: # push next random move
			n_leg_m = board.legal_moves.count()
			if (0==n_leg_m):
				b_end = True
				debug_print_board(board,"no move ??", steps, _DEBUG_SIM3)
			else:
				if n_leg_m==1:
					legal_moves = list(board.legal_moves)
					board.push(legal_moves[0])
					debug_print_board(board,"one move", steps, _DEBUG_SIM3)
					stack += 1
				else:
					legal_moves = list(board.legal_moves)
					r = random.randrange(0, n_leg_m)
					board.push(legal_moves[r])
					debug_print_board(board,"random move", steps, _DEBUG_SIM3)
					stack += 1
	if max_simulation_moves != 0: 
		if stack > max_simulation_moves:
			reason_for_simulation_stop = _STEPS
			win = get_win_value(board.turn, board.result(claim_draw = _CLAIM_DRAW), node_C.turn)
			b_end = True
	debug_print_board(board,"random end", steps, _DEBUG_SIM)
	return win, stack, reason_for_simulation_stop

def simulation(node_C, deep_level):	
	if _OPT_SIMULATION:
		if _OPT_SPECIFIC_HERISTIC:
			if _game_type == KRk:
				return simulation_KRk(node_C, deep_level)
			# elif _game_type == KQk:
			# 	return simulation_KQk(node_C, deep_level)
			else:
				return simulation_gen(node_C, deep_level)
		else:
			return simulation_gen(node_C, deep_level)
	else:
		return simulation_random(node_C, deep_level)


# iterative search from node_M fo first child with no playouts (playouts=0)
# in no such nodes, expand most promising node and return first child
def findLeaf(node_M):
	global _node_id
	deep_level = 0
	decisive_win_node = None
	if (node_M == None):
		raise Exception('ERR findLeaf node_M is none', 'node_M is none')
	if (node_M.playouts == 0): # when the first node is root
		if (node_M.move_uci == 'root'): # special case for root, which can not be played - has no legal moves to play (root)
			if node_M.is_game_over:
				return node_M, deep_level, decisive_win_node
			else:
				_node_id, decisive_win_node = node_M.expand(_node_id)
				deep_level +=1
				if (decisive_win_node != None):
					return decisive_win_node, deep_level, decisive_win_node
				else:
					return node_M.children[0], deep_level, decisive_win_node
		else:
			return node_M, deep_level, decisive_win_node # node_M has no playouts and it is not root
	else:
		b_end = False
		node_parent = node_M
		while not b_end:
			if (node_parent.playouts == 0): # we have a leaf
				return node_parent, deep_level, decisive_win_node
			elif (node_parent.is_game_over):
				return node_parent, deep_level, decisive_win_node
			else: # we go down the tree by the rule of formula
				if len(node_parent.children) == 0: # we have playouts, no children - we must expand and return first child
					_node_id, decisive_win_node = node_parent.expand(_node_id)
					deep_level +=1
					return node_parent.children[0], deep_level, decisive_win_node
				if node_parent.playouts == 0: # for safety - sometimes when we have only one move and we don't make simulation/propagation - we just make a move
					ln_M = 0
				else:	
					ln_M = math.log(node_parent.playouts)
				# node_by_formula = node_parent.children[0]
				max_node_value = -1
				min_sim_steps = 1000
				arr_nodes = [node_parent.children[0]]
				arr_no_playouts = []
				for node_child in node_parent.children:
					if (node_child.playouts == 0): # we have leaf to simulate - because value of the formula is INFINITE
						# return node_child, deep_level, decisive_win_node
						arr_no_playouts.append(node_child)
					else:
						node_value = (node_child.wins / node_child.playouts) + _C * math.sqrt(ln_M / node_child.playouts)
						if (node_value > max_node_value):
							arr_nodes = [node_child]
							max_node_value = node_value
							min_sim_steps = node_child.simulation_steps
						elif (node_value == max_node_value):
							if  _NODE_BY_SIM_STEPS:# if we have this optimisation and both nodes have the same result, we choose a node with lower simulation steps taken to a winning position
								if min_sim_steps > node_child.simulation_steps:
									min_sim_steps = node_child.simulation_steps
									arr_nodes = [node_child]
								elif  min_sim_steps == node_child.simulation_steps:
									arr_nodes.append(node_child)
							else:
								arr_nodes.append(node_child)	
				if len(arr_no_playouts) > 0: # nodes with 0 playouts have infinity - formula number 
					node_by_formula = random.choice(arr_no_playouts)	
				else:
					node_by_formula = random.choice(arr_nodes)
				if node_by_formula == None:
					raise Exception('ERR findLeaf node_by_formula is None', 'node_by_formula=None')
				if (len(node_by_formula.children) == 0): # all nodes have playouts, most valued is node withouth children, so we must expand
					if (node_by_formula.is_game_over):
						deep_level +=1
						return node_by_formula, deep_level, decisive_win_node
					else:
						_node_id, decisive_win_node = node_by_formula.expand(_node_id)
						deep_level +=1
						best_expanded_node =  node_by_formula.children[0]
						if decisive_win_node != None:
							best_expanded_node = decisive_win_node
						return best_expanded_node, deep_level, decisive_win_node
				else:
					deep_level +=1
					node_parent = node_by_formula # we go down in tree search

# from node which was last played move, we run MonteCarlo alghorithm (find leaf, expand, simulate (play one random game))
def searchMonteCarlo(node_M):
	decisive_win_node = None
	# selection
	find_steps = 0
	node_L, deep_level, decisive_win_node = findLeaf(node_M) # find leaf for simulation+
	# if _Debug:
	# 	if (node_L.move_uci == 'a7a6') or (node_L.move_uci == 'a7a4'):
	# 		print('debug')
	# if _Debug:+
	# 	if node_L.move_uci == 'e6f6':
	# 		print('what')
	# if (decisive_win_node != None):
	# 	backPropagate(1, decisive_win_node, node_M, _END_GAME, 1)
	# 	return find_steps, decisive_win_node
	if (node_L == None): # this should not happen
		node_L, deep_level, decisive_win_node = findLeaf(node_M) # DEBUG - call again to find the problem
		node_L = node_M
		raise Exception('ERR searchMonteCarlo node_L in None', 'node_L is none')
	else:
		if (node_L.is_game_over): # no need for expansion and simulation
			# propagate
			backPropagate(node_L.end_game_value, node_L, node_M, _END_GAME, 1) # propagate from node L fo node M
			# if _Debug:
			# 	if ((node_L.move_uci == 'h8g9') or (node_L.move_uci == 'a7g7')):
			# 		print('this is soo wrong 2')
		else:
			if (node_L.playouts == 0):
				# simulation & playouts for random node C
				win, find_steps, reason_for_simulation_stop = simulation(node_L, deep_level)
				if find_steps == 0:
					raise Exception('ERR searchMonteCarlo   find_steps == 0', '')
				backPropagate(win, node_L, node_M, reason_for_simulation_stop, find_steps)
				# if _Debug:
				# 	if ((node_L.move_uci == 'h8g8') ):
				# 		win, find_steps, reason_for_simulation_stop = simulation(node_L, deep_level)
				# 		print('this is soo wrong 3')
			else:
				raise Exception('ERR searchMonteCarlo  - we have the wrong child for playouts - (node_L.playouts != 0)', '')
	return find_steps, decisive_win_node


# get node value by formula type of _NODE_TYPE_SELECTION (_NODE_BY_WINS, _NODE_BY_PLAYOUTS, _NODE_BY_FAKTOR, _NODE_BY_SIM_STEPS)
def get_node_value(p_node):
	tmp_value = 0
	if _NODE_BY_WINS == _NODE_TYPE_SELECTION:
		tmp_value = p_node.wins
	elif _NODE_BY_PLAYOUTS == _NODE_TYPE_SELECTION:
		tmp_value = p_node.playouts
	elif _NODE_BY_FAKTOR == _NODE_TYPE_SELECTION:
		if p_node.playouts > 0:
			tmp_value = p_node.wins / p_node.playouts
	elif _NODE_BY_SIM_STEPS == _NODE_TYPE_SELECTION:
		if (p_node.wins > 0):
			 tmp_value = ( p_node.wins / p_node.simulation_steps)
		# if (p_node.playouts > 0) and (p_node.simulation_steps > 0):
		# 	tmp_value = (p_node.wins /  p_node.simulation_steps) / p_node.playouts
	return tmp_value


def tree_find_levels_traverse(node):
	global _tree_min_level
	global _tree_max_level
	if len(node.children) == 0:
		if node.tree_deep_level < _tree_min_level:
			_tree_min_level = node.tree_deep_level 
		if node.tree_deep_level > _tree_max_level:
			_tree_max_level = node.tree_deep_level 
	else:
		for child in node.children: 
			tree_find_levels_traverse(child)

def tree_find_levels(p_node):
	global _tree_min_level
	global _tree_max_level	
	_tree_min_level = 200000
	_tree_max_level = 0
	tree_find_levels_traverse(p_node)

# we return best child node of parent p_node
def get_best_node_from_tree(p_node):
	best_value = -1
	best_node = None
	l_best_nodes = None
	for node_child in p_node.children:
		if node_child.branch_type == _TO_WIN:
			l_best_nodes = [node_child]
			break
		if node_child.branch_type != _TO_LOSE: # we ignore nodes with decisive information to lose the game
			tmp_value = get_node_value(node_child)
			if tmp_value > best_value:
				l_best_nodes = [node_child]
				best_value = tmp_value
			elif tmp_value == best_value:
				 l_best_nodes.append(node_child)
	if l_best_nodes != None:
		if len(l_best_nodes) > 0:
			best_node = random.choice(l_best_nodes)
	if best_node == None:
		if len(p_node.children) > 0: 
			best_node = p_node.children[0] # all nodes are bad, we return first node
	return best_node, l_best_nodes

def findBestMove(p_node):
	global _tree_min_level
	global _tree_max_level
	best_node = None
	# if len(p_node.children) == 1: # there is only one possible move from current actual board position - if p_node have not been extended we check again in while loop
	# 	# it soo wrong to propagate !!
	# 	# n_b_win = get_win_value(p_node.children[0].turn, p_node.children[0].result, p_node.turn)
	# 	# backPropagate(n_b_win,p_node.children[0], p_node, _END_GAME, 1)
	# 	return p_node.children[0]
	# tmp_best_node = get_best_node_from_tree(p_node)
	find_steps = 0
	b_end = False
	timeStart = time.time()
	# for each actual move, we play the same number of playouts
	if _OPT_SIMULATION:
		num_print = 10
	else:
		num_print = 100
	playouts_num = 0
	while not b_end:
		playouts_num += 1
		if _Debug:
			if (playouts_num % num_print) == 0:
				tmp_best_node, tmp_l_best_nodes = get_best_node_from_tree(p_node)  
				s_best_nodes = ''
				if tmp_l_best_nodes != None:
					for t1 in tmp_l_best_nodes:
						s_best_nodes = s_best_nodes + ' '+t1.move_uci
				if tmp_best_node != None:
					tree_find_levels(p_node)
					print('playout {} / {} , current best = {} {} move; nodes = {} tree.lvl. (min = {} max = {})'.format(playouts_num, max_playouts, s_best_nodes, tmp_best_node.player, _node_id, _tree_min_level, _tree_max_level))
		tmp_steps, decisive_win_node = searchMonteCarlo(p_node)
		# if len(p_node.children) == 1: # we just extended and have one child for the actual move
		# 	# n_b_win = get_win_value(p_node.children[0].turn, p_node.children[0].result, p_node.turn)
		# 	# backPropagate(n_b_win,p_node.children[0], p_node, _END_GAME, 1)
		# 	return p_node.children[0]
		if _DEBUG_SIM3:
			if len(p_node.children)==0:
				print_children(p_node, _DEBUG_SIM3)
			else:
				print_children(p_node.children[0], _DEBUG_SIM3)
		if playouts_num>max_playouts:
			b_end =  True
		find_steps += tmp_steps
		if (max_time_for_find_move > 0): # if == 0 then we use time to stop
			if ((time.time() - timeStart) > max_time_for_find_move):
				b_end = True
		if p_node.branch_type != None:
			b_end = True				
	if _DEBUG_SIM:
		print(p_node)
	best_node, tmp_l_best_node = get_best_node_from_tree(p_node)
	if best_node == None:
		raise Exception('ERR no best node from parent', p_node.move_uci)
	return best_node

def playGame(fen, max_game_time, max_game_moves):
	global _node_id
	global _root_tree_node 
	global _game_type
	global _game_moves_num 
	time_start = time.time()
	random.seed()
	bEnd = False
	board = chess.Board(fen)  
	_game_type = get_game_type(board)
	_game_moves_num = 0
	# create root node for MonteCarlo Tree Search
	if _Debug:
		if board.turn:
			print('starting board position - WHITE to move')
		else:
			print('starting board position - BLACK to move')
		print(board)
		print('A B C D E F G H\n')
	_root_tree_node = mctree(fen, _node_id)
	best_node = _root_tree_node
	while not bEnd:
		best_node = findBestMove(best_node)
		best_node.played_node = True
		_game_moves_num += 1 # we made one move
		board.push(chess.Move.from_uci(best_node.move_uci))
		if _Debug:
			print_played_moves(_root_tree_node, board, time_start)
		bEnd = board.is_game_over(claim_draw = _CLAIM_DRAW)
		if bEnd:
			if _Debug:
				print_played_moves(_root_tree_node, board, time_start)
			if board.is_checkmate():
				if _Debug:
					print('GAME OVER - win with checkmate')
			else:
				if board.is_variant_draw():
					if _Debug:
						print('GAME OVER - draw')
				else:
					if _Debug:
						print('GAME OVER')
		if (max_game_time > 0):
			if ((time.time() - time_start) > max_game_time):
				bEnd = True
				if _Debug:
					print('GAME STOPED - time limit for game exceeded')
		if (max_game_moves > 0):
			if (_game_moves_num > max_game_moves):
				bEnd = True
				if _Debug:
					print('GAME STOPED - max moves for game exceeded')

def playMoneCarlo(board):
	global _node_id
	global _game_type
	_game_type = get_game_type(board)
	random.seed()
	tRoot = mctree(board.fen(), _node_id)
	best_node = tRoot
	best_node = findBestMove(tRoot)
	move = chess.Move.from_uci(best_node.move_uci)
	return move, best_node.wins, best_node.playouts


# Initialize tree from board
def playMoneCarlo_init(board):
	global _node_id
	global _game_type
	global _root_tree_node
	global _play_node
	global _game_moves_num 
	_node_id = 0
	_game_type = get_game_type(board)
	_game_moves_num = 0
	random.seed()
	_root_tree_node = mctree(board.fen(), _node_id)
	_play_node = _root_tree_node

# search children in chosen node and return the node if it exist
def find_child_node(make_move):
	global _play_node
	global _node_id
	ret_node = None
	if len(_play_node.children) == 0:
		_node_id, decisive_win_node = _play_node.expand(_node_id)
	uci = make_move.uci()
	for node in _play_node.children:
		if node.move_uci == uci:
			ret_node = node
			break
	return ret_node


# get best move / return best move
def get_best_move():
	global _play_node
	best_node = findBestMove(_play_node)
	ret_move = chess.Move.from_uci(best_node.move_uci)
	return ret_move, best_node.wins, best_node.playouts

# pick the son of the generated tree
def push_move(move):
	global _play_node
	global _game_moves_num
	if move == None:
		raise Exception('ERR push_move - move is None', 'push_move')
	find_node = find_child_node(move)
	if find_node == None:
		raise Exception('ERR push_move requested move is not legal'+move.uci(), 'push_move')
	find_node.played_node = True
	_game_moves_num += 1 # we made one move	 
	_play_node = find_node

# play move: if (make_move == None) then we make our move else we make move make_move and then play our move
def playMoneCarlo_move(make_move):
	global _game_moves_num 
	global _play_node
	_game_moves_num = 0
	if _play_node == None:
		raise Exception('ERR first ran initializaton procedure playMoneCarlo_init', 'playMoneCarlo_move')
	if make_move != None:
		opponent_node = find_child_node(make_move)
		if opponent_node == None:
			raise Exception('ERR requested move is not legal'+make_move.uci(), 'playMoneCarlo_move')
		opponent_node.played_node = True
		_game_moves_num += 1 # we made one move
		_play_node = opponent_node
	_play_node = findBestMove(_play_node)
	ret_move = chess.Move.from_uci(_play_node.move_uci)

	# Save json
	if _generate_json:
		save_json(_play_node.parent, "mcts_last_move.json")

	return ret_move, _play_node.wins, _play_node.playouts

def play_with_human(board, human_start):	
	playMoneCarlo_init(board)
	print('Starting board')
	print(board)
	print('A B C D E F G H\n')
	if board.turn:
		print('white to play next move')
	else:
		print('black to play next move')
	b_play = True
	first_time = not human_start
	while b_play:
		if first_time:
			first_time = False
			# MC play
			ret_move, _play_node.wins, _play_node.playouts = playMoneCarlo_move(None)
			board.push(ret_move)
			print('Mastermind played:',ret_move.uci())
			print(board)
			print('A B C D E F G H\n')		
			if board.is_game_over(claim_draw = _CLAIM_DRAW):
				b_play = False
				if board.is_checkmate():
					if _Debug:
						print('GAME OVER - win with checkmate')
				else:
					if board.is_variant_draw():
						if _Debug:
							print('GAME OVER - draw')
					else:
						if _Debug:
							print('GAME OVER')			
			human_to_move = not human_to_move
		else:
			human_uci = input('Make a move human:') 
			human_move = chess.Move.from_uci(human_uci)
			board.push(human_move)
			print('You played:', human_move.uci())
			print(board)
			print('A B C D E F G H\n')				
			ret_move, _play_node.wins, _play_node.playouts = playMoneCarlo_move(human_move)
			board.push(ret_move)
			if board.is_game_over(claim_draw = _CLAIM_DRAW):
				b_play = False
				if board.is_checkmate():
					if _Debug:
						print('GAME OVER - win with checkmate')
				else:
					if board.is_variant_draw():
						if _Debug:
							print('GAME OVER - draw')
					else:
						if _Debug:
							print('GAME OVER')		
				break	
			else:			
				print('Mastermind played:',ret_move.uci())
				print(board)
				print('A B C D E F G H\n')	
				if board.is_game_over(claim_draw = _CLAIM_DRAW):
					b_play = False
					if board.is_checkmate():
						if _Debug:
							print('GAME OVER - win with checkmate')
					else:
						if board.is_variant_draw():
							if _Debug:
								print('GAME OVER - draw')
						else:
							if _Debug:
								print('GAME OVER')	
					break	

def save_json(node, filepath):
	new_json = construct_json(node)
	#print(str(json.dumps(new_json, indent=4)))
	with open(filepath, "w") as output_file:
		output_file.write(str(json.dumps(new_json, indent=4)))

def construct_json(node, jobject = None):
	# At root
	if jobject == None:
		jobject = json.loads("{}")

	# Add current node properties
	jobject["id"] = node.node_id
	jobject["wins"] = node.wins
	jobject["playouts"] = node.playouts
	jobject["fen"] = node.fen
	jobject["children"] = []
	jobject["move"] = node.move_uci
	jobject["parent"] = None
	jobject["turn"] = node.turn
	if node.parent != None:
		jobject["parent"] = node.parent.node_id

	# Add children
	# TODO add a limiter which ads only n-best children to each node
	for child in node.children:
		child_jobject = construct_json(child)
		jobject["children"].append(child_jobject)

	return jobject

# Direct run this module - for testing
if __name__ == "__main__":
	board = chess.Board("7k/2R5/5K2/8/8/8/8/8 w - - 0 1")
	playMoneCarlo_init(board)
	# make_move = chess.Move.from_uci('h8h7')
	# make_move = None
	_OPT_SIMULATION = False
	best_move, wins, playouts = get_best_move()

	save_json(_root_tree_node, "MCTS_X_single.json")

	stop_me = 0
	

#core internal debugging
	#playGame(fen, max_game_time, max_game_moves)