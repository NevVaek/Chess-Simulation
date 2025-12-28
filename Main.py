import Board, sys

class Game:
    def __init__(self):
        self.boardObj = Board.Board()
        self.board = self.boardObj.board

        self.KW = Board.King("white", (5, 1), boardobj=self.boardObj)
        self.QW = Board.Queen("white", (4, 1), boardobj=self.boardObj)
        self.KnightW1 = Board.Knight("white", (2, 1), boardobj=self.boardObj)
        self.KnightW2 = Board.Knight("white", (7, 1), boardobj=self.boardObj)
        self.BW1 = Board.Bishop("white", (3, 1), boardobj=self.boardObj)
        self.BW2 = Board.Bishop("white", (6, 1), boardobj=self.boardObj)
        self.R1W = Board.Rook("White", (1, 1), boardobj=self.boardObj)
        self.R2W = Board.Rook("White", (8, 1), boardobj=self.boardObj)
        self.p1W = Board.Pawn("white", (1, 2), boardobj=self.boardObj)
        self.p2W = Board.Pawn("White", (2, 2), boardobj=self.boardObj)
        self.p3W = Board.Pawn("White", (3, 2), boardobj=self.boardObj)
        self.p4W = Board.Pawn("White", (4, 2), boardobj=self.boardObj)
        self.p5W = Board.Pawn("White", (5, 2), boardobj=self.boardObj)
        self.p6W = Board.Pawn("White", (6, 2), boardobj=self.boardObj)
        self.p7W = Board.Pawn("white", (7, 2), boardobj=self.boardObj)
        self.p8W = Board.Pawn("White", (8, 2), boardobj=self.boardObj)

        self.KB = Board.King("black", (5, 8), boardobj=self.boardObj)
        self.QB = Board.Queen("black", (4, 8), boardobj=self.boardObj)
        self.Knight1B = Board.Knight("black", (2, 8), boardobj=self.boardObj)
        self.Knight2B = Board.Knight("black", (7, 8), boardobj=self.boardObj)
        self.B1B = Board.Bishop("black", (3, 8), boardobj=self.boardObj)
        self.B2B = Board.Bishop("black", (6, 8), boardobj=self.boardObj)
        self.R1B = Board.Rook("Black", (1, 8), boardobj=self.boardObj)
        self.R2B = Board.Rook("Black", (8, 8), boardobj=self.boardObj)
        self.p1B = Board.Pawn("black", (1, 7), boardobj=self.boardObj)
        self.p2B = Board.Pawn("black", (2, 7), boardobj=self.boardObj)
        self.p3B = Board.Pawn("black", (3, 7), boardobj=self.boardObj)
        self.p4B = Board.Pawn("black", (4, 7), boardobj=self.boardObj)
        self.p5B = Board.Pawn("black", (5, 7), boardobj=self.boardObj)
        self.p6B = Board.Pawn("black", (6, 7), boardobj=self.boardObj)
        self.p7B = Board.Pawn("black", (7, 7), boardobj=self.boardObj)
        self.p8B = Board.Pawn("black", (8, 7), boardobj=self.boardObj)

    def print_board(self, players):
        print(f"\n\t{players[1]()}", end="\n")
        print("   |" + "- " * 31 + "-|")
        ordnum = 56
        for y in range(7, -1, -1):
            print(chr(ordnum).center(3), end="")
            ordnum -= 1
            for x in range(8):
                print("|  ", end="")
                boarditem = self.board[y][x][1]
                if boarditem is None:
                    print("   ", end="")
                else:
                    print(boarditem, end="")
                if x == 7:
                    print("  |")
                    continue
                print("  ", end="")
            print("   |" + "- " * 31 + "-|")
        print("   ", end="")
        for i in range(65, 73):
            print(f"    {chr(i)}   ", end="")
        print(f"\n\t{players[0]()}", end="\n")
        print("\n" * 2)

    # def create_board(self):


class Player:
    def __init__(self, color, gameobj, name):
        self.color = color.upper()
        self.name = name if name != "" else str(self.color)
        self.gameObj = gameobj
        self.points = 0

    def __call__(self):
        mypoints = 0
        enemypoints = 0
        pointsReference = {"Queen" : 5, "Rook" : 4, "Knight" : 3, "Bishop" : 3, "Pawn" : 1}

        myactivepieces = (piece1 for piece1 in self.gameObj.boardObj.activePieces[self.color])
        enemyactivepieces = (piece2 for piece2 in self.gameObj.boardObj.activePieces["BLACK" if self.color == "WHITE" else "WHITE"])


        for obj1 in myactivepieces:
            if obj1.__class__.__name__ == "King":
                continue
            mypoints += pointsReference[obj1.__class__.__name__]
        for obj2 in enemyactivepieces:
            if obj2.__class__.__name__ == "King":
                continue
            enemypoints += pointsReference[obj2.__class__.__name__]
        difference = mypoints - enemypoints
        if difference > 0:
            return f"{self.name.upper()}: +{difference}"
        else:
            return f"{self.name.upper()}"


    def turn(self):
        def string_interpreter(string):
            if string.upper() in ["F", "FORFEIT", "R", "RESIGN", "X"]:
                raise self.PlayerForfeit()

            stripped = [letter for letter in string.upper() if letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"]

            if ((len(stripped) != 5 and len(stripped) != 4) or
                    stripped[0] not in ("W", "B") or
                    stripped[0] != self.color[0] or
                    stripped[1] not in "KQRNBP" or
                    stripped[-2] not in "ABCDEFGH" or
                    stripped[-1] not in "12345678"):
                raise ValueError()

            for piecename in ["King", "Queen", "Rook", "Night", "Bishop", "Pawn"]:
                if stripped[1] == piecename[0]:
                    piece = piecename if piecename != "Night" else "Knight"
            coordinate = (ord(stripped[-2]) - 64, int(stripped[-1]))
            player = "WHITE" if stripped[0] == "W" else "BLACK"
            piece_number = stripped[2] if stripped[2] in "12345678" else ""
            return piece, piece_number, coordinate, player

        all_ok = False
        while not all_ok:
            playerinput = input("Enter a piece name and move coordinates: ")
            try:
                piece, piece_num, coordinate, player = string_interpreter(playerinput)
                all_ok = True
            except ValueError:
                print("Invalid Input. Please enter using the following format: Name_of_piece, Coordinate")
            except self.PlayerForfeit:
                raise Lose(self)
        keyword = player[0] + piece[0] + piece_num
        if piece == "Knight":
            keyword = player[0] + "N" + piece_num
        for pieceobj in self.gameObj.boardObj.activePieces[self.color]:
            if pieceobj.__class__.__name__ == piece and pieceobj.identity == keyword:
                try:
                    pieceobj.move(coordinate)
                except Board.InvalidDestination:
                    print("Piece cannot be moved to that position.")
                    self.turn()
                except Board.PromotionAllowed:
                    while True:
                        choice = input("[Promotion] Enter piece choice: ").title()
                        try:
                            pieceobj.promotor(choice)
                            break
                        except Board.InvalidPiece:
                            continue
                break

    class PlayerForfeit(Exception):
        pass

class RunGame:
    def __init__(self):
        self.game = Game()

        print("Welcome to Chess: The Power Struggle".center(50, ' '))
        input("Press ENTER to start...")
        print("")
        player1_name = input("Enter the player name for WHITE: ")
        player2_name = input("Enter the player name for BLACK: ")

        white = Player("white", self.game, player1_name)
        black = Player("black", self.game, player2_name)

        while True:
            try:
                self.game.print_board((white, black))
                print(self.game.boardObj.activePieces)
                print(self.game.boardObj.capturedPieces)
                print(f"{white.name}'s turn")
                white.turn()
                self.game.print_board((white, black))
                print(f"{black.name}'s turn")
                black.turn()
            except Lose as l:
                print(f"{l.player.name} has forfeited.")
                winner = white if l.player.color == "BLACK" else black
                print(f"{winner.name} is the winner.")
                break
        sys.exit()

class Lose(Exception):
    def __init__(self, player):
        self.player = player
    pass

RunGame()