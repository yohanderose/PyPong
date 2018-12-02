from tkinter import *

class Paddle(object):

    def __init__(self, canvas, player):
        if player == 1:


class Ball:
    # TODO: calculate diagonal speed so that diagonal speed the same as speed.

    def __init__(self, canvas, x1, y1, x2, y2, speed):
        self.canvas = canvas
        self.ball = canvas.create_oval(x1, y1, x2, y2, fill="red")
        self.dx = speed
        self.dy = speed

    def update(self):  
        self.canvas.move(self.ball, self.dx, self.dy)
        self.bounce()
        self.canvas.after(16, self.update)

    def bounce(self):
        x1, y1, x2, y2 = self.canvas.coords(self.ball)

        # Check if ball past upper or lower bounds 
        if y1 <= 0 or y2 >= 400:
             self.dy *= -1

        if x1 <= 0 or x2 >= 800:
             self.dx *= -1
           


def main():
    
    window = Tk()
    window.title("Pong")
    window.resizable(False,False)
    canvas = Canvas(window, width = 800, height = 400)
    canvas.pack()

    ball = Ball(canvas, 100, 100, 112, 112, 5)
    ball.update()

    window.mainloop()


if __name__ == "__main__":
    main()

