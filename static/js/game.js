$(document).ready(function() {
    console.log('Chess Game Initializing...');
    
    // Game state variables
    let gameState = {
        board: null,
        selectedSquare: null,
        validMoves: [],
        moveHistory: [],
        fenHistory: [], // Store FEN states for undo
        currentFen: 'start',
        gameMode: 'two-player',
        playerSide: 'white',
        difficulty: 3,
        isWhiteTurn: true,
        isGameOver: false,
        boardFlipped: false
    };

    // Mobile optimization functions
    function setupMobileOptimizations() {
        // Check if mobile device
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            console.log('Mobile device detected, optimizing for touch...');
            
            // Add mobile-specific CSS class
            document.body.classList.add('mobile-device');
            
            // Prevent accidental page zoom
            document.addEventListener('touchstart', function(e) {
                if (e.touches.length > 1) {
                    e.preventDefault();
                }
            }, { passive: false });
            
            // Prevent context menu on long press
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;
            });
            
            // Adjust chessboard on orientation change
            window.addEventListener('orientationchange', function() {
                setTimeout(() => {
                    if (gameState.board) {
                        gameState.board.resize();
                    }
                }, 100);
            });
        }
    }

    function optimizeBoardForMobile() {
        if (!/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            return; // Not mobile
        }
        
        // Get viewport dimensions
        const vh = window.innerHeight * 0.01;
        const vw = window.innerWidth * 0.01;
        
        // Calculate optimal board size
        const isPortrait = window.innerHeight > window.innerWidth;
        
        if (isPortrait) {
            // In portrait, use 85% of screen width
            const boardSize = Math.min(vw * 85, 600);
            $('.chessboard-container').css('max-width', boardSize + 'px');
        } else {
            // In landscape, use 70% of screen width
            const boardSize = Math.min(vw * 70, 500);
            $('.chessboard-container').css('max-width', boardSize + 'px');
        }
        
        // Force a resize of the chessboard
        if (gameState.board && typeof gameState.board.resize === 'function') {
            setTimeout(() => {
                gameState.board.resize();
            }, 50);
        }
    }

    // Initialize the chessboard
    function initBoard() {
        console.log('Initializing chessboard...');
        
        // Chessboard configuration
        const boardConfig = {
            draggable: true,
            dropOffBoard: 'snapback',
            position: 'start',
            onDragStart: onDragStart,
            onDrop: onDrop,
            onSnapEnd: onSnapEnd,
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
            orientation: 'white',
            appearSpeed: 200,
            moveSpeed: 200,
            snapbackSpeed: 100,
            snapSpeed: 50
        };
        
        gameState.board = Chessboard('board', boardConfig);
        
        if (gameState.board) {
            console.log('✅ Chessboard initialized successfully');
            setupBoardEvents();
        } else {
            console.error('❌ Chessboard failed to initialize');
        }
    }

    // Setup custom board events for click-to-move
    function setupBoardEvents() {
        const $board = $('#board .board-b72b1');
        
        // Handle square clicks (desktop and mobile)
        $board.off('click').on('click', '.square-55d63', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const square = $(this).data('square');
            console.log('Square clicked:', square);
            
            handleSquareClick(square);
        });
        
        // Handle touch events for mobile
        $board.off('touchstart').on('touchstart', '.square-55d63', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const square = $(this).data('square');
            console.log('Square touched:', square);
            
            handleSquareClick(square);
        });
        
        // Prevent default piece dragging behavior that interferes with clicks
        $board.off('mousedown touchstart', '.piece-417db').on('mousedown touchstart', '.piece-417db', function(e) {
            e.stopPropagation();
        });
    }

    // Handle square click/touch
    function handleSquareClick(square) {
        if (gameState.isGameOver) {
            showMessage('Game is over! Start a new game.');
            return;
        }
        
        // In vs bot mode, check if it's player's turn
        if (gameState.gameMode === 'vs-bot') {
            const playerColor = gameState.playerSide.charAt(0);
            const currentTurnColor = gameState.isWhiteTurn ? 'w' : 'b';
            
            if (playerColor !== currentTurnColor) {
                showMessage("It's the bot's turn!");
                return;
            }
        }
        
        const position = gameState.board.position();
        const piece = position[square];
        
        console.log('Square:', square, 'Piece:', piece);
        
        // If we have a selected square
        if (gameState.selectedSquare) {
            // Clicking same square - deselect
            if (square === gameState.selectedSquare) {
                clearSelection();
                return;
            }
            
            // Check if this is a valid move from selected square
            const isValidMove = gameState.validMoves.some(move => move.to === square);
            
            if (isValidMove) {
                // Find the specific move (for promotion info)
                const move = gameState.validMoves.find(m => m.to === square);
                makeMove(gameState.selectedSquare, square, move ? move.promotion : null);
                return;
            }
            
            // Clicking a new piece of same color - select it
            if (piece) {
                const pieceColor = piece.charAt(0);
                const currentTurnColor = gameState.isWhiteTurn ? 'w' : 'b';
                
                if (pieceColor === currentTurnColor) {
                    selectPiece(square);
                    return;
                }
            }
            
            // Clicking elsewhere - deselect
            clearSelection();
            return;
        }
        
        // No square selected - select this square if it has a piece
        if (piece) {
            const pieceColor = piece.charAt(0);
            const currentTurnColor = gameState.isWhiteTurn ? 'w' : 'b';
            
            if (pieceColor === currentTurnColor) {
                selectPiece(square);
            } else {
                showMessage("It's not your turn!");
            }
        }
    }

    // Select a piece and show its valid moves
    async function selectPiece(square) {
        clearSelection();
        
        gameState.selectedSquare = square;
        console.log('Selected piece at:', square);
        
        // Add selection highlight
        $(`[data-square="${square}"]`).addClass('selected');
        
        // Get valid moves for this piece
        try {
            const moves = await getLegalMoves(square);
            gameState.validMoves = moves;
            
            console.log('Valid moves:', moves);
            
            // Highlight valid moves
            moves.forEach(move => {
                const $targetSquare = $(`[data-square="${move.to}"]`);
                
                // Check if target has a piece (capture)
                const position = gameState.board.position();
                if (position[move.to]) {
                    $targetSquare.addClass('valid-capture');
                } else {
                    $targetSquare.addClass('valid-move');
                }
            });
        } catch (error) {
            console.error('Error getting legal moves:', error);
            clearSelection();
        }
    }

    // Clear selection and highlights
    function clearSelection() {
        gameState.selectedSquare = null;
        gameState.validMoves = [];
        
        // Remove all highlights
        $('.square-55d63').removeClass('selected valid-move valid-capture');
    }

    // Get legal moves from server
    async function getLegalMoves(square) {
        try {
            const response = await fetch('/get_legal_moves', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fen: getCurrentFEN(),
                    square: square
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Convert to array of move objects
            return data.legal_moves.map(move => ({
                from: square,
                to: move,
                promotion: null // Will handle promotion later
            }));
        } catch (error) {
            console.error('Error fetching legal moves:', error);
            return [];
        }
    }

    // Make a move
    async function makeMove(from, to, promotion = null) {
        console.log('Making move:', from, '->', to);
        
        try {
            const response = await fetch('/validate_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fen: getCurrentFEN(),
                    from: from,
                    to: to,
                    promotion: promotion
                })
            });
            
            const data = await response.json();
            
            if (!data.valid) {
                showMessage(data.error || 'Invalid move');
                return false;
            }
            
            // Save current FEN for undo
            gameState.fenHistory.push(getCurrentFEN());
            
            // Update game state
            gameState.currentFen = data.fen;
            gameState.isWhiteTurn = !gameState.isWhiteTurn;
            gameState.isGameOver = data.checkmate || data.stalemate || data.draw;
            
            // Update board
            gameState.board.position(data.fen);
            
            // Clear selection
            clearSelection();
            
            // Update UI
            updateGameStatus(data);
            
            // Add to move history
            const moveNotation = getMoveNotation(from, to);
            gameState.moveHistory.push({
                move: moveNotation,
                color: gameState.isWhiteTurn ? 'black' : 'white'
            });
            updateMoveHistory();
            
            // Update control buttons
            updateControlButtons();
            
            // If game over, show message
            if (gameState.isGameOver) {
                showGameOverMessage(data);
            } else {
                // If vs bot and it's bot's turn, get bot move
                if (gameState.gameMode === 'vs-bot' && 
                    ((gameState.playerSide === 'white' && !gameState.isWhiteTurn) ||
                     (gameState.playerSide === 'black' && gameState.isWhiteTurn))) {
                    setTimeout(getBotMove, 500);
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error making move:', error);
            showMessage('Error making move: ' + error.message);
            return false;
        }
    }

    // Get bot move
    async function getBotMove() {
        if (gameState.isGameOver) return;
        
        showMessage('Bot is thinking...');
        
        try {
            const response = await fetch('/get_bot_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fen: getCurrentFEN(),
                    difficulty: gameState.difficulty
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Save current FEN for undo
            gameState.fenHistory.push(getCurrentFEN());
            
            // Make the bot move
            await makeMove(data.from_square, data.to_square, data.promotion);
            
        } catch (error) {
            console.error('Error getting bot move:', error);
            showMessage('Bot error: ' + error.message);
            
            // Fallback: try to make a random legal move
            makeRandomBotMove();
        }
    }

    // Fallback: make random move for bot
    async function makeRandomBotMove() {
        try {
            const response = await fetch('/get_legal_moves', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fen: getCurrentFEN()
                })
            });
            
            const data = await response.json();
            
            if (data.error || !data.legal_moves || data.legal_moves.length === 0) {
                throw new Error('No legal moves available');
            }
            
            // Pick a random move
            const randomMove = data.legal_moves[Math.floor(Math.random() * data.legal_moves.length)];
            const from = randomMove.substring(0, 2);
            const to = randomMove.substring(2, 4);
            
            await makeMove(from, to);
        } catch (error) {
            console.error('Error making random move:', error);
            showMessage('Bot cannot move');
        }
    }

    // Drag start handler
    function onDragStart(source, piece, position, orientation) {
        if (gameState.isGameOver) return false;
        
        // In vs bot mode, only allow player to drag their pieces
        if (gameState.gameMode === 'vs-bot') {
            const pieceColor = piece.charAt(0);
            const playerColor = gameState.playerSide.charAt(0);
            if (pieceColor !== playerColor) return false;
        }
        
        // Don't allow dragging if it's not your turn
        const pieceColor = piece.charAt(0);
        if ((pieceColor === 'w' && !gameState.isWhiteTurn) ||
            (pieceColor === 'b' && gameState.isWhiteTurn)) {
            return false;
        }
        
        return true;
    }

    // Drop handler
    function onDrop(source, target, piece, newPos, oldPos, orientation) {
        // Clear any existing selection
        clearSelection();
        
        // Validate the move
        makeMove(source, target);
        
        return true;
    }

    // Snap end handler
    function onSnapEnd() {
        gameState.board.position(gameState.currentFen);
    }

    // Get current FEN
    function getCurrentFEN() {
        if (gameState.currentFen === 'start') {
            return 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        }
        return gameState.currentFen;
    }

    // Update game status display
    function updateGameStatus(data) {
        let statusText = `${gameState.isWhiteTurn ? 'White' : 'Black'} to move`;
        
        if (data.checkmate) {
            statusText = `Checkmate! ${gameState.isWhiteTurn ? 'Black' : 'White'} wins!`;
        } else if (data.stalemate) {
            statusText = 'Stalemate! Game drawn.';
        } else if (data.draw) {
            statusText = 'Game drawn.';
        } else if (data.check) {
            statusText = `${gameState.isWhiteTurn ? 'Black' : 'White'} is in check!`;
        }
        
        $('#status').text(statusText);
    }

    // Show game over message
    function showGameOverMessage(data) {
        let message = '';
        
        if (data.checkmate) {
            message = `🎉 Checkmate! ${gameState.isWhiteTurn ? 'Black' : 'White'} wins! 🎉`;
        } else if (data.stalemate) {
            message = '🤝 Stalemate! Game drawn. 🤝';
        } else if (data.draw) {
            message = '🤝 Game drawn. 🤝';
        }
        
        $('#game-over').html(`<h3>Game Over!</h3><p>${message}</p>`).removeClass('hidden');
    }

    // Update move history display
    function updateMoveHistory() {
        const $moveList = $('#move-list');
        $moveList.empty();
        
        for (let i = 0; i < gameState.moveHistory.length; i += 2) {
            const moveNumber = Math.floor(i / 2) + 1;
            const whiteMove = gameState.moveHistory[i];
            const blackMove = gameState.moveHistory[i + 1];
            
            const moveDiv = $('<div>').addClass('move-entry');
            
            if (whiteMove) {
                $('<span>').addClass('move-number').text(`${moveNumber}.`).appendTo(moveDiv);
                $('<span>').addClass('move white-move').text(whiteMove.move).appendTo(moveDiv);
            }
            
            if (blackMove) {
                $('<span>').addClass('move black-move').text(blackMove.move).appendTo(moveDiv);
            }
            
            $moveList.append(moveDiv);
        }
        
        // Scroll to bottom
        $moveList.scrollTop($moveList[0].scrollHeight);
    }

    // Get move notation
    function getMoveNotation(from, to) {
        return `${from}→${to}`;
    }

    // Show message
    function showMessage(message) {
        const $error = $('#error-message');
        $error.text(message).removeClass('hidden');
        
        setTimeout(() => {
            $error.addClass('hidden');
        }, 3000);
    }

    // Update control buttons
    function updateControlButtons() {
        $('#undo-btn').prop('disabled', gameState.fenHistory.length === 0);
    }

    // Initialize game
    function initGame() {
        initBoard();
        setupEventListeners();
        updateGameStatus({});
        updateControlButtons();
    }

    // Setup event listeners for buttons
    function setupEventListeners() {
        // Mode buttons
        $('#two-player-btn').click(() => setGameMode('two-player'));
        $('#vs-bot-btn').click(() => setGameMode('vs-bot'));
        
        // Control buttons
        $('#new-game-btn').click(startNewGame);
        $('#flip-board-btn').click(flipBoard);
        $('#undo-btn').click(undoMove);
        $('#hints-btn').click(toggleHints);
        $('#flip-sides-btn').click(flipPlayerSide);
        
        // Difficulty buttons
        $('.diff-btn').click(function() {
            const level = $(this).data('level');
            setDifficulty(level);
        });
    }

    // Set game mode
    function setGameMode(mode) {
        gameState.gameMode = mode;
        
        // Update UI
        $('#two-player-btn').toggleClass('active', mode === 'two-player');
        $('#vs-bot-btn').toggleClass('active', mode === 'vs-bot');
        
        // Show/hide controls
        $('.side-controls').toggleClass('hidden', mode === 'two-player');
        $('.bot-controls').toggleClass('hidden', mode === 'two-player');
        
        updateSideInfo();
        
        // If vs bot and it's not player's turn, make bot move
        if (mode === 'vs-bot') {
            if ((gameState.playerSide === 'white' && !gameState.isWhiteTurn) ||
                (gameState.playerSide === 'black' && gameState.isWhiteTurn)) {
                setTimeout(getBotMove, 500);
            }
        }
    }

    // Set difficulty
    function setDifficulty(level) {
        gameState.difficulty = level;
        $('.diff-btn').removeClass('active');
        $(`.diff-btn[data-level="${level}"]`).addClass('active');
    }

    // Flip player side
    function flipPlayerSide() {
        gameState.playerSide = gameState.playerSide === 'white' ? 'black' : 'white';
        updateSideInfo();
        
        // If vs bot and it's now bot's turn, make bot move
        if (gameState.gameMode === 'vs-bot') {
            if ((gameState.playerSide === 'white' && !gameState.isWhiteTurn) ||
                (gameState.playerSide === 'black' && gameState.isWhiteTurn)) {
                setTimeout(getBotMove, 500);
            }
        }
    }

    // Update side info
    function updateSideInfo() {
        const sideText = gameState.gameMode === 'vs-bot' 
            ? `You are playing as ${gameState.playerSide.charAt(0).toUpperCase() + gameState.playerSide.slice(1)}`
            : 'Two Player Mode';
        $('#side-info').text(sideText);
    }

    // Start new game
    function startNewGame() {
        gameState.board.position('start');
        gameState.currentFen = 'start';
        gameState.selectedSquare = null;
        gameState.validMoves = [];
        gameState.moveHistory = [];
        gameState.fenHistory = [];
        gameState.isWhiteTurn = true;
        gameState.isGameOver = false;
        
        updateGameStatus({});
        updateMoveHistory();
        clearSelection();
        updateControlButtons();
        $('#game-over').addClass('hidden');
        
        // If vs bot and player is black, make bot move
        if (gameState.gameMode === 'vs-bot' && gameState.playerSide === 'black') {
            setTimeout(getBotMove, 500);
        }
    }

    // Flip board
    function flipBoard() {
        const orientation = gameState.board.orientation();
        gameState.board.flip();
        gameState.boardFlipped = !gameState.boardFlipped;
    }

    // Undo move
    function undoMove() {
        if (gameState.fenHistory.length === 0) {
            showMessage('No moves to undo');
            return;
        }
        
        // Get the last FEN
        const lastFen = gameState.fenHistory.pop();
        gameState.board.position(lastFen);
        gameState.currentFen = lastFen;
        gameState.isWhiteTurn = !gameState.isWhiteTurn;
        gameState.isGameOver = false;
        
        // Remove last move from history
        if (gameState.moveHistory.length > 0) {
            gameState.moveHistory.pop();
        }
        
        // Update UI
        updateGameStatus({});
        updateMoveHistory();
        clearSelection();
        updateControlButtons();
        $('#game-over').addClass('hidden');
        
        showMessage('Move undone');
    }

    // Toggle hints
    function toggleHints() {
        const $hintBtn = $('#hints-btn');
        if ($hintBtn.text().includes('Show')) {
            $hintBtn.html('🔍 Hide Hints');
            showAllLegalMoves();
        } else {
            $hintBtn.html('🔍 Show Hints');
            clearSelection();
        }
    }

    // Show all legal moves
    async function showAllLegalMoves() {
        clearSelection();
        
        try {
            const response = await fetch('/get_legal_moves', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fen: getCurrentFEN()
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Highlight all legal moves
            const position = gameState.board.position();
            data.legal_moves.forEach(move => {
                const from = move.substring(0, 2);
                const to = move.substring(2, 4);
                
                const $targetSquare = $(`[data-square="${to}"]`);
                if (position[to]) {
                    $targetSquare.addClass('valid-capture');
                } else {
                    $targetSquare.addClass('valid-move');
                }
            });
        } catch (error) {
            console.error('Error showing hints:', error);
        }
    }

    // === MAIN INITIALIZATION ===
    
    // Setup mobile optimizations first
    setupMobileOptimizations();
    
    // Call optimizeBoardForMobile on window resize
    $(window).on('resize', optimizeBoardForMobile);
    
    // Initialize the game
    initGame();
    
    // Optimize board for mobile after initialization
    setTimeout(optimizeBoardForMobile, 100);
});