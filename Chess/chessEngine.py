"""
This class is responsible for storing all the information about the current state of a chess game. Also responsible for
 determing the valid moves at the current state. It will also keep a move log.
"""
import chess


class Gamestate():
    white2move: bool

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.moveFunctions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves,
                              'N': self.get_knight_moves, 'B': self.get_bishop_moves, 'Q': self.get_queen_moves,
                              'K': self.get_king_moves}
        self.white2move = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = ()  # the square where an enpassant capture is possible
        self.current_castle_right = castle_rights(True, True, True, True)
        self.castle_right_log = [castle_rights(self.current_castle_right.wks, self.current_castle_right.wqs,
                                               self.current_castle_right.bks, self.current_castle_right.bqs)]

    def make_move(self, move):
        """Takes a move as parameter and execute it """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move)
        self.white2move = not self.white2move  # swap players
        # update king's position
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.is_pawn_promotion:
            promoted_piece = input("Promote to Q, R, B or K : ")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promoted_piece

        # En passant
        if move.is_enpassant_move:
            self.board[move.startRow][move.endCol] = '--'  # capture the pawn

        # update enpassant possible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassant_possible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.endCol - move.startCol == 2:  # king side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move the rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erase the rook


            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move the rook
                self.board[move.endRow][move.endCol - 2] = '--'  # erase the rook

        # update castling rights - whenever it is a rook or king move
        self.update_castle_right(move)
        self.castle_right_log.append(castle_rights(self.current_castle_right.wks, self.current_castle_right.wqs,
                                                   self.current_castle_right.bks, self.current_castle_right.bqs))

    def undo_move(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.white2move = not self.white2move
            # undo enpassant
            if move.is_enpassant_move:
                self.board[move.startRow][move.startCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassant_possible = (move.endRow, move.endCol)
            # undo 2 squares pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassant_possible = ()

            # undo castling rights
            self.castle_right_log.pop()
            self.current_castle_right = self.castle_right_log[-1]

            # undo castle move
            if move.is_castle_move:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"

                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    def update_castle_right(self, move):
        ''' update the castle right given the move'''
        if move.pieceMoved == 'wk':
            self.current_castle_right.wks = False
            self.current_castle_right.wqs = False
        elif move.pieceMoved == 'bk':
            self.current_castle_right.bks = False
            self.current_castle_right.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.current_castle_right.wqs = False
                elif move.startCol == 7:  # right rook
                    self.current_castle_right.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.current_castle_right.bqs = False
                elif move.startCol == 7:  # righ rook
                    self.current_castle_right.bks = False
        # if rook has been captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.current_castle_right.wqs = False
                elif move.endCol == 7:
                    self.current_castle_right.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.current_castle_right.bqs = False
                elif move.endCol == 7:
                    self.current_castle_right.bks = False

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.white2move = not self.white2move  # switch to opponent's point of view
        opponents_moves = self.possible_moves()
        self.white2move = not self.white2move
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col: # square is under attack

                print(
                    f"Move from {move.startRow}, {move.startCol} to {move.endRow}, {move.endCol} is considered as an attack.")
                return True
        return False

    def get_valid_moves(self):
        """
        all moves considering checks
        """
        temp_castle_rights = castle_rights(self.current_castle_right.wks, self.current_castle_right.wqs,
                                           self.current_castle_right.bks, self.current_castle_right.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.white2move:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            print("check!")
            if len(self.checks) == 1:  # only check by 1 piece
                moves = self.possible_moves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # identify the enemy piece that is checking your king
                validSquares = []  # sqaures that pieces can move to , if knight must capture knight or move king, else see if can be block by other pieces
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                        kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check direction
                        validSquares.append(validSquare)
                        print(validSquare, checkRow, checkCol)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1,
                               -1):  # go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king so it must be block or capture
                        if not (moves[i].endRow,
                                moves[i].endCol) in validSquares:  # move doesnt block check or capture piece
                            moves.remove(moves[i])
            else:  # double check so king has to move
                self.get_king_moves(kingRow, kingCol, moves)
        else:  # not in check
            moves = self.possible_moves()
            if self.white2move:
                self.get_castle_move(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.get_castle_move(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        if len(moves) == 0:
            if self.inCheck:
                self.check_mate = True
                print('Check Mate !')
            else:
                self.stale_mate = True
        self.current_castle_right = temp_castle_rights
        return moves

    def possible_moves(self):
        """
        all moves without considering checks
        """
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in a given row
                turn = self.board[r][c][0]  # color
                if (turn == 'w' and self.white2move) or (turn == 'b' and not self.white2move):
                    piece = self.board[r][c][1]  # piece type
                    self.moveFunctions[piece](r, c, moves)  # call the appropriate move function based on piece
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white2move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKingLocation[0]
            start_col = self.blackKingLocation[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def get_pawn_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white2move:
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # capture
            if c - 1 >= 0:  # capture to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_enpassant_move=True))

            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))
        else:
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # capture to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))
            if c + 1 <= 7:  # capture to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][
                    1] != 'Q':  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = "b" if self.white2move else "w"
        for d in directions:
            for i in range(1, 8):  # rooks can move up to 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                    else:  # out of the board
                        break

    def get_knight_moves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (1, -2), (1, 2), (2, 1), (-1, 2), (2, -1))
        allyColor = "w" if self.white2move else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def get_bishop_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # bl, br,tl,tr
        enemyColor = "b" if self.white2move else "w"
        for d in directions:
            for i in range(1, 8):  # rooks can move up to 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol < 8 and 0 <= endRow < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # out of the board
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.white2move else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def get_castle_move(self, r, c, moves):
        '''
        generate all valid castle moves for the king at (r, c) and add them to the list of moves
        '''
        in_checks, pins, check = self.checkForPinsAndChecks()
        if in_checks:
            return

        if (self.white2move and self.current_castle_right.wks) or (
                not self.white2move and self.current_castle_right.bks):
            self.get_king_side_castle_move(r, c, moves)
        if (self.white2move and self.current_castle_right.bqs) or (
                not self.white2move and self.current_castle_right.wqs):
            self.get_queen_side_castle_move(r, c, moves)

    def get_king_side_castle_move(self, r, c, moves):

        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == "--":
            print("1")
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                print('2')
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_move(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == "--" and self.board[r][c - 3] == '--':
            print('10')
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                print('11')
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class castle_rights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranks2Rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows2ranks = {v: k for k, v in ranks2Rows.items()}
    files2Cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols2files = {v: k for k, v in files2Cols.items()}

    def __init__(self, startSq, endSq, board, is_enpassant_move=False, is_castle_move=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        # pawn promotion
        self.is_pawn_promotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.is_pawn_promotion = True

        # En passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.pieceCaptured = "wp" if self.pieceMoved == 'bp' else 'bp'

        # castle move
        self.is_castle_move = is_castle_move

    def __eq__(self, other):
        """
        overwrite the equal method
        """
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.cols2files[c] + self.rows2ranks[r]
