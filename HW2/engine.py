#!/usr/bin/env python3
# Engine for a Tic Tac Toe Game
class Engine:
    EMPTY = '🍆'
    TIE = '🚫'
    X = '❌'
    O = '⭕'

    winning_combos = [ 
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)]

    def __init__(self):
        self.restart()

    def restart(self):
        self.board = [Engine.EMPTY for i in range(9)]
        self.x_turn = True
        self.turns = 0
    
    def __str__(self):
        return '\n'.join([f'    {self.board[i*3+0]}  {self.board[i*3+1]}  {self.board[i*3+2]}' for i in range(0, 3)])
    
    def is_game_over(self):
        def winner(board, combo, empty):
            return (
                board[combo[0]] is not empty and
                board[combo[0]] is board[combo[1]] and
                board[combo[1]] is board[combo[2]])

        for combo in winning_combos:
            if winner(self.board, combo, Engine.EMPTY):
                return self.board[combo[0]]
            if self.turns is 9:
                return Engine.TIE
        return Engine.EMPTY

    def is_move_valid(self, pos):
        return 0 <= pos and pos <= 8 and self.board[pos] is Engine.EMPTY

    def make_move(self, pos):
        if self.is_move_valid(pos):
            self.board[pos] = (Engine.X if self.x_turn else Engine.O)
            self.turns += 1
            self.x_turn = not self.x_turn
            return True
        return False


if __name__ == "__main__":
    engine = Engine()
    print(engine, end='\n\n')
    for i in range(0, 9):
        engine.make_move(i)
        print(engine, end='\n\n')
