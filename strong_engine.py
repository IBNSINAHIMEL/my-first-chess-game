"""
Strong Chess Engine using python-chess with minimax, alpha-beta pruning, and position evaluation
"""

import chess
import math
import random
from typing import List, Tuple, Optional

class StrongChessEngine:
    """Strong chess engine with proper search algorithm"""
    
    def __init__(self, difficulty=3):
        """
        difficulty levels:
        1: Easy (depth 2)
        2: Medium (depth 3) 
        3: Hard (depth 4)
        4: Expert (depth 5)
        """
        self.difficulty = difficulty
        
        # Piece values (centipawns)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece-square tables (middlegame) - Improved values
        self.pawn_table = [
            0,   0,   0,   0,   0,   0,   0,   0,
            50,  50,  50,  50,  50,  50,  50,  50,
            10,  10,  20,  30,  30,  20,  10,  10,
            5,   5,  10,  25,  25,  10,   5,   5,
            0,   0,   0,  20,  20,   0,   0,   0,
            5,  -5, -10,   0,   0, -10,  -5,   5,
            5,  10,  10, -20, -20,  10,  10,   5,
            0,   0,   0,   0,   0,   0,   0,   0
        ]
        
        self.knight_table = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,   0,   0,   0,   0, -20, -40,
            -30,   0,  10,  15,  15,  10,   0, -30,
            -30,   5,  15,  20,  20,  15,   5, -30,
            -30,   0,  15,  20,  20,  15,   0, -30,
            -30,   5,  10,  15,  15,  10,   5, -30,
            -40, -20,   0,   5,   5,   0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
        
        self.bishop_table = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -10,   0,   5,  10,  10,   5,   0, -10,
            -10,   5,   5,  10,  10,   5,   5, -10,
            -10,   0,  10,  10,  10,  10,   0, -10,
            -10,  10,  10,  10,  10,  10,  10, -10,
            -10,   5,   0,   0,   0,   0,   5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ]
        
        self.rook_table = [
            0,   0,   0,   0,   0,   0,   0,   0,
            5,  10,  10,  10,  10,  10,  10,   5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            0,   0,   0,   5,   5,   0,   0,   0
        ]
        
        self.queen_table = [
            -20, -10, -10,  -5,  -5, -10, -10, -20,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
            -5,   0,   5,   5,   5,   5,   0,  -5,
            0,   0,   5,   5,   5,   5,   0,  -5,
            -10,   5,   5,   5,   5,   5,   0, -10,
            -10,   0,   5,   0,   0,   0,   0, -10,
            -20, -10, -10,  -5,  -5, -10, -10, -20
        ]
        
        self.king_middle_table = [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20,  20,   0,   0,   0,   0,  20,  20,
            20,  30,  10,   0,   0,  10,  30,  20
        ]
        
        self.king_end_table = [
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10,   0,   0, -10, -20, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -30,   0,   0,   0,   0, -30, -30,
            -50, -30, -30, -30, -30, -30, -30, -50
        ]
        
        # Set search parameters based on difficulty
        self.update_depth()
        
        # Transposition table
        self.transposition_table = {}
        self.nodes_searched = 0
        self.max_nodes = 0
        
        # Killer moves and history heuristic
        self.killer_moves = [[None, None] for _ in range(64)]  # Two killer moves per ply
        self.history_table = [[0 for _ in range(64)] for _ in range(64)]  # [from][to]
        
        print(f"🎯 Chess Engine initialized with difficulty {self.difficulty} (depth: {self.max_depth})")
    
    def update_depth(self):
        """Update search depth based on current difficulty"""
        if self.difficulty == 1:
            self.max_depth = 2  # Easy
            self.max_nodes = 5000
        elif self.difficulty == 2:
            self.max_depth = 3  # Medium
            self.max_nodes = 20000
        elif self.difficulty == 3:
            self.max_depth = 4  # Hard
            self.max_nodes = 50000
        elif self.difficulty == 4:
            self.max_depth = 5  # Expert
            self.max_nodes = 100000
        else:
            self.max_depth = 3  # Default
            self.max_nodes = 20000
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Evaluate the board position with improved evaluation"""
        if board.is_checkmate():
            return -100000 if board.turn else 100000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        score = 0
        
        # Material evaluation
        white_material = 0
        black_material = 0
        
        # Piece-square evaluation
        white_position = 0
        black_position = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Material value
                material = self.piece_values[piece.piece_type]
                
                # Position value
                position_value = self.get_position_value(piece, square, board)
                
                if piece.color == chess.WHITE:
                    white_material += material
                    white_position += position_value
                else:
                    black_material += material
                    black_position += position_value
        
        score = (white_material + white_position) - (black_material + black_position)
        
        # Mobility (number of legal moves)
        white_mobility = len(list(board.legal_moves))
        board.turn = not board.turn
        black_mobility = len(list(board.legal_moves))
        board.turn = not board.turn  # Reset turn
        
        score += (white_mobility - black_mobility) * 10
        
        # Pawn structure
        score += self.evaluate_pawn_structure(board)
        
        # King safety
        score += self.evaluate_king_safety(board)
        
        # Center control
        score += self.evaluate_center_control(board)
        
        # Piece activity
        score += self.evaluate_piece_activity(board)
        
        # Bishop pair bonus
        if self.count_bishops(board, chess.WHITE) >= 2:
            score += 30
        if self.count_bishops(board, chess.BLACK) >= 2:
            score -= 30
        
        # Rook on open/semi-open files
        score += self.evaluate_rooks(board)
        
        # Perspective: positive score is good for white, negative for black
        return score
    
    def get_position_value(self, piece: chess.Piece, square: chess.Square, board: chess.Board) -> float:
        """Get position bonus for a piece"""
        tables = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: self.knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_middle_table if self.count_material(board) > 2000 else self.king_end_table
        }
        
        table = tables[piece.piece_type]
        
        # Flip square for black pieces
        if piece.color == chess.WHITE:
            idx = square
        else:
            # Mirror vertically
            row = 7 - (square // 8)
            col = square % 8
            idx = row * 8 + col
        
        return table[idx]
    
    def count_material(self, board: chess.Board) -> int:
        """Count total material on board"""
        total = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.KING:
                total += self.piece_values[piece.piece_type]
        return total
    
    def count_bishops(self, board: chess.Board, color: chess.Color) -> int:
        """Count bishops of a given color"""
        count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color and piece.piece_type == chess.BISHOP:
                count += 1
        return count
    
    def evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Evaluate pawn structure"""
        score = 0
        
        # Doubled pawns penalty
        for file in range(8):
            white_pawns = 0
            black_pawns = 0
            
            for rank in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                
                if piece == chess.Piece(chess.PAWN, chess.WHITE):
                    white_pawns += 1
                elif piece == chess.Piece(chess.PAWN, chess.BLACK):
                    black_pawns += 1
            
            if white_pawns > 1:
                score -= (white_pawns - 1) * 20  # Doubled pawn penalty
            if black_pawns > 1:
                score += (black_pawns - 1) * 20
        
        # Isolated pawns penalty
        for file in range(8):
            for rank in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                
                if piece == chess.Piece(chess.PAWN, chess.WHITE):
                    # Check if pawn is isolated (no friendly pawns on adjacent files)
                    isolated = True
                    for adj_file in [file - 1, file + 1]:
                        if 0 <= adj_file < 8:
                            for adj_rank in range(8):
                                adj_square = chess.square(adj_file, adj_rank)
                                adj_piece = board.piece_at(adj_square)
                                if adj_piece == chess.Piece(chess.PAWN, chess.WHITE):
                                    isolated = False
                                    break
                    if isolated:
                        score -= 15
                
                elif piece == chess.Piece(chess.PAWN, chess.BLACK):
                    isolated = True
                    for adj_file in [file - 1, file + 1]:
                        if 0 <= adj_file < 8:
                            for adj_rank in range(8):
                                adj_square = chess.square(adj_file, adj_rank)
                                adj_piece = board.piece_at(adj_square)
                                if adj_piece == chess.Piece(chess.PAWN, chess.BLACK):
                                    isolated = False
                                    break
                    if isolated:
                        score += 15
        
        # Passed pawns bonus
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                if self.is_passed_pawn(board, square, piece.color):
                    bonus = 30
                    # Extra bonus for advanced passed pawns
                    rank = chess.square_rank(square)
                    if piece.color == chess.WHITE:
                        bonus += rank * 10  # Closer to promotion
                    else:
                        bonus += (7 - rank) * 10
                    
                    if piece.color == chess.WHITE:
                        score += bonus
                    else:
                        score -= bonus
        
        return score
    
    def is_passed_pawn(self, board: chess.Board, square: chess.Square, color: chess.Color) -> bool:
        """Check if pawn is a passed pawn"""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        if color == chess.WHITE:
            # Check files: current, left, right
            for f in [file - 1, file, file + 1]:
                if 0 <= f < 8:
                    for r in range(rank + 1, 8):  # Ahead of the pawn
                        s = chess.square(f, r)
                        piece = board.piece_at(s)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            return False
        else:  # BLACK
            for f in [file - 1, file, file + 1]:
                if 0 <= f < 8:
                    for r in range(rank - 1, -1, -1):  # Ahead of the pawn (downwards)
                        s = chess.square(f, r)
                        piece = board.piece_at(s)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            return False
        
        return True
    
    def evaluate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety"""
        score = 0
        
        # White king
        white_king = board.king(chess.WHITE)
        if white_king:
            # Penalize if king is not castled in middle game
            if white_king in [chess.E1, chess.D1, chess.F1] and board.fullmove_number < 20:
                score -= 40
            
            # Bonus for castled king
            if white_king in [chess.G1, chess.C1]:  # Castled
                score += 30
            
            # Penalty for exposed king (few pawns around)
            score -= self.king_shield_penalty(board, white_king, chess.WHITE)
        
        # Black king
        black_king = board.king(chess.BLACK)
        if black_king:
            if black_king in [chess.E8, chess.D8, chess.F8] and board.fullmove_number < 20:
                score += 40
            
            if black_king in [chess.G8, chess.C8]:
                score -= 30
            
            score += self.king_shield_penalty(board, black_king, chess.BLACK)
        
        return score
    
    def king_shield_penalty(self, board: chess.Board, king_square: chess.Square, color: chess.Color) -> float:
        """Calculate penalty for weak king pawn shield"""
        penalty = 0
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        # Check pawns in front of king
        for file_offset in [-1, 0, 1]:
            file = king_file + file_offset
            if 0 <= file < 8:
                if color == chess.WHITE:
                    pawn_rank = king_rank + 1  # Square in front of king
                else:
                    pawn_rank = king_rank - 1
                
                if 0 <= pawn_rank < 8:
                    square = chess.square(file, pawn_rank)
                    piece = board.piece_at(square)
                    if not (piece and piece.piece_type == chess.PAWN and piece.color == color):
                        penalty += 10  # Missing pawn in shield
        
        return penalty
    
    def evaluate_center_control(self, board: chess.Board) -> float:
        """Evaluate center control"""
        score = 0
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        extended_center = [chess.C3, chess.D3, chess.E3, chess.F3,
                          chess.C4, chess.D4, chess.E4, chess.F4,
                          chess.C5, chess.D5, chess.E5, chess.F5,
                          chess.C6, chess.D6, chess.E6, chess.F6]
        
        for square in extended_center:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 5
                else:
                    score -= 5
        
        return score
    
    def evaluate_piece_activity(self, board: chess.Board) -> float:
        """Evaluate piece activity"""
        score = 0
        
        # Knights in center bonus
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.KNIGHT:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                
                # Knights in center are better
                center_distance = max(abs(file - 3.5), abs(rank - 3.5))
                activity_bonus = 20 - int(center_distance * 5)
                
                if piece.color == chess.WHITE:
                    score += activity_bonus
                else:
                    score -= activity_bonus
        
        return score
    
    def evaluate_rooks(self, board: chess.Board) -> float:
        """Evaluate rook placement"""
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.ROOK:
                # Rook on open file bonus
                file = chess.square_file(square)
                is_open_file = True
                
                for rank in range(8):
                    s = chess.square(file, rank)
                    p = board.piece_at(s)
                    if p and p.piece_type == chess.PAWN:
                        is_open_file = False
                        break
                
                if is_open_file:
                    if piece.color == chess.WHITE:
                        score += 25
                    else:
                        score -= 25
                
                # Rook on 7th rank bonus (attacking enemy king's position)
                rank = chess.square_rank(square)
                if (piece.color == chess.WHITE and rank == 6) or (piece.color == chess.BLACK and rank == 1):
                    if piece.color == chess.WHITE:
                        score += 30
                    else:
                        score -= 30
        
        return score
    
    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                maximizing: bool, ply: int = 0) -> float:
        """Minimax with alpha-beta pruning and quiescence search"""
        self.nodes_searched += 1
        
        # Check node limit
        if self.nodes_searched >= self.max_nodes:
            return self.evaluate_position(board)
        
        # Check for repetition or 50-move rule
        if board.can_claim_threefold_repetition() or board.halfmove_clock >= 100:
            return 0
        
        # Quiescence search at leaf nodes
        if depth == 0:
            return self.quiescence(board, alpha, beta, maximizing)
        
        # Generate moves
        moves = self.order_moves(board, ply)
        
        if maximizing:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False, ply + 1)
                board.pop()
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                
                if beta <= alpha:
                    # Store killer move
                    if not board.is_capture(move):
                        self.killer_moves[ply][1] = self.killer_moves[ply][0]
                        self.killer_moves[ply][0] = move
                    break
            
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True, ply + 1)
                board.pop()
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                if beta <= alpha:
                    # Store killer move
                    if not board.is_capture(move):
                        self.killer_moves[ply][1] = self.killer_moves[ply][0]
                        self.killer_moves[ply][0] = move
                    break
            
            return min_eval
    
    def quiescence(self, board: chess.Board, alpha: float, beta: float, maximizing: bool) -> float:
        """Quiescence search to evaluate only capture moves at leaf nodes"""
        self.nodes_searched += 1
        
        # Evaluate static position
        stand_pat = self.evaluate_position(board)
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat
        
        # Only consider captures and promotions
        moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion:
                moves.append(move)
        
        # Order capture moves (MVV-LVA)
        moves.sort(key=lambda m: self.capture_value(board, m), reverse=True)
        
        if maximizing:
            for move in moves:
                board.push(move)
                score = self.quiescence(board, alpha, beta, False)
                board.pop()
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            
            return alpha
        else:
            for move in moves:
                board.push(move)
                score = self.quiescence(board, alpha, beta, True)
                board.pop()
                
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
            
            return beta
    
    def capture_value(self, board: chess.Board, move: chess.Move) -> int:
        """Calculate MVV-LVA value for move ordering"""
        value = 0
        
        # Most Valuable Victim - Least Valuable Aggressor
        if board.is_capture(move):
            captured = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            
            if captured and attacker:
                victim_value = self.piece_values.get(captured.piece_type, 0)
                aggressor_value = self.piece_values.get(attacker.piece_type, 0)
                value = victim_value * 10 - aggressor_value
        
        # Promotions are valuable
        if move.promotion:
            value += 1000
        
        return value
    
    def order_moves(self, board: chess.Board, ply: int = 0) -> List[chess.Move]:
        """Order moves for better alpha-beta pruning with killer moves and history heuristic"""
        moves = list(board.legal_moves)
        
        move_scores = []
        
        for move in moves:
            score = 0
            
            # 1. PV move (we don't have PV in this simple implementation)
            
            # 2. Captures (MVV-LVA)
            if board.is_capture(move):
                score = 10000 + self.capture_value(board, move)
            
            # 3. Promotions
            elif move.promotion:
                score = 9000 + self.piece_values.get(move.promotion, 0)
            
            # 4. Killer moves
            elif self.killer_moves[ply][0] == move:
                score = 8000
            elif self.killer_moves[ply][1] == move:
                score = 7000
            
            # 5. History heuristic
            else:
                score = self.history_table[move.from_square][move.to_square]
            
            # 6. Good positional moves
            piece = board.piece_at(move.from_square)
            if piece:
                # Developing minor pieces in opening
                if board.fullmove_number < 10:
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        if move.from_square in [chess.B1, chess.G1, chess.B8, chess.G8,  # Knight starting squares
                                               chess.C1, chess.F1, chess.C8, chess.F8]:  # Bishop starting squares
                            score += 500
                
                # Center control
                if move.to_square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                    score += 100
                
                # Castling
                if board.is_castling(move):
                    score += 600
            
            move_scores.append((move, score))
        
        # Sort by score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def update_history(self, move: chess.Move, depth: int, ply: int):
        """Update history heuristic table"""
        self.history_table[move.from_square][move.to_square] += depth * depth
    
    def get_best_move(self, fen: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get the best move for given position with iterative deepening"""
        try:
            board = chess.Board(fen)
            
            if board.is_game_over():
                return None, None, None
            
            # Update depth based on current difficulty
            self.update_depth()
            
            # Reset search statistics
            self.nodes_searched = 0
            self.transposition_table.clear()
            
            print(f"🤖 Engine thinking (difficulty: {self.difficulty}, depth: {self.max_depth})...")
            
            # Simple iterative deepening for better move selection
            best_move = None
            best_value = -math.inf if board.turn == chess.WHITE else math.inf
            
            # Try different depths based on time/complexity
            target_depth = self.max_depth
            if len(list(board.legal_moves)) > 35:  # Very complex position
                target_depth = max(2, target_depth - 1)
            
            # Order moves
            ordered_moves = self.order_moves(board)
            
            alpha = -math.inf
            beta = math.inf
            
            # Search each move
            for move in ordered_moves:
                if self.nodes_searched >= self.max_nodes:
                    print(f"⚠️ Node limit reached ({self.nodes_searched})")
                    break
                
                board.push(move)
                eval = self.minimax(board, target_depth - 1, alpha, beta, board.turn == chess.WHITE)
                board.pop()
                
                if (board.turn == chess.WHITE and eval > best_value) or \
                   (board.turn == chess.BLACK and eval < best_value):
                    best_value = eval
                    best_move = move
                
                if board.turn == chess.WHITE:
                    alpha = max(alpha, eval)
                else:
                    beta = min(beta, eval)
            
            if best_move:
                from_sq = chess.square_name(best_move.from_square)
                to_sq = chess.square_name(best_move.to_square)
                promotion = chess.piece_symbol(best_move.promotion).lower() if best_move.promotion else None
                
                # Update history heuristic
                self.update_history(best_move, target_depth, 0)
                
                print(f"✅ Engine move: {from_sq} -> {to_sq} (eval: {best_value:.1f}, nodes: {self.nodes_searched})")
                return from_sq, to_sq, promotion
            
            # Fallback: choose the first legal move
            print("⚠️ No best move found, using first legal move")
            move = list(board.legal_moves)[0]
            from_sq = chess.square_name(move.from_square)
            to_sq = chess.square_name(move.to_square)
            promotion = chess.piece_symbol(move.promotion).lower() if move.promotion else None
            
            return from_sq, to_sq, promotion
            
        except Exception as e:
            print(f"❌ Engine error: {e}")
            import traceback
            traceback.print_exc()
            
            # Last resort: random move
            try:
                board = chess.Board(fen)
                if board.is_game_over():
                    return None, None, None
                
                import random
                move = random.choice(list(board.legal_moves))
                from_sq = chess.square_name(move.from_square)
                to_sq = chess.square_name(move.to_square)
                promotion = chess.piece_symbol(move.promotion).lower() if move.promotion else None
                
                return from_sq, to_sq, promotion
            except:
                return None, None, None


# Test the engine
if __name__ == "__main__":
    print("🧪 Testing Strong Chess Engine...")
    
    engine = StrongChessEngine(difficulty=3)
    
    # Test with starting position
    test_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    result = engine.get_best_move(test_fen)
    
    if result[0]:
        print(f"✅ Engine test successful: {result[0]} -> {result[1]}")
    else:
        print("❌ Engine test failed")
