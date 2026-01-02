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
        
        # Piece values
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece-square tables (middlegame)
        self.pawn_table = [
            0,   0,   0,   0,   0,   0,  0,   0,
            98, 134,  61,  95,  68, 126, 34, -11,
            -6,   7,  26,  31,  65,  56, 25, -20,
            -14,  13,   6,  21,  23,  12, 17, -23,
            -27,  -2,  -5,  12,  17,   6, 10, -25,
            -26,  -4,  -4, -10,   3,   3, 33, -12,
            -35,  -1, -20, -23, -15,  24, 38, -22,
            0,   0,   0,   0,   0,   0,  0,   0
        ]
        
        self.knight_table = [
            -167, -89, -34, -49,  61, -97, -15, -107,
            -73, -41,  72,  36,  23,  62,   7,  -17,
            -47,  60,  37,  65,  84, 129,  73,   44,
            -9,  17,  19,  53,  37,  69,  18,   22,
            -13,   4,  16,  13,  28,  19,  21,   -8,
            -23,  -9,  12,  10,  19,  17,  25,  -16,
            -29, -53, -12,  -3,  -1,  18, -14,  -19,
            -105, -21, -58, -33, -17, -28, -19,  -23
        ]
        
        self.bishop_table = [
            -29,   4, -82, -37, -25, -42,   7,  -8,
            -26,  16, -18, -13,  30,  59,  18, -47,
            -16,  37,  43,  40,  35,  50,  37,  -2,
            -4,   5,  19,  50,  37,  37,   7,  -2,
            -6,  13,  13,  26,  34,  12,  10,   4,
            0,  15,  15,  15,  14,  27,  18,  10,
            4,  15,  16,   0,   7,  21,  33,   1,
            -33,  -3, -14, -21, -13, -12, -39, -21
        ]
        
        self.rook_table = [
            32,  42,  32,  51, 63,  9,  31,  43,
            27,  32,  58,  62, 80, 67,  26,  44,
            -5,  19,  26,  36, 17, 45,  61,  16,
            -24, -11,   7,  26, 24, 35,  -8, -20,
            -36, -26, -12,  -1,  9, -7,   6, -23,
            -45, -25, -16, -17,  3,  0,  -5, -33,
            -44, -16, -20,  -9, -1, 11,  -6, -71,
            -19, -13,   1,  17, 16,  7, -37, -26
        ]
        
        self.queen_table = [
            -28,   0,  29,  12,  59,  44,  43,  45,
            -24, -39,  -5,   1, -16,  57,  28,  54,
            -13, -17,   7,   8,  29,  56,  47,  57,
            -27, -27, -16, -16,  -1,  17,  -2,   1,
            -9, -26,  -9, -10,  -2,  -4,   3,  -3,
            -14,   2, -11,  -2,  -5,   2,  14,   5,
            -35,  -8,  11,   2,   8,  15,  -3,   1,
            -1, -18,  -9,  10, -15, -25, -31, -50
        ]
        
        self.king_middle_table = [
            -65,  23,  16, -15, -56, -34,   2,  13,
            29,  -1, -20,  -7,  -8,  -4, -38, -29,
            -9,  24,   2, -16, -20,   6,  22, -22,
            -17, -20, -12, -27, -30, -25, -14, -36,
            -49,  -1, -27, -39, -46, -44, -33, -51,
            -14, -14, -22, -46, -44, -30, -15, -27,
            1,   7,  -8, -64, -43, -16,   9,   8,
            -15,  36,  12, -54,   8, -28,  24,  14
        ]
        
        self.king_end_table = [
            -74, -35, -18, -18, -11,  15,   4, -17,
            -12,  17,  14,  17,  17,  38,  23,  11,
            10,  17,  23,  15,  20,  45,  44,  13,
            -8,  22,  24,  27,  26,  33,  26,   3,
            -18,  -4,  21,  24,  27,  23,   9, -11,
            -19,  -3,  11,  21,  23,  16,   7,  -9,
            -27, -11,   4,  13,  14,   4,  -5, -17,
            -53, -34, -21, -11, -28, -14, -24, -43
        ]
        
        # Set search depth based on difficulty
        self.max_depth = difficulty + 1  # 3-5 ply
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Evaluate the board position"""
        if board.is_checkmate():
            return -100000 if board.turn else 100000
        
        if board.is_stalemate():
            return 0
        
        score = 0
        
        # Material evaluation
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                
                # Add position value
                position_value = self.get_position_value(piece, square, board)
                value += position_value
                
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        # Mobility (number of legal moves)
        mobility = len(list(board.legal_moves))
        if board.turn == chess.WHITE:
            score += mobility * 0.1
        else:
            score -= mobility * 0.1
        
        # Pawn structure
        score += self.evaluate_pawn_structure(board)
        
        # King safety
        score += self.evaluate_king_safety(board)
        
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
        
        return table[idx] * 0.1  # Scale down
    
    def count_material(self, board: chess.Board) -> int:
        """Count total material on board"""
        total = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.KING:
                total += self.piece_values[piece.piece_type]
        return total
    
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
                score -= (white_pawns - 1) * 10
            if black_pawns > 1:
                score += (black_pawns - 1) * 10
        
        return score
    
    def evaluate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety"""
        score = 0
        
        # White king
        white_king = board.king(chess.WHITE)
        if white_king:
            # Penalize if king is not castled in middle game
            if white_king in [chess.E1, chess.D1, chess.F1] and board.fullmove_number < 20:
                score -= 30
            
            # Bonus for castled king
            if white_king in [chess.G1, chess.C1]:  # Castled
                score += 20
        
        # Black king
        black_king = board.king(chess.BLACK)
        if black_king:
            if black_king in [chess.E8, chess.D8, chess.F8] and board.fullmove_number < 20:
                score += 30
            
            if black_king in [chess.G8, chess.C8]:
                score -= 20
        
        return score
    
    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax with alpha-beta pruning"""
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
        
        if maximizing:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def order_moves(self, board: chess.Board) -> List[chess.Move]:
        """Order moves for better alpha-beta pruning"""
        moves = list(board.legal_moves)
        
        def move_score(move: chess.Move) -> int:
            score = 0
            
            # Captures get high priority
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += self.piece_values.get(captured.piece_type, 0)
            
            # Promotions are good
            if move.promotion:
                score += 900
            
            # Checks
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()
            
            # Center control
            center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
            if move.to_square in center_squares:
                score += 20
            
            return score
        
        moves.sort(key=move_score, reverse=True)
        return moves
    
    def get_best_move(self, fen: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get the best move for given position"""
        try:
            board = chess.Board(fen)
            
            if board.is_game_over():
                return None, None, None
            
            best_move = None
            best_value = -math.inf if board.turn == chess.WHITE else math.inf
            
            # Order moves for better pruning
            ordered_moves = self.order_moves(board)
            
            alpha = -math.inf
            beta = math.inf
            
            print(f"🤖 Engine thinking (depth: {self.max_depth}, difficulty: {self.difficulty})...")
            
            for move in ordered_moves:
                board.push(move)
                
                # Adjust search depth based on position complexity
                depth = self.max_depth
                if len(list(board.legal_moves)) > 30:
                    depth = max(2, depth - 1)
                
                eval = self.minimax(board, depth - 1, alpha, beta, board.turn == chess.WHITE)
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
                
                print(f"✅ Engine move: {from_sq} -> {to_sq} (eval: {best_value:.1f})")
                return from_sq, to_sq, promotion
            
            # Fallback: random move
            print("⚠️ No best move found, using random move")
            import random
            move = random.choice(list(board.legal_moves))
            from_sq = chess.square_name(move.from_square)
            to_sq = chess.square_name(move.to_square)
            promotion = chess.piece_symbol(move.promotion).lower() if move.promotion else None
            
            return from_sq, to_sq, promotion
            
        except Exception as e:
            print(f"❌ Engine error: {e}")
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