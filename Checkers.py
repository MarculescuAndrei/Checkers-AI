
import time
import keyboard
import pygame
from copy import deepcopy


WIDTH, HEIGHT = 800, 800
ROWS, COL = 8, 8
PATRAT = WIDTH // COL


ALB = (255, 255, 255)
NEGRU = (0, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128,128,128)

CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (44, 25))

##########################################

class Piece:
    PADDING = 15
    OUTLINE = 4

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0; self.y = 0
        self.calcPosition()


    def calcPosition(self):
        self.x = PATRAT * self.col + PATRAT // 2
        self.y = PATRAT * self.row + PATRAT // 2

    def makeKing(self):
        self.king = True


    def drawPiece(self, win, outlinecolor):
        radius = PATRAT // 2 - self.PADDING
        pygame.draw.circle(win, outlinecolor, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def commitMove(self, row, col):
        self.row = row
        self.col = col
        self.calcPosition()


class Board:
    def __init__(self):
        self.gameBoard = []
        self.alb_ramase = self.negre_ramase = 12
        self.alb_regi = self.negre_regi = 0
        self.createBoard()

   
    def drawSquares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COL, 2):
                pygame.draw.rect(win, ALB, (row * PATRAT, col * PATRAT, PATRAT, PATRAT))

    

    def evaluateState(self):
        return self.negre_ramase - self.alb_ramase + (self.negre_regi * 0.4 - self.alb_regi * 0.4)

  
    def getAllPieces(self, color):
        pieces = []
        for row in self.gameBoard:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces


    def move(self, piece, row, col):
        self.gameBoard[piece.row][piece.col], self.gameBoard[row][col] = self.gameBoard[row][col], self.gameBoard[piece.row][piece.col]
        piece.commitMove(row, col)

        if row == ROWS - 1 or row == 0:
            piece.makeKing()
            if piece.color == NEGRU:
                self.negre_regi += 1
            else:
                self.alb_regi += 1


    def getPiece(self, row, col):
        return self.gameBoard[row][col]


    def createBoard(self):
        for row in range(ROWS):
            self.gameBoard.append([])
            for col in range(COL):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.gameBoard[row].append(Piece(row, col, NEGRU))
                    elif row > 4:
                        self.gameBoard[row].append(Piece(row, col, ALB))
                    else:
                        self.gameBoard[row].append(0)
                else:
                    self.gameBoard[row].append(0)


    def findObligations(self, color):

        obligatedPieces = []

        for r in range(ROWS):
            for c in range(COL):
                ok = False
                if self.gameBoard[r][c] != 0 and self.gameBoard[r][c].color == color:
                    if color == ALB or self.gameBoard[r][c].king:
                        if c-2 >= 0 and r-2 >= 0 and self.gameBoard[r - 1][c - 1] != 0 and self.gameBoard[r - 1][c - 1].color != color and self.gameBoard[r - 2][c - 2] == 0:
                            ok = True
                        if c+2 <= COL-1 and r-2 >= 0 and self.gameBoard[r - 1][c + 1] != 0 and self.gameBoard[r - 1][c + 1].color != color and self.gameBoard[r - 2][c + 2] == 0:
                            ok = True

                    if color == NEGRU or self.gameBoard[r][c].king:
                        if c-2 >= 0 and r+2 <= ROWS-1 and self.gameBoard[r + 1][c - 1] != 0 and self.gameBoard[r + 1][c - 1].color != color and self.gameBoard[r + 2][c - 2] == 0:
                            ok = True
                        if c+2 <= COL-1 and r+2 <= ROWS-1 and self.gameBoard[r + 1][c + 1] != 0 and self.gameBoard[r + 1][c + 1].color != color and self.gameBoard[r + 2][c + 2] == 0:
                            ok = True
                if ok == True:

                    obligatedPieces.append(self.gameBoard[r][c])
        return obligatedPieces

  
    def drawPieces(self, win, turn):
        self.drawSquares(win)

        for row in range(ROWS):
            for col in range(COL):

                piece = self.gameBoard[row][col]
                if piece != 0 and piece.color == turn and piece in self.findObligations(turn):
                    piece.drawPiece(win, (0, 255, 0))
                elif piece != 0 and piece.color == turn:
                    piece.drawPiece(win, (255, 0, 0))
                elif piece !=0:
                    piece.drawPiece(win, (129, 129, 129))


    def removePieces(self, pieces):
        for piece in pieces:
            self.gameBoard[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == ALB:
                    self.alb_ramase -= 1
                else:
                    self.negre_ramase -= 1


    def printBoard(self):
        print('------------------------------')
        for r in range(ROWS):
            rowToPrint = ''
            for c in range(COL):
                if self.gameBoard[r][c] != 0 and self.gameBoard[r][c].color == NEGRU:
                    rowToPrint = rowToPrint + ' N '
                elif self.gameBoard[r][c] != 0 and self.gameBoard[r][c].color == ALB:
                    rowToPrint = rowToPrint + ' A '
                else:
                    rowToPrint = rowToPrint + ' 0 '
            print(rowToPrint)

  
    def checkForWinner(self):
        if self.alb_ramase <= 0:
            return NEGRU
        elif self.negre_ramase <= 0:
            return ALB
        return None

    def getValidMoves(self, piesa):
        moves = {}
        cm = piesa.col - 1; cp = piesa.col + 1
        rm = piesa.row - 1; rp = piesa.row + 1
        obligations = self.findObligations(piesa.color)


        if len(obligations) == 0:

            if rm >= 0 and cp < COL:
                if (piesa.color == ALB or piesa.king) and self.gameBoard[rm][cp] == 0:
                    moves[(piesa.row - 1, piesa.col + 1)] = []
            if rm >= 0 and cm >= 0:
                if (piesa.color == ALB or piesa.king) and self.gameBoard[rm][cm] == 0:
                    moves[(piesa.row - 1, piesa.col - 1)] = []
            if rp < ROWS and cp < COL:
                if (piesa.color == NEGRU or piesa.king) and self.gameBoard[rp][cp] == 0:
                    moves[(piesa.row + 1, piesa.col + 1)] = []
            if rp < ROWS and cm >= 0:
                if (piesa.color == NEGRU or piesa.king) and self.gameBoard[rp][cm] == 0:
                    moves[(piesa.row + 1, piesa.col - 1)] = []
            return moves

        elif piesa in self.findObligations(piesa.color):

            if piesa.color == ALB:
                if piesa.king:

                    moves.update(self.obligatiiAlb(piesa.row, piesa.col, ALB))
                    moves.update(self.obligatiiNegru(piesa.row, piesa.col, ALB))
                else:
                    moves.update(self.obligatiiAlb(piesa.row, piesa.col, ALB))

            if piesa.color == NEGRU:
                if piesa.king:
                    moves.update(self.obligatiiAlb(piesa.row, piesa.col, NEGRU))
                    moves.update(self.obligatiiNegru(piesa.row, piesa.col, NEGRU))
                else:
                    moves.update(self.obligatiiNegru(piesa.row, piesa.col, NEGRU))
        return moves

    def obligatiiAlb(self, r, c, color, skips=[]):
        moves = {}

        

        if r-2 >= 0 and c-2 >= 0 and self.gameBoard[r - 1][c - 1] != 0 :
            if (self.gameBoard[r - 1][c - 1].color != color and self.gameBoard[r - 2][c - 2] == 0):
                moves[(r-2, c-2)] = [self.gameBoard[r - 1][c - 1]] + skips
                skips = skips + [self.gameBoard[r - 1][c - 1]]
                moves.update(self.obligatiiAlb(r - 2, c - 2, color, skips))

        if r-2 >= 0 and c+2 <= COL-1 and self.gameBoard[r - 1][c + 1] !=0:
            if (self.gameBoard[r - 1][c + 1].color != color and self.gameBoard[r - 2][c + 2] == 0):

                moves[(r-2, c+2)] = [self.gameBoard[r - 1][c + 1]] + skips
                skips = skips + [self.gameBoard[r - 1][c + 1]]
                moves.update(self.obligatiiAlb(r - 2, c + 2, color, skips))
        return moves


    def obligatiiNegru(self, r, c, color, skips=[]):
        moves = {}

        if r+2 <= ROWS-1 and c-2 >= 0 and self.gameBoard[r + 1][c - 1] != 0:
            if (self.gameBoard[r + 1][c - 1].color != color and self.gameBoard[r + 2][c - 2] == 0):
                moves[(r+2, c-2)] = [self.gameBoard[r + 1][c - 1]] + skips
                skips = skips + [self.gameBoard[r + 1][c - 1]]
                moves.update(self.obligatiiNegru(r + 2, c - 2, color, skips))

        if r+2 <= ROWS-1 and c+2 <= COL-1 and self.gameBoard[r + 1][c + 1] !=0:
            if (self.gameBoard[r + 1][c + 1].color != color and self.gameBoard[r + 2][c + 2] == 0):

                moves[(r+2, c+2)] = [self.gameBoard[r + 1][c + 1]] + skips
                skips = skips + [self.gameBoard[r + 1][c + 1]]
                moves.update(self.obligatiiNegru(r + 2, c + 2, color, skips))

        return moves


class Game:

    def __init__(self, win):
        self.selected = None
        self.gameBoard = Board()
        self.turn = NEGRU
        self.validMoves = {}
        self.win = win

    def updateGame(self):
        self.gameBoard.drawPieces(self.win, self.turn)
        self.drawValidMoves(self.validMoves)
        pygame.display.update()

    def getTurn(self):
        return self.turn

    def getWinner(self):
        return self.gameBoard.checkForWinner()

    def select(self, row, col):
        if self.selected:
            result = self.makeMove(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.gameBoard.getPiece(row, col)

        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.validMoves = self.gameBoard.getValidMoves(piece)
            return True

        return False

    def makeMove(self, row, col):

        piece = self.gameBoard.getPiece(row, col)
        if self.selected and piece == 0 and (row, col) in self.validMoves:
            self.gameBoard.move(self.selected, row, col)
            skipped = self.validMoves[(row, col)]
            if skipped:
                self.gameBoard.removePieces(skipped)
            self.changeTurn()
        else:
            return False
        return True


    def drawValidMoves(self, moves):
        for move in moves:
            r, c = move
            pygame.draw.circle(self.win, BLUE, (c * PATRAT + PATRAT // 2, r * PATRAT + PATRAT // 2), 17)


    def changeTurn(self):
        self.validMoves = {}
        if self.turn == ALB:
            self.turn = NEGRU
        else:
            self.turn = ALB
        self.gameBoard.printBoard()

    def getBoard(self):
        return self.gameBoard


    def aiMove(self, board):
        self.gameBoard = board
        self.changeTurn()



def minimax(position, depth, max_player, game):
    if depth == 0 or position.checkForWinner() != None:
        return position.evaluateState(), position


    if max_player:
        maxEval = float('-inf')
        bestMove = None
        for move in getAllMoves(position, NEGRU, game):
            evaluation = minimax(move, depth - 1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                bestMove = move

        return maxEval, bestMove
    else:
        minEval = float('inf')
        bestMove = None
        for move in getAllMoves(position, ALB, game):
            evaluation = minimax(move, depth - 1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                bestMove = move

        return minEval, bestMove


def alpha_beta(alpha, beta, position, depth, max_player, game):

    if depth == 0 or position.checkForWinner() != None:
        return position.evaluateState(), position

    if alpha > beta:
        return position.evaluateState(), position

    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in getAllMoves(position, NEGRU, game):
            evaluation = alpha_beta(alpha, beta, move, depth - 1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move

            if alpha < position.evaluateState():
                alpha = position.evaluateState()
                if alpha >= beta:
                    break

        return maxEval, best_move

    else:
        minEval = float('inf')
        best_move = None
        for move in getAllMoves(position, ALB, game):
            evaluation = alpha_beta(alpha, beta, move, depth - 1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move

            if beta > position.evaluateState():
                beta = position.evaluateState()
                if alpha >= beta:
                    break

        return minEval, best_move


def simulateMove(piece, move, board, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.removePieces(skip)

    return board


def getAllMoves(board, color, game):
    moves = []
    for piece in board.getAllPieces(color):
        valid_moves = board.getValidMoves(piece)
        for move, skip in valid_moves.items():
            temp_board = deepcopy(board)
            temp_piece = temp_board.getPiece(piece.row, piece.col)
            new_board = simulateMove(temp_piece, move, temp_board, skip)
            moves.append(new_board)
    return moves


FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Marculescu Andrei Dame')
pygame.font.init()
font = pygame.font.SysFont('Corbel', 30)
bigfont = pygame.font.SysFont('Corbel', 50)


def getRowColMouse(pos):
    x, y = pos
    row = y // PATRAT
    col = x // PATRAT
    return row, col



def main():

    globalstart = time.time()

    global aiend
    MENU = pygame.display.set_mode((800, 800))
    playbutton = pygame.Rect(100, 100, 250, 50); pvpbutton = pygame.Rect(100, 200, 150, 50)
    pvaibutton = pygame.Rect(100, 270, 150, 50); difbutton1 = pygame.Rect(100, 380, 50, 50)
    difbutton2 = pygame.Rect(160, 380, 50, 50); difbutton3 = pygame.Rect(220, 380, 50, 50)
    difbutton4 = pygame.Rect(280, 380, 50, 50)
    minimaxbutton = pygame.Rect(100, 480, 150, 50); alphabetabutton = pygame.Rect(100, 550, 150, 50)

    MENU.fill((60, 25, 60))
    pygame.draw.rect(MENU, [255, 0, 0], playbutton); pygame.draw.rect(MENU, [255, 0, 0], pvpbutton)
    pygame.draw.rect(MENU, [255, 0, 0], pvaibutton); pygame.draw.rect(MENU, [255, 0, 0], difbutton1)
    pygame.draw.rect(MENU, [255, 0, 0], difbutton2); pygame.draw.rect(MENU, [255, 0, 0], difbutton3)
    pygame.draw.rect(MENU, [255, 0, 0], difbutton4); pygame.draw.rect(MENU, [255, 0, 0], minimaxbutton)
    pygame.draw.rect(MENU, [255, 0, 0], alphabetabutton)

    difficulty = 0
    menu = True
    opponent = ''; algorithm = ''
    PVP = False; PVAI = False

    while menu:
        title_img = bigfont.render("Checkers!", True, (255, 255, 255))
        play_img = font.render("Play Game", True, (255, 255, 255))

        opp_text = font.render("Choose opponent:", True, (255, 255, 255))
        diff_text = font.render("Choose AI Difficulty: ", True, (255, 255, 255))
        alg_text = font.render("Choose algorithm: ", True, (255, 255, 255))

        play_len = play_img.get_width()

        pvp_img = font.render("PvP", True, (255, 255, 255))
        pvai_img = font.render("PvAI", True, (255, 255, 255))

        db1_img = font.render("1", True, (255, 255, 255)); db2_img = font.render("2", True, (255, 255, 255))
        db3_img = font.render("3", True, (255, 255, 255)); db4_img = font.render("4", True, (255, 255, 255))

        minimax_img = font.render("Minimax", True, (255, 255, 255)); alphabeta_img = font.render("Alpha-Beta", True, (255, 255, 255))
        tip1 = font.render("Press 'q' to exit", True, (255,100,100))
        liner = font.render("____________", True, (255,255,255))
        tip2 = font.render("Make all selections", True, (255, 100, 100))
        tip3 = font.render("to play with AI.", True, (255,100,100))

        MENU.blit(tip1, (500, 200)); MENU.blit(liner, (500, 235))
        MENU.blit(tip2, (500, 294)); MENU.blit(tip3, (500, 324))
        MENU.blit(title_img, (300, 30)); MENU.blit(pvp_img, (150, 210))
        MENU.blit(pvai_img, (145, 280)); MENU.blit(alphabeta_img, (110, 560))
        MENU.blit(play_img, (200 + 25 - int(play_len / 2), 105 + 5))
        MENU.blit(db1_img, (117, 388)); MENU.blit(db2_img, (175, 388))
        MENU.blit(db3_img, (235, 388)); MENU.blit(db4_img, (295, 388))
        MENU.blit(opp_text, (100, 160)); MENU.blit(diff_text, (100, 340))
        MENU.blit(alg_text, (100, 440)); MENU.blit(minimax_img, (125, 490))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if pvaibutton.collidepoint(mouse_pos):
                    opponent = 'PVAI'
                    pygame.draw.rect(MENU, [0, 0, 255], pvaibutton); pygame.draw.rect(MENU, [255, 0, 0], pvpbutton)
                    pygame.display.update()
                if pvpbutton.collidepoint(mouse_pos):
                    opponent = 'PVP'
                    pygame.draw.rect(MENU, [0, 0, 255], pvpbutton); pygame.draw.rect(MENU, [255, 0, 0], pvaibutton)
                    pygame.display.update()

                if opponent == "PVAI":
                    if difbutton1.collidepoint(mouse_pos):
                        pygame.draw.rect(MENU, [0, 0, 255], difbutton1); pygame.draw.rect(MENU, [255, 0, 0], difbutton2)
                        pygame.draw.rect(MENU, [255, 0, 0], difbutton3); pygame.draw.rect(MENU, [255, 0, 0], difbutton4)
                        difficulty = 1
                    if difbutton2.collidepoint(mouse_pos):
                        pygame.draw.rect(MENU, [0, 0, 255], difbutton2); pygame.draw.rect(MENU, [255, 0, 0], difbutton1)
                        pygame.draw.rect(MENU, [255, 0, 0], difbutton3); pygame.draw.rect(MENU, [255, 0, 0], difbutton4)
                        difficulty = 2
                    if difbutton3.collidepoint(mouse_pos):
                        pygame.draw.rect(MENU, [0, 0, 255], difbutton3); pygame.draw.rect(MENU, [255, 0, 0], difbutton2)
                        pygame.draw.rect(MENU, [255, 0, 0], difbutton1); pygame.draw.rect(MENU, [255, 0, 0], difbutton4)
                        difficulty = 3
                    if difbutton4.collidepoint(mouse_pos):
                        pygame.draw.rect(MENU, [0, 0, 255], difbutton4); pygame.draw.rect(MENU, [255, 0, 0], difbutton2)
                        pygame.draw.rect(MENU, [255, 0, 0], difbutton1); pygame.draw.rect(MENU, [255, 0, 0], difbutton3)
                        difficulty = 4

                elif opponent == "PVP":
                    pygame.draw.rect(MENU, [255, 0, 0], difbutton4); pygame.draw.rect(MENU, [255, 0, 0], difbutton2)
                    pygame.draw.rect(MENU, [255, 0, 0], difbutton1); pygame.draw.rect(MENU, [255, 0, 0], difbutton3)
                    pygame.draw.rect(MENU, [255, 0, 0], minimaxbutton); pygame.draw.rect(MENU, [255, 0, 0], alphabetabutton)

                if minimaxbutton.collidepoint(mouse_pos):
                    pygame.draw.rect(MENU, [0, 0, 255], minimaxbutton); pygame.draw.rect(MENU, [255, 0, 0], alphabetabutton)
                    algorithm = "minimax"

                if alphabetabutton.collidepoint(mouse_pos):
                    pygame.draw.rect(MENU, [0, 0, 255], alphabetabutton); pygame.draw.rect(MENU, [255, 0, 0], minimaxbutton)
                    algorithm = "alphabeta"

                if playbutton.collidepoint(mouse_pos):
                    if opponent == "PVP":
                        PVP = True
                        menu = False
                    elif opponent == "PVAI" and difficulty != 0 and (algorithm == 'minimax' or algorithm == 'alphabeta'):
                        PVAI = True
                        menu = False

    clock = pygame.time.Clock()
    aimoves = 0
    game = Game(WIN)
    aitimestamps = []

    while PVAI:

        clock.tick(FPS)

        if game.turn == NEGRU:

            start = time.time()
            aimoves += 1
            if algorithm == 'minimax':
                value, new_board = minimax(game.getBoard(), difficulty, NEGRU, game)
                game.aiMove(new_board)
                aiend = time.time()
                print("Move score: " + str(value))
                print(f"AI moved in: {aiend - start:0.3f} seconds on Minimax")
                aitimestamps.append(aiend - start)

            elif algorithm == 'alphabeta':
                value, new_board = alpha_beta(-500, 500, game.getBoard(), difficulty, NEGRU, game)
                game.aiMove(new_board)
                aiend = time.time()
                print("Move score: " + str(value))
                print(f"AI moved in: {aiend - start:0.3f} seconds on Alpha-Beta")
                aitimestamps.append(aiend - start)

            playerstart = time.time()

        if game.getWinner() != None or keyboard.is_pressed('q'):
            PVAI = False
            print("The AI won!")
            globalend = time.time()
            if game.getWinner() == NEGRU:
                print("AI moved: " + str(aimoves))
                print("Player moved: " + str(aimoves-1))
                print("------------------------------")

            else:
                print("AI moved: " + str(aimoves))
                print("Player moved: " + str(aimoves + 1))
                print("------------------------------")



            my_formatter = "{0:.2f}"
            print(f"Program ran for : {globalend - globalstart:0.2f}  seconds.")
            print("Longest time AI needed to move: " + my_formatter.format(max(aitimestamps)) + " seconds")
            print("Shortest time AI needed to move: " + my_formatter.format(min(aitimestamps)) + " seconds")
            aitimestamps.sort()
            print("Mean time for AI: " + my_formatter.format(aitimestamps[int(len(aitimestamps) / 2)]) + " seconds")

        if game.turn == ALB:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    PVAI = False
                    print("Player won!")
                    print("AI moved: " + str(aimoves))
                    print("Player moved: " + str(aimoves - 1))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = getRowColMouse(pos)

                    game.select(row, col)
                    if game.turn == NEGRU:
                        playerend = time.time()
                        print(f"Player moved in: {playerend - playerstart:0.3f} seconds")
            game.updateGame()

    while PVP:
        clock.tick(FPS)

        if game.getWinner() != None:
            globalend = time.time()
            PVP = False

            if game.getWinner() == NEGRU:
                print("NEGRU won!")
            else:
                print("ALB won!")

            print(f"Program ran for : {globalend - globalstart:0.2f}  seconds.")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                PVP = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = getRowColMouse(pos)
                game.select(row, col)

        game.updateGame()

    pygame.quit()

main()