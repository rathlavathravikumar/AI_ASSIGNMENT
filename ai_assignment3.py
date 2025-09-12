

import chess
from chessboard import display
import time

class State:
    def __init__(self, board=None, player=True):
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board
        self.player = player 
    def goalTest(self):
       
        if self.board.is_checkmate():
            return not self.player 
        return None

    def isTerminal(self):
        return self.board.is_game_over()
    def get_ordered_moves(self):
        moves = list(self.board.legal_moves)
        captures = [move for move in moves if self.board.is_capture(move)]
        other_moves = [move for move in moves if not self.board.is_capture(move)]
        return captures + other_moves


    
    
    def moveGen(self):
        children = []
        for move in self.get_ordered_moves():  
            new_board = self.board.copy()
            new_board.push(move)
            children.append(State(new_board, not self.player))
        return children


    def __str__(self):
        return str(self.board)

    def __eq__(self, other):
        return self.board.fen() == other.board.fen() and self.player == other.player

    def __hash__(self):
        return hash((self.board.fen(), self.player))

    def evaluate(self):
        score=0
        piece_values={
            chess.PAWN:1,
            chess.KNIGHT:3,
            chess.BISHOP:3,
            chess.ROOK:5,
            chess.QUEEN:9,
            chess.KING:0
        
        }
        for square,piece in self.board.piece_map().items():
            value=piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score+=value
            else:
                score-=value
        
        center_squares=[chess.D4,chess.E4,chess.D5,chess.E5]
        for sq in center_squares:
            piece=self.board.piece_at(sq)
            if piece and piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    score+=0.1
                else:
                    score-=0.1
        current_turn=self.board.turn
        self.board.turn = chess.WHITE
        white_mobility = self.board.legal_moves.count()
        self.board.turn = chess.BLACK
        black_mobility = self.board.legal_moves.count();
        score+=0.05 *(white_mobility-black_mobility)
        self.board.turn=current_turn
        white_king=self.board.king(chess.WHITE)
        black_king=self.board.king(chess.BLACK)
        attacters=self.board.attackers(chess.BLACK,white_king)
        if attacters:
            score-=0.5*len(attacters)
        attacters=self.board.attackers(chess.WHITE,black_king)
        if attacters:
            score+=0.5*len(attacters);
        white_bishops=0
        black_bishops=0
        for piece in self.board.piece_map().values():
            if piece.piece_type ==chess.BISHOP:
                if piece.color == chess.WHITE:
                    white_bishops +=1
                else:
                    black_bishops+=1
        if white_bishops:
            score+=0.5
        if black_bishops:
            score-=0.5
        if self.board.has_castling_rights(chess.WHITE):
            score+=0.3
        if self.board.has_castling_rights(chess.BLACK):
            score-=0.3
            
        
       
        
        return score
       

        # Step 1: Handle finished games
        if self.board.is_checkmate():
            return -1000 if self.player else 1000  # Current player is mated
        if self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.can_claim_draw():
            return 0

     
        return 0
       


def minimax(state, depth, alpha, beta, maximizingPlayer, maxDepth):
    if state.isTerminal() or depth == maxDepth:
        return state.evaluate(), None

    best_move = None

    if maximizingPlayer: 
        maxEval = float('-inf')
        for child in state.moveGen():
            eval_score, _ = minimax(child, depth + 1, alpha, beta, False, maxDepth)

            if eval_score > maxEval:
                maxEval = eval_score
                best_move = child.board.peek()  

            alpha = max(alpha, eval_score)
            if alpha >= beta:
                break  

        return maxEval, best_move

    else: 
        minEval = float('inf')
        for child in state.moveGen():
            eval_score, _ = minimax(child, depth + 1, alpha, beta, True, maxDepth)

            if eval_score < minEval:
                minEval = eval_score
                best_move = child.board.peek()

            beta = min(beta, eval_score)
            if alpha >= beta:
                break

        return minEval, best_move


def play_game():
    current_state = State(player=True) 
    maxDepth = 3 
    game_board = display.start()  

    print("Artificial Intelligence – Assignment 3")
    print("Simple Chess AI")
    print("You are playing as White (enter moves in UCI format, e.g., e2e4)")

    while not current_state.isTerminal():
        # Update the display
        display.update(current_state.board.fen(), game_board)

        
        if display.check_for_quit():
            break

        if current_state.player:  
            try:
                move_uci = input("Enter your move (e.g., e2e4, g1f3, a7a8q) or 'quit': ")

                if move_uci.lower() == 'quit':
                    break

                move = chess.Move.from_uci(move_uci)

                if move in current_state.board.legal_moves:
                    new_board = current_state.board.copy()
                    new_board.push(move)
                    current_state = State(new_board, False)
                else:
                    print("Invalid move! Try again.")
                    continue
            except ValueError:
                print("Invalid input format! Use UCI format like 'e2e4'.")
                continue
        else:  
            print("AI is thinking...")
            start_time = time.time()
            eval_score, best_move = minimax(current_state, 0, float('-inf'), float('inf'), False, maxDepth)
            end_time = time.time()

            print(f"AI thought for {end_time - start_time:.2f} seconds")

            if best_move:
                new_board = current_state.board.copy()
                new_board.push(best_move)
                current_state = State(new_board, True)
                print(f"AI plays: {best_move.uci()}")
            else:
                # Fallback
                legal_moves = list(current_state.board.legal_moves)
                if legal_moves:
                    move = legal_moves[0]
                    new_board = current_state.board.copy()
                    new_board.push(move)
                    current_state = State(new_board, True)
                    print(f"AI plays (fallback): {move.uci()}")
                else:
                    break

    # Game over
    print("\nGame over!")
    display.update(current_state.board.fen(), game_board)

    if current_state.board.is_checkmate():
        print("Checkmate! " + ("White" if not current_state.player else "Black") + " wins!")
    elif current_state.board.is_stalemate():
        print("Stalemate! It's a draw.")
    elif current_state.board.is_insufficient_material():
        print("Insufficient material! It's a draw.")
    elif current_state.board.can_claim_draw():
        print("Draw by repetition or 50-move rule!")

   
    time.sleep(3)
    display.terminate()


if __name__ == "__main__":
    play_game()
