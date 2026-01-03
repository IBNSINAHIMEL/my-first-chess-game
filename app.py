from flask import Flask, render_template, jsonify, request
import chess
import os  # Required for environment variables
from strong_engine import StrongChessEngine

app = Flask(__name__)

# Initialize strong engine
chess_engine = StrongChessEngine(difficulty=3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_bot_move', methods=['POST'])
def get_bot_move():
    data = request.json
    fen = data.get('fen')
    difficulty = data.get('difficulty', 3)
    
    try:
        # Update engine difficulty - use update_depth() method
        chess_engine.difficulty = difficulty
        chess_engine.update_depth()  # This sets all search parameters correctly
        
        # Get best move
        from_sq, to_sq, promotion = chess_engine.get_best_move(fen)
        
        if from_sq and to_sq:
            return jsonify({
                'from_square': from_sq,
                'to_square': to_sq,
                'promotion': promotion
            })
        else:
            # Simple fallback
            board = chess.Board(fen)
            import random
            if board.is_game_over():
                return jsonify({'error': 'Game is over'}), 400
            
            move = random.choice(list(board.legal_moves))
            return jsonify({
                'from_square': chess.square_name(move.from_square),
                'to_square': chess.square_name(move.to_square),
                'promotion': chess.piece_symbol(move.promotion).lower() if move.promotion else None
            })
            
    except Exception as e:
        print(f"Error in get_bot_move: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/get_legal_moves', methods=['POST'])
def get_legal_moves():
    data = request.json
    fen = data.get('fen')
    square = data.get('square')
    
    try:
        board = chess.Board(fen)
        moves = []
        
        if square:
            from_square = chess.parse_square(square)
            for move in board.legal_moves:
                if move.from_square == from_square:
                    moves.append(chess.square_name(move.to_square))
        else:
            for move in board.legal_moves:
                moves.append(chess.square_name(move.to_square))
        
        return jsonify({'legal_moves': moves})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/validate_move', methods=['POST'])
def validate_move():
    data = request.json
    fen = data.get('fen')
    from_sq = data.get('from')
    to_sq = data.get('to')
    promotion = data.get('promotion')
    
    try:
        board = chess.Board(fen)
        
        # Check if this is a pawn promotion move
        piece = board.piece_at(chess.parse_square(from_sq))
        is_pawn = piece and piece.piece_type == chess.PAWN
        target_rank = chess.square_rank(chess.parse_square(to_sq))
        
        # Determine if move requires promotion
        if is_pawn and ((piece.color == chess.WHITE and target_rank == 7) or 
                       (piece.color == chess.BLACK and target_rank == 0)):
            # If promotion is not specified, we need to ask for it
            if not promotion:
                return jsonify({
                    'valid': False, 
                    'requires_promotion': True,
                    'error': 'Pawn promotion required'
                })
        
        # Create the move
        move_uci = f"{from_sq}{to_sq}{promotion if promotion else ''}"
        move = chess.Move.from_uci(move_uci)
        
        if move in board.legal_moves:
            board.push(move)
            return jsonify({
                'valid': True,
                'fen': board.fen(),
                'check': board.is_check(),
                'checkmate': board.is_checkmate(),
                'stalemate': board.is_stalemate(),
                'draw': board.is_game_over() and not board.is_checkmate(),
                'promotion_made': promotion if promotion else None
            })
        else:
            return jsonify({'valid': False, 'error': 'Illegal move'})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Modern Chess Game Server...")
    print("📱 Game optimized for mobile and desktop")
    
    # Test the engine
    test_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    result = chess_engine.get_best_move(test_fen)
    if result[0]:
        print(f"✅ Engine ready: {result[0]} -> {result[1]}")
    else:
        print("⚠️ Engine test failed")
    
    # Get port from environment variable (Fly.io provides PORT)
    port = int(os.environ.get("PORT", 8080))
    
    # Disable debug mode for production
    app.run(debug=False, host='0.0.0.0', port=port)
