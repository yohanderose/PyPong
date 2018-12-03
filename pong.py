from tkinter import *

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else: # other is a scalar
            return Point(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else: # other is a scalar
            return Point(self.x - other, self.y - other)

    def __eq__(self, other):
        assert isinstance(other, Point)

        return self.x == other.x and self.y == other.y

class BoundingBox:
    def __init__(self, origin, width, height):
        self.origin = origin
        self.width = width
        self.height = height

    def top_left(self):
        return self.origin.copy()

    def top_right(self):
        return Point(self.origin.x + self.width, self.origin.y)

    def bottom_left(self):
        return Point(self.origin.x, self.origin.y + self.height)
        
    def bottom_right(self):
        return Point(self.origin.x + self.width, self.origin.y + self.height)

    def intersects(self, other):
        assert other is BoundingBox

        if self.top_left().x < other.bottom_right().x and self.top_left().y < other.bottom_right().y:
            return True

        if self.top_right().x > other.bottom_left().x and self.top_right().y < other.bottom_left().y:
            return True

        if self.bottom_left().x < other.top_right().x and self.bottom_left().y > other.top_right().y:
            return True

        if self.bottom_right().x > other.top_left().x and self.bottom_right().y > other.top_left().y:
            return True

        return False
        
        
class GameObject:
    def __init__(self, canvas, x1, y1, x2, y2, velocity=Point(0, 0)):
        self.canvas = canvas
        self.canvas_object = canvas.create_rectangle(x1, y1, x2, y2, fill="black")
        self.bounding_box = BoundingBox(Point(x1, y1), x2 - x1, y2 - y1)
        self.velocity = velocity

    def move(self):
        self.bounding_box.origin + self.velocity
        self.canvas.move(self.canvas_object, self.velocity.x, self.velocity.y)

    def get_position(self):
        return self.canvas.coords(self.canvas_object)    

class Paddle(GameObject):
    PLAYER_ONE = 1
    PLAYER_TWO = 2

    def __init__(self, canvas, player, speed=20):
        if player == Paddle.PLAYER_ONE:
            x1 = 25
            y1 = 180
            x2 = 35
            y2 = 220
        else:
            x1 = 765
            y1 = 180
            x2 = 775
            y2 = 220
        
        super().__init__(canvas, x1, y1, x2, y2)
        self.canvas_object = canvas.create_rectangle(x1, y1, x2, y2, fill="black")  
        self.speed = speed      

    def move_up(self, event):
        self.velocity = Point(0, -self.speed)

    def move_down(self, event):
        self.velocity = Point(0, self.speed)

class Ball(GameObject):
    # TODO: calculate diagonal speed so that diagonal speed the same as speed.

    def __init__(self, canvas, x1, y1, x2, y2, speed):
        super().__init__(canvas, x1, y1, x2, y2, velocity=Point(speed, speed))
        
        self.canvas_object = canvas.create_oval(x1, y1, x2, y2, fill="red")


class Manager(object):
    def __init__(self, window, canvas):
        self.window = window
        self.canvas = canvas
        self.ball = Ball(self.canvas, 100, 100, 112, 112, speed=3)
        self.pad1 = Paddle(self.canvas, Paddle.PLAYER_ONE)
        self.pad2 = Paddle(self.canvas, Paddle.PLAYER_TWO)

        window.bind('<KeyPress>', self.handle_key_pressed)
        window.bind('<KeyRelease>', self.handle_key_released)

    def handle_key_pressed(self, event):
        print('%s pressed' % event.char)

        if event.char == 'w':
            self.pad1.move_up()
        elif event.char == 's':
            self.pad1.move_down()

        if event.char == 'up':
            self.pad2.move_up()            
        elif event.char == 'down':
            self.pad2.move_down()
        
    def handle_key_released(self, event):
        print('%s released' % event.char)

        if event.char == 'w' or event.char == 's':
            self.pad1.velocity = Point()

        if event.char == 'up' or event.char == 'down':
            self.pad2.velocity = Point()

    def physics(self):
        x1, y1, x2, y2 = self.ball.get_position()
        pad1_x1, pad1_y1, pad1_x2, pad1_y2 = self.pad1.get_position()
        pad2_x1, pad2_y1, pad2_x2, pad2_y2 = self.pad2.get_position()

    # Check if ball has collided with a paddle.
        if (pad1_x1 <= x1 <= pad1_x2 and pad1_y1 <= y1 + ((y2-y1)/2) <= pad1_y2):
            self.ball.velocity.x *= -1

        # TODO: Second paddle
        # TODO: Bounding box
        # TODO: Paddle controls
        
    # Check if ball past upper or lower screen bounds. 
        if y1 <= 0 or y2 >= 400:
             self.ball.velocity.y *= -1

        if x1 <= 0 or x2 >= 800:
             self.ball.velocity.x *= -1

        

    def run(self):
        self.physics()
        self.ball.move()
        self.pad1.move()
        self.pad2.move()
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

