import tkinter as tk
from functools import partial
import random
import copy


class Player():

    def __init__(self, id, type):
        self.id = id
        self.type = type

    def getID(self):
        return self.id

    def getType(self):
        return self.type



class Square():

    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.status = None # 0: Blank, 1: Player 1, 2: Player 2
        self.button = None

        self.images = {
            0: tk.PhotoImage(file="Images/Blank.png"),
            1: tk.PhotoImage(file="Images/Cross.png"),
            2: tk.PhotoImage(file="Images/Circle.png")
        }

    def addButton(self, button):
        self.button = button

    def updateStatus(self, status):
        self.status = status

    def updateImage(self, key):
        self.button.config(image=self.images[key])

    def getStatus(self):
        return self.status

    def getRow(self):
        return self.row

    def getColumn(self):
        return self.col



class Main(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.turn = 1

        # Players
        self.players = [Player(1, "Human"), Player(2, "AI")]
        self.currentPlayer = self.players[random.randint(0, len(self.players)-1)]
        self.winner = None

        # Placeholder board for squares
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]

        # Simulation board for minimax
        self.simBoard = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]

        # Win condition indexes
        self.win_cons = [
            # Horizontal
            [0, 0, 0, 1, 0, 2],
            [1, 0, 1, 1, 1, 2],
            [2, 0, 2, 1, 2, 2],

            # Vertical
            [0, 0, 1, 0, 2, 0],
            [0, 1, 1, 1, 2, 1],
            [0, 2, 1, 2, 2, 2],

            # Diagonal
            [0, 0, 1, 1, 2, 2],
            [0, 2, 1, 1, 2, 0]]

        # Available Squares
        self.availSquares = list()

        #Scores
        self.scores = {"AI" : 1, "Human" : -1, "Tie" : 0}
        self.createboard()


    def createboard(self):
        for row in range(3):
            for col in range(3):
                self.s = Square(row, col)

                button = tk.Button(root, borderwidth=0, highlightthickness=0,
                         command=partial(self.humanMove, row, col))
                button.grid(row=row, column=col)

                self.s.addButton(button)
                self.s.updateStatus(0)
                self.s.updateImage(0)
                self.availSquares.append(self.s)
                self.board[row][col] = self.s

        # If AI begins
        if self.turn == 1 and self.currentPlayer.type == "AI":
            self.aiMove()

    # Finds best available move
    def minimax(self, board, turn, isMax, depth):
        result = self.checkSimWin(board, turn)

        if result != None:
            return self.scores[result]

        if (isMax):
            bestScore = float("-inf")
            for row in range(3):
                for col in range(3):

                    if board[row][col] == 0:
                        board[row][col] = "AI"
                        score = self.minimax(board, turn+1, False, depth+1)
                        board[row][col] = 0

                        if score > bestScore:
                            bestScore = score
            return bestScore

        else:
            bestScore = float("inf")
            for row in range(3):
                for col in range(3):
                    if board[row][col] == 0:
                        board[row][col] = "Human"
                        score = self.minimax(board, turn+1, True, depth+1)
                        board[row][col] = 0

                        if score < bestScore:
                            bestScore = score
            return bestScore

    # Returns winner, tie else None
    def checkWin(self):
        for i in range(len(self.win_cons)):
            if self.checkSequence(self.win_cons[i]):
                self.winner = self.currentPlayer
                print(f"Winner: {self.winner.getType()}")
                return

        if self.turn == 9:
            print("Tie")

    # Winning sequence as input, eg. top row
    def checkSequence(self, seq):
        s1 = self.board[seq[0]][seq[1]]
        s2 = self.board[seq[2]][seq[3]]
        s3 = self.board[seq[4]][seq[5]]

        if (s1.getStatus() == s2.getStatus() and
            s2.getStatus() == s3.getStatus() and
            s3.getStatus() == self.currentPlayer.id):

            return True


    def checkSimWin(self, board, turn):
        for i in range(len(self.win_cons)):
            if self.checkSimSequence(board, self.win_cons[i]):
                row = self.win_cons[i][0]
                col = self.win_cons[i][1]
                return board[row][col]

        if turn == 9:
            return "Tie"
        return None


    def checkSimSequence(self, board, seq):
        s1 = board[seq[0]][seq[1]]
        s2 = board[seq[2]][seq[3]]
        s3 = board[seq[4]][seq[5]]

        return s1 == s2 and s2 == s3 and s1 != 0


    def aiMove(self):
        if self.turn < 10 and self.winner == None:
            bestScore = float("-inf")
            bestSquares = list()
            tempBoard = self.simBoard.copy()

            for i in range(len(self.availSquares)):
                tempSquare = self.availSquares[i]
                row = tempSquare.getRow()
                col = tempSquare.getColumn()
                tempBoard[row][col] = self.currentPlayer.getType()

                score = self.minimax(tempBoard, self.turn*1, False, 0)
                tempBoard[row][col] = 0

                if score > bestScore: # Replaces all with a better square
                    bestScore = score
                    bestSquares.clear()
                    bestSquares.append(tempSquare)

                elif score == bestScore: # Appends equally good squares
                    bestSquares.append(tempSquare)

            square = bestSquares[random.randint(0, len(bestSquares)-1)]
            square.updateStatus(self.currentPlayer.id)
            square.updateImage(self.currentPlayer.id)

            self.simBoard[square.getRow()][square.getColumn()] = self.currentPlayer.getType()
            self.availSquares.remove(square)
            self.checkWin()

            self.turn += 1
            self.currentPlayer = self.players[self.currentPlayer.id % 2]


    def humanMove(self, row, col):
        square = self.board[row][col]
        if (self.currentPlayer.type == "Human" and self.turn < 10 and
            square.getStatus() == 0 and self.winner == None):
            square.updateStatus(self.currentPlayer.id)
            square.updateImage(self.currentPlayer.id)
            self.simBoard[row][col] = self.currentPlayer.getType()
            self.availSquares.remove(square)
            self.checkWin()
            self.turn += 1
            self.currentPlayer = self.players[self.currentPlayer.id % 2]


        self.aiMove()



if __name__ == "__main__":
    root = tk.Tk()
    Main(root)
    root.mainloop()
