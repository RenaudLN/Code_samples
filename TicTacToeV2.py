# -*- coding: utf-8 -*-
"""
@author: Renaud

This is the electronic version of a game I used to play when I lived in South
Korea. It is a game of Tic tac toe with 9 grids, each time a player plays, it
forces which grid the next player will play in. The winner is the first to get
three aligned symbols in any of the 9 grids.

"""

import tkinter as tk
import numpy as np

class Tictactoe(tk.Frame):
    
    def __init__(self, window, **kwargs):
        # Set main object fields and inherit from tkinter Frame
        tk.Frame.__init__(self,window,width=500,height=600,**kwargs)
        # Player 1 or 2
        self.player = 1
        # Initialize boxes array as lists
        self.text = [[0 for x in range(9)] for x in range(9)]
        self.btn = [[0 for x in range(9)] for x in range(9)]
        # Initialize memory of what was played
        self.moves = np.zeros((9, 9))
        # Initialize player instructions
        self.textplayer = tk.StringVar()
        self.textplayer.set('Player O')
        self.textwin = tk.StringVar()
        # Initialize boxes content
        for i in range(9):
            for j in range(9):
                self.text[i][j] = tk.StringVar()
        
        self.grid()
        
        # Set the 9*9 boxes to play in
        for i in range(9):
            for j in range(9):
                self.btn[i][j] = tk.Button(self, bg = "blue", width = 4, height = 2, textvariable = self.text[i][j], command = lambda i = i, j = j: self.activatebutton(i, j))
                nrow = i + 1 + i // 3
                ncol = j + 1 + j // 3
                self.btn[i][j].grid(row = nrow, column = ncol, padx = 1, pady = 1)
        # Set some spacing in between each grid
        self.hl1 = tk.Label(self, width = 4, height = 2, text = '')
        self.hl1.grid(row = 4, column = 1)
        self.hl2 = tk.Label(self, width = 4, height = 2, text = '')
        self.hl2.grid(row = 8, column = 1)
        self.vl1 = tk.Label(self, width = 4, height = 2, text = '')
        self.vl1.grid(row = 1, column = 4)
        self.vl2 = tk.Label(self, width = 4, height = 2, text = '')
        self.vl2.grid(row = 1, column = 8)
        # Set text indications for players
        self.hl3 = tk.Label(self, height = 2, textvariable = self.textplayer)
        self.hl3.grid(row = 12, column = 1, columnspan = 11)
        self.hl3 = tk.Label(self, height = 2, textvariable = self.textwin)
        self.hl3.grid(row = 13, column = 1, columnspan = 11)
        # Set a reset button
        self.resetbtn = tk.Button(self, text = 'Start again', command = self.reset)
        self.resetbtn.grid(row = 14, column = 1, columnspan = 11)
            
    def activatebutton(self, i, j):
        '''
        This method memorizes what was played, writes it on the board,
        activates next playable grid, calls the victory check and stops the
        game if there is a winner
        '''
        if self.text[i][j].get() == '':
            if self.player == 1:
                s = 'O'
                t = 'X'
            else:
                s = 'X'
                t = 'O'
            self.text[i][j].set(s)
            self.player = 3 - self.player
            self.textplayer.set('Player ' + t)
            self.moves[i][j] = self.player
            win = self.checkwin(i,j)
            for x in range(9):
                for y in range(9):
                    self.btn[x][y].configure(state = tk.DISABLED, bg = "white")
            if win == 0:
                if i % 3 == 0:
                    if j % 3 == 0:
                        for x in range(3):
                            for y in range(3):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    elif j % 3 == 1:
                        for x in range(3):
                            for y in range(3,6):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    else:
                        for x in range(3):
                            for y in range(6,9):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                elif i % 3 == 1:
                    if j % 3 == 0:
                        for x in range(3,6):
                            for y in range(3):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    elif j % 3 == 1:
                        for x in range(3,6):
                            for y in range(3,6):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    else:
                        for x in range(3,6):
                            for y in range(6,9):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                else:
                    if j % 3 == 0:
                        for x in range(6,9):
                            for y in range(3):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    elif j % 3 == 1:
                        for x in range(6,9):
                            for y in range(3,6):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
                    else:
                        for x in range(6,9):
                            for y in range(6,9):
                                self.btn[x][y].configure(state = tk.NORMAL, bg = "blue")
            else:
                if win == 1:
                    swin = 'X'
                else:
                    swin = 'O'
                self.textwin.set('Player {} won.'.format(swin))
            
    def reset(self):
        '''
        This method resets the board
        '''
        for i in range(9):
            for j in range(9):
                self.text[i][j].set('')
                self.btn[i][j].configure(state = tk.NORMAL, bg = "blue")
        self.textwin.set('')
        self.moves = np.zeros((9, 9))
                
    def checkwin(self, i, j):
        '''
        This method cheks whether the last move played was a winning move
        '''
        square = self.moves[3 * (i // 3) : 3 * (i // 3) + 3, 3 * (j // 3) : 3 * (j // 3) + 3]
        for h in range(3):
            win = self.checkline(square[h,:])
            if win != 0:
                return win
        for w in range(3):
            win = self.checkline(square[:,w])
            if win != 0:
                return win
        win = self.checkline(np.diagonal(square))
        if win != 0:
            return win
        win = self.checkline(np.diagonal(np.fliplr(square)))
        if win != 0:
            return win
        return 0
        
    def checkline(self, a):
        if a[0] == a[1] and np.sum(a) > 0 and np.sum(a) % 3 == 0:
            return a[0]
        return 0
        
        
if __name__ == "__main__":
    window = tk.Tk()
    window.resizable(width = tk.FALSE, height = tk.FALSE)
    tictactoe = Tictactoe(window)
    tictactoe.mainloop()
    window.destroy()