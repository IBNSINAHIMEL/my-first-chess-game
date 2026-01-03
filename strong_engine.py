"""
Optimized Chess Engine using python-chess with time management
Compatible with the Flask web interface
"""

import chess
import math
import random
import time
from typing import List, Tuple, Optional

class StrongChessEngine:
    """Optimized chess engine with proper search algorithm and time management"""
    
    def __init__(self, difficulty=3):
        """
        difficulty levels:
        1: Easy (depth 2-3, 5 seconds max)
        2: Medium (depth 3-4, 10 seconds max) 
        3: Hard (depth 4-5, 15 seconds max)
        4: Expert (depth 5-6, 20 seconds max)
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
        
        # Piece-square tables - simplified for speed
        self.pawn_table = [
            0,   0,   0,   0,   0,   0,   0,   0,
            50,  50,  50,  50,  50,  50,  50,  50,
            10,  10,  20,  25,  25,  20,  10,  10,
            5,   5,  10,  20,  20,  10,   5,   5,
            0,   0,   0,  15,  15,   0,   0,   0,
            5,  -5, -10,   0,   0, -10,  -5,   5,
            5,  10,  10, -20, -20,  10,  10,   5,
            0,   0,   0,   0,   0,   0,   0,   0
        ]
        
        self.knight_table = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,   0,   5,   5,   0, -20, -40,
            -30,   0,  10,  15,  15,  10,   0, -30,
            -30,   5,  15,  20,  20,  15,   5, -30,
            -30,   0,  15,  20,  20,  15,   0, -30,
            -30,   5,  10,  15,  15,  10,   5, -30,
            -40, -20,   0,   5,   5,   0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
        
        self.bishop_table = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,   5,   0,   0,   0,   0,   5, -10,
            -10,  10,  10,  10,  10,  10,  10, -10,
            -10,   0,  10,  10,  10,  10,   0, -10,
            -10,   5,   5,  10,  10,   5,   5, -10,
            -10,   0,   5,  10,  10,   5,   0, -10,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ]
        
        self.rook_table = [
            0,   0,   0,   5,   5,   0,   0,   0,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            5,  10,  10,  10,  10,  10,  10,   5,
            0,   0,   0,   0,   0,   0,   0,   0
        ]
        
        self.queen_table = [
            -20, -10, -10,  -5,  -5, -10, -10, -20,
            -10,   0,   5,   0,   0,   0,   0, -10,
            -10,   5,   5,   5,   5,   5,   0, -10,
            0,   0,   5,   5,   5,   5,   0,  -5,
            -5,   0,   5,   5,   5,   5,   0,  -5,
            -10,   0,   5,   5,   5,   5,   0, -10,
            -10,   0,   0,   0,   0,   0,   0, -10,
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
        
        # Initialize parameters
        self.update_depth()
        
        # Search tracking
        self.nodes_searched = 0
        self.start_time = None
        self.timeout = False
        self.best_move_found = None
        
        # Move ordering heuristics
        self.killer_moves = [[None, None] for _ in range(64)]
        self.history_table = [[0 for _ in range(64)] for _ in range(64)]
        
        print(f"🎯 Chess Engine initialized with difficulty {self.difficulty}")
        print(f"   Target: Depth {self.target_depth}, Time limit: {self.max_time}s")
    
    def update_depth(self):
        """Update search parameters based on current difficulty"""
        # Time limits per difficulty
        self.time_limits = {1: 5, 2: 10, 3: 15, 4: 20}  # seconds
        self.depth_limits = {1: 3, 2: 4, 3: 5, 4: 6}
        
        self.max_time = self.time_limits.get(self.difficulty, 10)
        self.target_depth = self.depth_limits.get(self.difficulty, 4)
        self.max_depth = self.target_depth  # For compatibility
        self.max_nodes = 1000000  # Default high value
    
    def check_timeout(self) -> bool:
        """Check if search should timeout"""
        if self.start_time and (time.time() - self.start_time) > self.max_time:
            self.timeout = True
            return True
        return False
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Fast evaluation of the board position"""
        # Quick terminal condition checks
        if board.is_checkmate():
            return -99999 if board.turn else 99999
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        # Material and positional evaluation
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Material value
                material = self.piece_values[piece.piece_type]
                
                # Position value (simplified)
                if piece.color == chess.WHITE:
                    score += material + self.get_fast_position_value(piece, square, board)
                else:
                    score -= material + self.get_fast_position_value(piece, square, board)
        
        # Simple mobility bonus
        legal_moves = len(list(board.legal_moves))
        if board.turn == chess.WHITE:
            score += legal_moves * 5
        else:
            score -= legal_moves * 5
        
        return score
    
    def get_fast_position_value(self, piece: chess.Piece, square: chess.Square, board: chess.Board) -> float:
        """Fast position value lookup"""
        tables = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: self.knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_middle_table
        }
        
        table = tables.get(piece.piece_type)
        if not table:
            return 0
        
        # Flip square for black pieces
        if piece.color == chess.WHITE:
            idx = square
        else:
            row = 7 - (square // 8)
            col = square % 8
            idx = row * 8 + col
        
        return table[idx]
    
    def iterative_deepening_search(self, board: chess.Board, max_depth: int) -> Tuple[Optional[chess.Move], float]:
        """Perform iterative deepening search with time management"""
        self.start_time = time.time()
        self.timeout = False
        self.nodes_searched = 0
        
        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf
        
        # Try depths from 2 to max_depth
        for depth in range(2, max_depth + 1):
            if self.timeout:
                break
                
            print(f"  Searching depth {depth}...")
            
            # Search with current depth
            try:
                current_best_move, current_best_value = self.alpha_beta_search(
                    board, depth, -math.inf, math.inf, board.turn == chess.WHITE
                )
                
                if not self.timeout and current_best_move:
                    best_move = current_best_move
                    best_value = current_best_value
                    print(f"    Depth {depth}: eval = {best_value:.1f}, nodes = {self.nodes_searched}")
                    
                    # If we found a forced mate, no need to search deeper
                    if abs(best_value) > 90000:
                        print(f"    Found forced mate, stopping search")
                        break
            except Exception as e:
                if not self.timeout:
                    print(f"    Error at depth {depth}: {e}")
                break
        
        print(f"  Search complete: {self.nodes_searched} nodes")
        return best_move, best_value
    
    def alpha_beta_search(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                         maximizing: bool, ply: int = 0) -> Tuple[Optional[chess.Move], float]:
        """Alpha-beta search with time management"""
        # Check timeout every 1000 nodes
        if self.nodes_searched % 1000 == 0 and self.check_timeout():
            return None, 0
        
        self.nodes_searched += 1
        
        # Check for terminal conditions
        if board.is_checkmate():
            return None, -99999 if maximizing else 99999
        
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
            return None, 0
        
        # Leaf node - use quiescence search or evaluation
        if depth == 0:
            return None, self.quiescence(board, alpha, beta, maximizing)
        
        # Generate and order moves
        moves = self.order_moves(board, ply, depth==1)
        best_move = None
        best_value = -math.inf if maximizing else math.inf
        
        for move in moves:
            # Check timeout
            if self.timeout:
                break
                
            board.push(move)
            
            # Recursive search
            _, move_value = self.alpha_beta_search(board, depth - 1, alpha, beta, not maximizing, ply + 1)
            
            board.pop()
            
            if self.timeout:
                break
            
            if maximizing:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
                    alpha = max(alpha, best_value)
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
                    beta = min(beta, best_value)
            
            # Alpha-beta cutoff
            if beta <= alpha:
                # Store killer move
                if not board.is_capture(move):
                    if move != self.killer_moves[ply][0]:
                        self.killer_moves[ply][1] = self.killer_moves[ply][0]
                        self.killer_moves[ply][0] = move
                break
        
        return best_move, best_value if best_value != -math.inf and best_value != math.inf else 0
    
    def quiescence(self, board: chess.Board, alpha: float, beta: float, maximizing: bool) -> float:
        """Quiescence search to evaluate only capture moves"""
        # Static evaluation
        stand_pat = self.evaluate_position(board)
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat
        
        # Generate capture moves only
        capture_moves = []
        for move in board.legal_moves:
            if board.is_capture(move):
                capture_moves.append(move)
        
        # Sort captures by expected gain (MVV-LVA)
        capture_moves.sort(key=lambda m: self.estimate_capture_value(board, m), reverse=True)
        
        for move in capture_moves:
            # Check timeout
            if self.check_timeout():
                break
                
            # Delta pruning - skip obviously bad captures
            if self.delta_pruning(board, move, stand_pat, alpha, beta, maximizing):
                continue
                
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha, not maximizing)
            board.pop()
            
            if maximizing:
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            else:
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
        
        return alpha if maximizing else beta
    
    def estimate_capture_value(self, board: chess.Board, move: chess.Move) -> int:
        """Estimate capture value for move ordering (MVV-LVA)"""
        if not board.is_capture(move):
            return 0
            
        victim = board.piece_at(move.to_square)
        aggressor = board.piece_at(move.from_square)
        
        if not victim or not aggressor:
            return 0
            
        victim_value = self.piece_values.get(victim.piece_type, 0)
        aggressor_value = self.piece_values.get(aggressor.piece_type, 0)
        
        return victim_value * 10 - aggressor_value
    
    def delta_pruning(self, board: chess.Board, move: chess.Move, stand_pat: float, 
                     alpha: float, beta: float, maximizing: bool) -> bool:
        """Delta pruning - skip captures that can't improve alpha"""
        if not board.is_capture(move):
            return False
            
        victim = board.piece_at(move.to_square)
        if not victim:
            return False
            
        victim_value = self.piece_values.get(victim.piece_type, 0)
        
        # If capturing the victim can't raise alpha, skip it
        if maximizing:
            if stand_pat + victim_value + 100 < alpha:  # Small margin
                return True
        else:
            if stand_pat - victim_value - 100 > beta:  # Small margin
                return True
                
        return False
    
    def order_moves(self, board: chess.Board, ply: int = 0, is_qsearch: bool = False) -> List[chess.Move]:
        """Order moves for better alpha-beta pruning"""
        moves = list(board.legal_moves)
        
        # If very few moves or at leaf of quiescence search, don't spend time sorting
        if len(moves) <= 3 or (is_qsearch and len(moves) <= 5):
            return moves
        
        move_scores = []
        
        for move in moves:
            score = 0
            
            # 1. Captures (ordered by MVV-LVA)
            if board.is_capture(move):
                score = 10000 + self.estimate_capture_value(board, move)
            
            # 2. Promotions
            elif move.promotion:
                score = 9000 + self.piece_values.get(move.promotion, 0)
            
            # 3. Killer moves (only in main search)
            elif not is_qsearch:
                if self.killer_moves[ply][0] == move:
                    score = 8000
                elif self.killer_moves[ply][1] == move:
                    score = 7000
            
            # 4. Simple positional bonuses
            piece = board.piece_at(move.from_square)
            if piece:
                # Center control
                to_file = chess.square_file(move.to_square)
                to_rank = chess.square_rank(move.to_square)
                
                # Bonus for moving to center
                if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
                    score += 50
                
                # Bonus for developing pieces early
                if board.fullmove_number < 10:
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        if move.from_square in [chess.B1, chess.G1, chess.B8, chess.G8,
                                               chess.C1, chess.F1, chess.C8, chess.F8]:
                            score += 100
                
                # Bonus for castling
                if board.is_castling(move):
                    score += 300
            
            move_scores.append((move, score))
        
        # Sort by score (highest first)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def get_best_move(self, fen: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get the best move for given position with time management"""
        try:
            board = chess.Board(fen)
            
            if board.is_game_over():
                return None, None, None
            
            print(f"🤖 Engine thinking (difficulty: {self.difficulty}, time limit: {self.max_time}s)...")
            
            # Determine search depth based on position complexity
            legal_moves = list(board.legal_moves)
            
            # Adjust depth based on position complexity
            if len(legal_moves) > 40:  # Very complex position
                effective_depth = min(self.target_depth - 1, 4)
            elif len(legal_moves) > 25:  # Complex position
                effective_depth = min(self.target_depth, 5)
            else:  # Normal position
                effective_depth = self.target_depth
            
            print(f"  Position has {len(legal_moves)} legal moves, searching to depth {effective_depth}")
            
            # Perform iterative deepening search
            best_move, eval_score = self.iterative_deepening_search(board, effective_depth)
            
            # If search timed out or found no move, use fallback
            if not best_move or self.timeout:
                print(f"  {'Timeout' if self.timeout else 'No move found'}, using best available move")
                
                # Try to use the last best move found
                if not best_move:
                    # Order moves and pick the best one based on simple evaluation
                    ordered_moves = self.order_moves(board)
                    
                    # Evaluate first few moves quickly
                    best_score = -math.inf if board.turn == chess.WHITE else math.inf
                    for move in ordered_moves[:5]:  # Only check first 5
                        board.push(move)
                        score = self.evaluate_position(board)
                        board.pop()
                        
                        if (board.turn == chess.WHITE and score > best_score) or \
                           (board.turn == chess.BLACK and score < best_score):
                            best_score = score
                            best_move = move
            
            # Final fallback: random move
            if not best_move:
                print("  Using random move as fallback")
                best_move = random.choice(list(board.legal_moves))
            
            # Convert move to string format
            from_sq = chess.square_name(best_move.from_square)
            to_sq = chess.square_name(best_move.to_square)
            promotion = chess.piece_symbol(best_move.promotion).lower() if best_move.promotion else None
            
            elapsed = time.time() - self.start_time if self.start_time else 0
            print(f"✅ Engine move: {from_sq} -> {to_sq} (eval: {eval_score:.1f}, time: {elapsed:.1f}s)")
            
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
                
                move = random.choice(list(board.legal_moves))
                from_sq = chess.square_name(move.from_square)
                to_sq = chess.square_name(move.to_square)
                promotion = chess.piece_symbol(move.promotion).lower() if move.promotion else None
                
                return from_sq, to_sq, promotion
            except:
                return None, None, None


# Test the engine
if __name__ == "__main__":
    print("🧪 Testing Optimized Chess Engine...")
    
    # Test each difficulty level
    for difficulty in range(1, 5):
        print(f"\n{'='*50}")
        print(f"Testing difficulty {difficulty}")
        print('='*50)
        
        engine = StrongChessEngine(difficulty=difficulty)
        
        # Test with starting position
        test_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        start_time = time.time()
        result = engine.get_best_move(test_fen)
        elapsed = time.time() - start_time
        
        if result[0]:
            print(f"✅ Difficulty {difficulty}: {result[0]} -> {result[1]} (time: {elapsed:.1f}s)")
            if elapsed > engine.max_time * 1.1:  # 10% tolerance
                print(f"⚠️  Warning: Slightly over time limit ({elapsed:.1f}s > {engine.max_time}s)")
        else:
            print(f"❌ Difficulty {difficulty} test failed")
