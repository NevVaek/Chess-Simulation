import copy

class Piece:
    """Superclass of the individual chess piece class. Holds the bulk of the codes for move() method"""
    def __init__(self, player, pos, boardobj):
        self.Player = player.upper()
        self.current_pos = pos
        self.boardObj = boardobj
        self.boardObj.activePieces[self.Player].append(self)
        self.boardObj.place_piece(piece=self, coord=self.current_pos)

    def move(self, destination, movesdict=None, currentpos=None):
        """move() method inside each of the piece class. The method receives
        destination coordinates and the list of largest possible move combinations
        from the individual subclasses and determines whether it is legal.
        Calls for place_piece() method in Board class to actually place the piece"""
        valid_moves = copy.deepcopy(movesdict)

        deleteList = {"lftUp": [],
                      "up": [],
                      "rtUp": [],
                      "rt": [],
                      "rtDown": [],
                      "down": [],
                      "lftDown": [],
                      "lft": [],}

        if self.__class__.__name__ == "Pawn":  #Checks if the piece is a pawn and whether the special moves are allowed
            self.boardObj.pawn_processor(pawnobj=self, movedict=valid_moves)

        elif self.__class__.__name__ == "King": #Checks if the piece is a king and whether castling is allowed
            if self.castling_allowed() == 1 or self.castling_allowed() == 3:
                valid_moves["lft"].append((self.current_pos[0] - 2, self.current_pos[1]))
            if self.castling_allowed() == 2 or self.castling_allowed() == 3:
                valid_moves["rt"].append((self.current_pos[0] + 2, self.current_pos[1]))

        blocked = False  # Checks whether any pieces are blocking move paths. Removes path from "valid_moves" if so
        for direction, listobj in valid_moves.items():
            for item in listobj:
                for coord in item:
                    if coord <= 0 or coord >= 9:    #Checks if the move path is outside board
                        blocked = True
                        break
                if blocked is True:
                    deleteList[direction].append(item)  #If a grid is blocked, also removes the rest of the grids thereon
                    continue
                result = self.boardObj.find_grid(coordinates=item, placeobj="CHECKMODE")
                if result is not None and result.Player != self.Player: # If a piece is blocking the path and if it is a enemy, blocked thereon
                    blocked = True
                elif result is not None and result.Player == self.Player:   # If a piece is blocking and if its your own, grid itself is forbidden and blocked
                    deleteList[direction].append(item)
                    blocked = True
            blocked = False         #"blocked" is turned to false when the check moves on to another direction

        for direction, listobj in deleteList.items():
            for move in listobj:
                valid_moves[direction].remove(move)        #Actually removes the invalid paths from "valid_moves"

        is_valid = False  # Moves the piece to target location if move is valid
        for listobj in valid_moves.values():
            if destination in listobj:
                if self.boardObj.board[destination[1] - 1][destination[0] - 1][1] is not None:
                    self.boardObj.capture_piece(destination)

                self.boardObj.place_piece(piece=self, coord=destination, fromPosition=currentpos)
                is_valid = True

                if self.__class__.__name__ == "Pawn":
                    # if the pawn move done was 2-step forward, enables enpassant for opponent
                    if destination == (self.current_pos[0], self.current_pos[1] + 2) or destination == (self.current_pos[0], self.current_pos[1] - 2):
                        self.enpassant_allowed = True

                    # Code for allowing pawn to pawn capture
                    if destination == (self.current_pos[0] + 1, self.current_pos[1] + 1) or destination == (self.current_pos[0] - 1, self.current_pos[1] + 1):
                        piecebehind = self.boardObj.find_grid(coordinates=(destination[0], destination[1] - 1), placeobj="CHECKMODE")
                        if piecebehind is not None and piecebehind.__class__.__name__ == "Pawn" and piecebehind.enpassant_allowed:
                            self.boardObj.capture_piece(piecebehind.current_pos)

                    elif destination == (self.current_pos[0] + 1, self.current_pos[1] - 1) or destination == (self.current_pos[0] - 1, self.current_pos[1] - 1):
                        piecebehind = self.boardObj.find_grid(coordinates=(destination[0], destination[1] + 1), placeobj="CHECKMODE")
                        if piecebehind is not None and piecebehind.__class__.__name__ == "Pawn" and piecebehind.enpassant_allowed:
                            self.boardObj.capture_piece(piecebehind.current_pos)

                elif self.__class__.__name__ == "King": #If the king was castled, moves the rook accordingly
                    if destination == (self.current_pos[0] - 2, self.current_pos[1]):
                        rookObj = self.boardObj.find_grid(coordinates=(self.current_pos[0] - 4, self.current_pos[1]), placeobj="CHECKMODE")
                        self.boardObj.place_piece(piece=rookObj, coord=(self.current_pos[0] - 1, self.current_pos[1]), fromPosition=rookObj.current_pos)
                        rookObj.current_pos = (self.current_pos[0] - 1, self.current_pos[1])

                    elif destination == (self.current_pos[0] + 2, self.current_pos[1]):
                        rookObj = self.boardObj.find_grid(coordinates=(self.current_pos[0] + 3, self.current_pos[1]), placeobj="CHECKMODE")
                        self.boardObj.place_piece(piece=rookObj, coord=(self.current_pos[0] + 1, self.current_pos[1]), fromPosition=rookObj.current_pos)
                        rookObj.current_pos = (self.current_pos[0] + 1, self.current_pos[1])

                self.current_pos = destination

                pawnBox = []  # Gets the opponents pawn pieces and make sure none of them are enpassant allowed
                opponent = "BLACK" if self.Player == "WHITE" else "WHITE"
                for piece in self.boardObj.activePieces[opponent]:
                    if piece.__class__.__name__ == "Pawn":
                        pawnBox.append(piece)
                if len(pawnBox) > 0:
                    for pawn in pawnBox:
                        if pawn.enpassant_allowed:
                            pawn.enpassant_allowed = False

                if self.__class__.__name__ == "Pawn" and (self.current_pos[1] == 1 or self.current_pos[1] == 8):
                    raise PromotionAllowed()
                break
        if not is_valid:
            raise InvalidDestination("Illegal move.")

        
class King(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        self.first_step = True
        self.identity = "WK" if self.Player == "WHITE" else "BK"

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos

        valid_moves = {"lftUp" :[(fromx - 1, fromy + 1)],
                       "up" : [(fromx, fromy + 1)],
                       "rtUp" : [(fromx + 1, fromy + 1)],
                       "rt" : [(fromx + 1, fromy)],
                       "rtDown" : [(fromx + 1, fromy - 1)],
                       "down" : [(fromx, fromy - 1)],
                       "lftDown" : [(fromx - 1, fromy - 1)],
                       "lft" : [(fromx - 1, fromy)]}

        super().move(destination, movesdict=valid_moves, currentpos=self.current_pos)
        if self.first_step:
            self.first_step = False

    def castling_allowed(self):
        if self.first_step:
            y = self.current_pos[1]
            QueenSide = {(1, y), (2, y), (3, y), (4, y)}
            KingSide = {(6, y), (7, y), (8, y)}
            Checked = set()

            for side in QueenSide, KingSide:
                for grid in side:
                    gridresult = self.boardObj.find_grid(coordinates=grid, placeobj="CHECKMODE")
                    if grid in ((2, y), (3, y), (4, y), (6, y), (7, y)):
                        if gridresult is None:
                            Checked.add(grid)
                    if grid in ((1, y), (8, y)):
                        if gridresult.__class__.__name__ == "Rook" and gridresult.first_step:
                            Checked.add(grid)
            answer = 0
            if Checked.intersection(QueenSide) == QueenSide:
                answer += 1
            if Checked.intersection(KingSide) == KingSide:
                answer += 2

            return answer   #Returns 1 if can castle on Queenside, 2 if on Kingside, 3 (1 + 2) if on both sides.

    def __repr__(self):
        return "WK " if self.Player == "WHITE" else "BK "


class Queen(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        piecename = "WQ" if self.Player == "WHITE" else "BQ"
        self.identity = piecename
        if self.boardObj.count_pieces("Queen", self.Player) != "1":
            self.identity += self.boardObj.count_pieces("Queen", self.Player)

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos
        valid_moves = {"lftUp" : [(fromx - 1, fromy + 1), (fromx - 2, fromy + 2), (fromx - 3, fromy + 3), (fromx - 4, fromy + 4), (fromx - 5, fromy + 5),(fromx - 6, fromy + 6), (fromx - 7, fromy + 7)],
                       "up" : [(fromx, fromy + 1), (fromx, fromy + 2), (fromx, fromy + 3), (fromx, fromy + 4), (fromx, fromy + 5), (fromx, fromy + 6), (fromx, fromy + 7)],
                       "rtUp" : [(fromx + 1, fromy + 1), (fromx + 2, fromy + 2), (fromx + 3, fromy + 3), (fromx + 4, fromy + 4), (fromx + 5, fromy + 5), (fromx + 6, fromy + 6), (fromx + 7, fromy + 7)],
                       "rt" : [(fromx + 1, fromy), (fromx + 2, fromy), (fromx + 3, fromy), (fromx + 4, fromy), (fromx + 5, fromy), (fromx + 6, fromy), (fromx + 7, fromy)],
                       "rtDown" : [(fromx + 1, fromy - 1), (fromx + 2, fromy - 2), (fromx + 3, fromy - 3), (fromx + 4, fromy - 4), (fromx + 5, fromy - 5), (fromx + 6, fromy - 6), (fromx + 7, fromy - 7)],
                       "down" : [(fromx, fromy - 1), (fromx, fromy - 2), (fromx, fromy - 3), (fromx, fromy - 4), (fromx, fromy - 5), (fromx, fromy - 6), (fromx, fromy - 7)],
                       "lftDown" : [(fromx - 1, fromy - 1), (fromx - 2, fromy - 2), (fromx - 3, fromy - 3), (fromx - 4, fromy - 4), (fromx - 5, fromy - 5), (fromx - 6, fromy - 6), (fromx - 7, fromy - 7)],
                       "lft" : [(fromx - 1, fromy), (fromx - 2, fromy), (fromx - 3, fromy), (fromx - 4, fromy), (fromx - 5, fromy), (fromx - 6, fromy), (fromx - 7, fromy)]}
        super().move(destination, movesdict=valid_moves, currentpos=self.current_pos)

    def __repr__(self):

        if self.boardObj.count_pieces("Queen", self.Player) == "1":
            return self.identity + " "
        else:
            return self.identity

class Rook(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        self.first_step = True
        piecename = "WR" if self.Player == "WHITE" else "BR"
        piecename += self.boardObj.count_pieces("Rook", self.Player)
        self.identity = piecename

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos
        valid_moves = {"up" : [(fromx, fromy + 1), (fromx, fromy + 2), (fromx, fromy + 3), (fromx, fromy + 4), (fromx, fromy + 5), (fromx, fromy + 6), (fromx, fromy + 7)],
                       "rt" : [(fromx + 1, fromy), (fromx + 2, fromy), (fromx + 3, fromy), (fromx + 4, fromy), (fromx + 5, fromy), (fromx + 6, fromy), (fromx + 7, fromy)],
                       "down" : [(fromx, fromy - 1), (fromx, fromy - 2), (fromx, fromy - 3), (fromx, fromy - 4), (fromx, fromy - 5), (fromx, fromy - 6), (fromx, fromy - 7)],
                       "lft" : [(fromx - 1, fromy), (fromx - 2, fromy), (fromx - 3, fromy), (fromx - 4, fromy), (fromx - 5, fromy), (fromx - 6, fromy), (fromx - 7, fromy)]}
        super().move(destination, movesdict=valid_moves, currentpos=self.current_pos)
        if self.first_step:
            self.first_step = False

    def __repr__(self):
        return self.identity

class Bishop(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        piecename = "WB" if self.Player == "WHITE" else "BB"
        piecename += self.boardObj.count_pieces("Bishop", self.Player)
        self.identity = piecename

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos
        valid_moves = {"lftUp" : [(fromx - 1, fromy + 1), (fromx - 2, fromy + 2), (fromx - 3, fromy + 3), (fromx - 4, fromy + 4), (fromx - 5, fromy + 5),(fromx - 6, fromy + 6), (fromx - 7, fromy + 7)],
                       "rtUp" : [(fromx + 1, fromy + 1), (fromx + 2, fromy + 2), (fromx + 3, fromy + 3), (fromx + 4, fromy + 4), (fromx + 5, fromy + 5), (fromx + 6, fromy + 6), (fromx + 7, fromy + 7)],
                       "rtDown" : [(fromx + 1, fromy - 1), (fromx + 2, fromy - 2), (fromx + 3, fromy - 3), (fromx + 4, fromy - 4), (fromx + 5, fromy - 5), (fromx + 6, fromy - 6), (fromx + 7, fromy - 7)],
                       "lftDown" : [(fromx - 1, fromy - 1), (fromx - 2, fromy - 2), (fromx - 3, fromy - 3), (fromx - 4, fromy - 4), (fromx - 5, fromy - 5), (fromx - 6, fromy - 6), (fromx - 7, fromy - 7)]}
        super().move(destination, movesdict=valid_moves, currentpos=self.current_pos)

    def __repr__(self):
        return self.identity

class Knight(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        piecename = "WN" if self.Player == "WHITE" else "BN"
        piecename += self.boardObj.count_pieces("Knight", self.Player)
        self.identity = piecename

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos
        valid_moves = {"lftUp" : [(fromx - 1, fromy + 2)],
                       "up" : [(fromx + 1, fromy + 2)],
                       "rtUp" : [(fromx + 2, fromy + 1)],
                       "rt" : [(fromx + 2, fromy - 1)],
                       "rtDown" : [(fromx + 1, fromy - 2)],
                       "down" : [(fromx - 1, fromy - 2)],
                       "lftDown" : [(fromx - 2, fromy - 1)],
                       "lft" : [(fromx - 2, fromy + 1)]}

        super().move(destination, movesdict=valid_moves, currentpos=self.current_pos)

    def __repr__(self):
        return self.identity

class Pawn(Piece):
    def __init__(self, player, pos, boardobj):
        super().__init__(player, pos, boardobj)
        self.first_step = True
        self.enpassant_allowed = False
        self.starting_pos = pos
        piecename = "WP" if self.Player == "WHITE" else "BP"
        piecename += str(self.starting_pos[0])
        self.identity = piecename

    def move(self, destination, moves=None, currentpos=None):
        fromx, fromy = self.current_pos
        valid_movesW = {"lftUp" : [(fromx - 1, fromy + 1)], #Taking pieces
                       "up" : [(fromx, fromy + 1), (fromx, fromy + 2)],
                       "rtUp" : [(fromx + 1, fromy + 1)]}

        valid_movesB = {"lftDown" : [(fromx - 1, fromy - 1)],
                        "down" : [(fromx, fromy - 1), (fromx, fromy - 2)],
                        "rtDown" : [(fromx + 1, fromy - 1)]}

        if self.Player == "WHITE":
            super().move(destination, movesdict=valid_movesW, currentpos=self.current_pos)
        else:
            super().move(destination, movesdict=valid_movesB, currentpos=self.current_pos)

        if self.first_step:
            self.first_step = False

    def enpassant(self): #After creation, use in
        x, y = self.current_pos
        leftObj = self.boardObj.find_grid(coordinates=(x - 1, y), placeobj="CHECKMODE")
        rightObj = self.boardObj.find_grid(coordinates=(x + 1, y), placeobj="CHECKMODE")
        if leftObj.__class__.__name__ == "Pawn" and leftObj.Player != self.Player and leftObj.enpassant_allowed:
            return 1
        elif rightObj.__class__.__name__ == "Pawn" and rightObj.Player != self.Player and rightObj.enpassant_allowed:
            return 2
        else:
            return 0

    def promotor(self, promoteto):
        """Promotes self to a higher being. To use this method, always check beforehand
            that self satisfies the promotion requirement (Being in the 1st or 8th rank)"""

        higherbeings = ("Queen", "Rook", "Bishop", "Knight")
        if promoteto not in higherbeings:
            raise InvalidPiece("Invalid Piece name")

        self.boardObj.find_grid(coordinates=(self.current_pos), placeobj=None)

        if promoteto == "Queen":
            newPiece = Queen(player=self.Player, pos=self.current_pos, boardobj=self.boardObj)
        elif promoteto == "Rook":
            newPiece = Rook(player=self.Player, pos=self.current_pos, boardobj=self.boardObj)
        elif promoteto == "Bishop":
            newPiece = Bishop(player=self.Player, pos=self.current_pos, boardobj=self.boardObj)
        elif promoteto == "Knight":
            newPiece = Knight(player=self.Player, pos=self.current_pos, boardobj=self.boardObj)

        self.boardObj.activePieces[self.Player].remove(self)
        del self

    def __repr__(self):
        return self.identity

class InvalidDestination(Exception):
    pass

class InvalidPiece(Exception):
    pass

class PromotionAllowed(Exception):
    pass


class Board:
    """The main class that keeps track of the gameboard and the pieces on it."""
    def __init__(self):
        """Creates a brand-new board when the class is created"""
        self.activePieces = {"WHITE" : [], "BLACK" : []}
        self.capturedPieces = {"WHITE" : [], "BLACK" : []}
        self.board = []
        for y in range(8):
            self.board.append([])
            for x in range(8):
                self.board[y].append([(x + 1, y + 1), None])

    def find_grid(self, coordinates, placeobj):
        for y, v1 in enumerate(self.board):
            for x, v2 in enumerate(v1):
                if coordinates in v2:
                    if placeobj == "CHECKMODE":
                        return None if self.board[y][x][1] is None else self.board[y][x][1]
                    else:
                        self.board[y][x][1] = placeobj

    def place_piece(self, piece, coord, fromPosition=None):
        """This method can place new pieces as well as move existing ones.
        the presence of fromPosition argument determines whether the piece is new or not"""
        Initial = False
        if fromPosition is None:
            Initial = True
        self.find_grid(coord, piece)

        if not Initial:
            self.find_grid(fromPosition, None)

    def count_pieces(self, piece_name, player):
        count = 0
        for piece in self.activePieces[player.upper()]:
            if piece.__class__.__name__ == piece_name:
                count += 1
        for capturedpiece in self.capturedPieces["BLACK" if player.upper() == "WHITE" else "WHITE"]:
            if capturedpiece.__class__.__name__ == piece_name:
                count += 1
        return str(count)

    def pawn_processor(self, pawnobj, movedict):
        #if destination[1] == 1 or 8:
            #print("Promoting pawn") # Temporary
            #Remove pawn Obj and PROMOTE
            #ALSO: PROMOTION SHOULD BE IN ITS OWN METHOD AND CALLED JUST BEFORE place_piece() in Piece class.
        if not pawnobj.first_step:  # Removes 2 step forward moves from valid moves.
            movedict["up"].pop(1) if pawnobj.Player == "WHITE" else movedict["down"].pop(1)

        currentx, currenty = pawnobj.current_pos

        lftUp = (currentx - 1, currenty + 1)
        lftDown = (currentx - 1, currenty - 1)
        rtUp = (currentx + 1, currenty + 1)
        rtDown = (currentx + 1, currenty - 1)
        for direction in (lftUp, rtUp, lftDown, rtDown):
            if str(direction) not in str(movedict.values()):
                continue
            gridObj = self.find_grid(coordinates=direction, placeobj="CHECKMODE")
            if direction in (lftUp, rtUp) and (gridObj is None or gridObj.Player == "WHITE"):
                if direction == lftUp and pawnobj.enpassant() != 1:
                    movedict["lftUp"].remove(direction)
                if direction == rtUp and pawnobj.enpassant() != 2:
                    movedict["rtUp"].remove(direction)
                continue

            elif direction in (lftDown, rtDown) and (gridObj is None or gridObj.Player == "BLACK"):
                if direction == lftDown and pawnobj.enpassant() != 1:
                    movedict["lftDown"].remove(direction)
                if direction == rtDown and pawnobj.enpassant() != 2:
                    movedict["rtDown"].remove(direction)
                continue

        return movedict

    def capture_piece(self, coord):
        opponentPiece = self.find_grid(coordinates=coord, placeobj="CHECKMODE")
        self.board[opponentPiece.current_pos[1] - 1][opponentPiece.current_pos[0] - 1][1] = None
        opponentPiece.current_pos = None
        self.capturedPieces["BLACK" if opponentPiece.Player == "WHITE" else "WHITE"].append(opponentPiece)
        self.activePieces[opponentPiece.Player].remove(opponentPiece)
