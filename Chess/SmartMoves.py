from chessEngine import Gamestate as gs
piece_score = {"K":0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, "p" : 1, }
CHECKMATE = 1000
STALEMATE = 0

def find_best_move(gs, validMoves):
    turn_multiplier = 1 if gs.white2move else -1
    oppentMinMaxScore = -CHECKMATE
    bestMove = None
    for playerMove in validMoves:
        gs.make_move(playerMove)
        oppoentsMoves = gs.get_valid_moves()
        for oppoentsMove in oppoentsMoves:
            gs.make_move(oppoentsMove)
            if gs.check_mate:
                score = -CHECKMATE
            elif gs.stale_mate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(gs.board)
            if score > oppentMinMaxScore:
                score = oppentMinMaxScore
                bestMove = playerMove
        gs.undo_move()
    return bestMove

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score
