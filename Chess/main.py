"""
Main file use for handling user input and displayimng the current GameState object
"""

import pygame as p
from Chess import chessEngine
#from Chess import SmartMoves as sm

width = height = 512
Dimension = 8
square_size = width // Dimension
max_fps = 15
images = {}

'''
Initialize a global dictionary of images. Call exactly once in the main
'''
def load_images():
    pieces = ['wp','wR','wN','wB',"wK","wQ","bp","bB","bN","bK","bQ","bR"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (square_size, square_size))
        # we can access an image by calling images['wp']

'''
main driver for our code. This will handle user input and updating the graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = chessEngine.Gamestate()
    validMoves = gs.get_valid_moves()
    move_made = False # flag variable for when a move is made
    animate = False
    load_images()
    running = True
    sq_selected = () # no square is selected initially, keep tract of the last click of the user 'tuple: (row, col)'
    player_clicks = [] # keep tract of player clicks (two tuples: [(6,4),(4,4)]
    gameOver = False
    #player1 = True # if human player is playing white this will be True. If AI is playing then false
    #player2 = False # if human player is playing black this will be True. If AI is playing then false
    while running:
        #human_turn = (gs.white2move and player1) or (not gs.white2move and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse event handles
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0]//square_size
                    row = location[1]//square_size
                    if sq_selected == (row, col): # user click same square twice then undo
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) # append both first and second clicks
                    if len(player_clicks) == 2: # after 2nd click
                        move = chessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move ==  validMoves[i]:
                                gs.make_move(validMoves[i])
                                move_made = True
                                animate = True
                                sq_selected = () # reset user clicks
                                player_clicks = []
                            if not move_made:
                                player_clicks = [sq_selected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when z is pressed
                    gs.undo_move()
                    animate = False
                    move_made = True

                if e.key == p.K_r: # reset the board if 'r' is pressed
                    gs = chessEngine.Gamestate()
                    validMoves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
        # if not gameOver and not human_turn:
        #     ai_move = sm.find_best_move(gs, validMoves)
        #     gs.make_move(ai_move)
        #     move_made = True
            animate = True

        if move_made:
            animateMove(gs.movelog[-1], screen,gs.board,clock)
            validMoves = gs.get_valid_moves()
            move_made = False
            animate = False
        drawGameState(screen, gs, validMoves, sq_selected)
        if gs.check_mate:
            gameOver = True
            if gs.white2move:
                drawText(screen, 'Black wins by Checkmate')
            else:
                drawText(screen, 'White wins by Checkmate')
        elif gs.stale_mate:
            gameOver = True
            drawText(screen, 'stalemate')
        clock.tick(max_fps)
        p.display.flip()

def highlight_squares(screen, gs, validMoves, sq_selected):
    '''
    highligh move sleected and piece selected
    '''
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white2move else 'b'):  # sqSelected is a piece that can be moved
            s = p.Surface((square_size, square_size))
            s.set_alpha(100)  # transparency value -> 0 transparent, 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * square_size, r * square_size))

            # Place dots on squares of valid moves from the selected square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (square_size*move.endCol, square_size*move.endRow))



def drawGameState(screen, gs, validMoves, sq_selected):
    '''
    responsible for all graphics within a current game state
    '''
    drawBoard(screen)
    highlight_squares(screen, gs, validMoves, sq_selected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    '''
    draw the squares of the board
    '''
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(Dimension):
        for c in range(Dimension):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*square_size,r*square_size,square_size,square_size))



def drawPieces(screen, board):
    '''
    draw the pieces on the board
    '''
    for row in range(Dimension):
        for c in range(Dimension):
            piece = board[row][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*square_size, row * square_size, square_size, square_size))

def animateMove(move, screen, board, clock):
    '''
    animate the move
    '''
    global colors

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 5 # frames to move one squares
    frameCount = (abs(dR) + abs(dC))*framePerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*square_size, move.endRow*square_size, square_size, square_size)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        screen.blit(images[move.pieceMoved], p.Rect(c*square_size, r*square_size, square_size, square_size))
        p.display.flip()
        clock.tick(60)


def drawText(screen, txt):
    font = p.font.SysFont('Helvitca', 32,True, False)
    textObject = font.render(txt, 0, p.Color('Gray'))
    textlocation = p.Rect(0,0, width, height).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
    screen.blit(textObject, textlocation)
    textObject = font.render(txt, 0, p.Color('Black'))
    screen.blit(textObject, textlocation)

if __name__ == '__main__':
    main()