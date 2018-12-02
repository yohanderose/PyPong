from tkinter import *

class Paddle(object):
    def __init__(self, canvas, player):
        self.canvas = canvas
        if player == 1:
            self.pad = canvas.create_rectangle(25, 180, 35, 220, fill="black")
        else:
            self.pad = canvas.create_rectangle(765, 180, 775, 220, fill="black")            

    def move_up(self, event):
        self.canvas.move(self.pad, 0, -20)

    def move_down(self, event):
        self.canvas.move(self.pad, 0, 20)

    def get_position(self):
        return self.canvas.coords(self.pad)

class Ball:
    # TODO: calculate diagonal speed so that diagonal speed the same as speed.

    def __init__(self, canvas, x1, y1, x2, y2, speed):
        self.canvas = canvas
        self.ball = canvas.create_oval(x1, y1, x2, y2, fill="red")
        self.dx = speed
        self.dy = speed
    
    def move(self):
        self.canvas.move(self.ball, self.dx, self.dy)
    
    def get_position(self):
        return self.canvas.coords(self.ball)


class Manager(object):
    def __init__(self, window, canvas):
        self.window = window
        self.canvas = canvas
        self.ball = Ball(self.canvas, 100, 100, 112, 112, speed=3)
        self.pad1 = Paddle(self.canvas, 1)
        self.pad2 = Paddle(self.canvas, 2)

        window.bind('<w>', self.pad1.move_up)
        window.bind('<s>', self.pad1.move_down)
        window.bind('<Up>', self.pad2.move_up)
        window.bind('<Down>', self.pad2.move_down)

    def physics(self):
        x1, y1, x2, y2 = self.ball.get_position()
        pad1_x1, pad1_y1, pad1_x2, pad1_y2 = self.pad1.get_position()
        pad2_x1, pad2_y1, pad2_x2, pad2_y2 = self.pad2.get_position()

    # Check if ball has collided with a paddle.
        if (pad1_x1 <= x1 <= pad1_x2 and pad1_y1 <= y1 + ((y2-y1)/2) <= pad1_y2):
            self.ball.dx *= -1

        # TODO: Second paddle
        # TODO: Bounding box
        # TODO: Paddle controls
        
    # Check if ball past upper or lower screen bounds. 
        if y1 <= 0 or y2 >= 400:
             self.ball.dy *= -1

        if x1 <= 0 or x2 >= 800:
             self.ball.dx *= -1

        

    def run(self):
        self.physics()
        self.ball.move()
        self.canvas.after(16, self.run)
        

def main():
    
    # Setup.
    window = Tk()
    window.title("Pong")
    window.resizable(False,False)
    canvas = Canvas(window, width = 800, height = 400)
    canvas.pack()

    # Main game.

    man = Manager(window, canvas)
    man.run()
    window.mainloop()

if __name__ == "__main__":
    main()

