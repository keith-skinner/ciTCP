# HW2: Tic Tac Oh No!

## How to Submit Work

- You're not allowed to push to master.
-  Create a branch
   - Make a folder for your assignment, say `HW2`
   - Add, commit, push stuff.
- When you're ready to submit
  -  Make a Pull Request 

## Overview

### Goal

Your goal is to implement your tic tac toe protocol so that two clients may play a game of Tic Tac Toe over the Internet. A Tic Tac Toe engine is given below to save you time. It probably works.

### Requirements

- Protocol documentation.
- Implementation of a client-server architecture for multiplayer tic tac toe.
- It must be done with Python 3.
- The transport layer must be TCP.
- The provided engine must be used, though it may be modified to fit your needs.
- Submission must be through your assigned bitbucket repo.

### Grading

- Protocol Implementation
  - Did you implement the protocol you described?
  - If you changed any of the shortcomings, did you update your documentation?
- General Code Quality (Significant forgiveness for IT majors)
  - Are there two blank lines after function definitions?
  - Do your variable names make sense?
  - Did you use comments or docstrings to document your code?
  - Is everything in one big file or spread across multiple files?
- git
  - Did you submit your code correctly through git?
  - Are there commits to show work over a period of time?
  - Did you make the pull request so I can grade it?
- Sample run documentation
  - Please include text documents containing a sample run of the clients and server.

## Engine

Below is a Tic Tac Toe engine written in python. It should work on macOS, Windows, and Linux.

```python
class TicTacToeEngine:
    def __init__(self):
        # board is just a list of dashes for blanks. X and O's will fill it eventually.
        self.board = ['-','-','-','-','-','-','-','-','-']
        # is it x's turn?
        self.x_turn = True
        # how many successful turns have we played?
        self.turns = 0
        

    def restart(self):
        self.board = ['-','-','-','-','-','-','-','-','-']
        self.x_turn = True
        self.turns = 0


    def display_board(self):
        j = 0
        for i in range(0,9): # for (i = 0; i < 9; i++) 
            # print without a new line
            print(self.board[i], end=' ') 
            j += 1
            # add a new line every 3 board spaces
            if j % 3 == 0:
                print('')
    
    
    def is_game_over(self):
        # winning combos in tic tac toe
        winning_combos = [  (0,1,2),(3,4,5),(6,7,8),
                            (0,3,6),(1,4,7),(2,5,8),
                            (0,4,8),(2,4,6)]

        # for each of the winning combos
        for combo in winning_combos:
            # assume the first piece is a winner
            winner = self.board[combo[0]]
            # if it is not blank
            if winner is 'X' or winner is 'O':
                # and if the next two on the board are the same as the first one
                if winner is self.board[combo[1]] and winner is self.board[combo[2]]:
                    # that piece has won
                    return winner

        # no winning combos and the board is full.
        if self.turns == 9:
            return 'T'
        
        # not done yet
        return '-'


    def make_move(self, pos):
        # make a move if it is valid (between 0 and 8 inclusive) 
        # increase number of turns by 1
        # invert the x_turn boolean
        if self.is_move_valid(pos):
            if self.x_turn:
                self.board[pos] = 'X'
            else:
                self.board[pos] = 'O'
            self.turns += 1
            self.x_turn = not self.x_turn

    
    def is_move_valid(self, pos):
        # make sure it is on the board and no one has already plkayed there!
        return (pos >= 0 and pos <= 8 and self.board[pos] is '-')


# sample game
ttte = TicTacToeEngine()
ttte.display_board()
print(ttte.is_game_over())

for i in range(0,9):
    print('='*40)
    ttte.make_move(i)
    ttte.display_board()
    winner = ttte.is_game_over()
    if winner is not '-':
        print("Winner: " + winner)
        break

if winner is '-':
    print("Tie.")
```

## Simple Server Example

```python
import argparse, socket, logging, threading

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):
    def __init__(self, address, socket):
        threading.Thread.__init__(self)
        self.csock = socket
        logging.info('New connection added.')

    
    def run(self):
        # exchange messages
        message = self.recvall(8)
        msg = message.decode('utf-8')
        logging.info('Recieved a message from client: ' + msg)

        if msg.startswith('100'):
            self.csock.sendall(b'200 OK')
            logging.info('Recieved HELO ok from client.')
        else:
            self.csock.sendall(b'500 BAD REQUEST')
            logging.warning('Bad request from client.')

        # disconnect client
        self.csock.close()
        logging.info('Disconnect client.')

    
    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data
        

def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))    
        
        # client has connected
        sc,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc)
        t.start()
```

### Simple Client Example

```python
import argparse, socket, logging

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data


def client(host,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    # exchange messages
    sock.sendall(b'100 HELO')
    logging.info('Sent: 100 HELO')
    message = recvall(sock, 6).decode('utf-8') 
    logging.info('Received: ' + message)
    if message.startswith('200'):
        logging.info('This is a good thing.')
    else:
        logging.info('We sent a bad request.')

    # quit
    sock.close()


if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)
```

## Required Reading

- [Introduction to Client-Server Networking](https://learning.oreilly.com/library/view/foundations-of-python/9781430258551/9781430258544_Ch01.xhtml)
- [TCP Networking](https://learning.oreilly.com/library/view/foundations-of-python/9781430258551/9781430258544_Ch03.xhtml)
- [Threading and Python](https://realpython.com/intro-to-python-threading/#starting-a-thread)

## Available Development Tools

- [Visual Studio Code](https://code.visualstudio.com/)
  - Has multiple terminal interface for testing clients/servers (button next to the trash icon).
  - git is integrated with the program.
  - Python language highlighting and support.
  - Free for everyone.
- [PyCharm](https://www.jetbrains.com/pycharm/)
  - Enterprise level application.
  - git is integerated with the program.
  - I'm sure it has a terminal somewhere.
  - Python language highlighting and support.
  - Free for students.
- Text Editor/Command Line
  - You can do this as well.

## Python2 vs. Python3
Python3 was released in 2008. Because version 3 was not backwards compatible with version 2, people used to argue which was better. Mark G. Sobell has this to say about the version which version to use:

> Python is available in two main development branches: Python 2.x and Python 3.x. This chapter focuses on Python 2.x because the bulk of Python written today uses 2.x.

At the time of writing for this version of the book (2018), I find that hard to believe. Officially, python2 will not be maintained passed 2020. Also consider this, [http://py3readiness.org/](http://py3readiness.org/) shows 360/360 most popular packages have upgraded to Python3 (Spring 2019 it was 359/360)

The Evi Nemeth sysadmin book has this to say about which version to use:

> For new scripting work or for those new to Python altogether, it makes sense to jump directly to Python 3. That's the syntax we show in this chapter, though in fact it's only the print lines that vary between Python 2 and Python 3 in our simple examples.

Indeed, we must go with Python 3.  
Also, anyone who tells you to use version 2 make sure to inform them politely and sincerely that they are indeed incorrect, should change everything they believe, and that you are right 100% regardless of their argument. Or whatever.
