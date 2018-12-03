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
        assert isinstance(other, BoundingBox)

        x_overlaps =  self.top_right().x > other.top_left().x and other.top_right().x > self.top_left().x
        y_overlaps = self.bottom_left().y > other.top_left().y and other.bottom_left().y > self.top_left().y

        return x_overlaps and y_overlaps

        
        
class GameObject:
    def __init__(self, canvas, x1, y1, x2, y2, velocity=Point(0, 0)):
        self.canvas = canvas
        self.canvas_object = None #canvas.create_rectangle(x1, y1, x2, y2, fill="black")
        self.bounding_box = BoundingBox(Point(x1, y1), x2 - x1, y2 - y1)
        self.velocity = velocity

    def update(self):
        self.bounding_box.origin += self.velocity
        self.canvas.move(self.canvas_object, self.velocity.x, self.velocity.y)

    def get_position(self):
        return self.canvas.coords(self.canvas_object)

    def intersects(self, other):
        assert isinstance(other, GameObject)

        return self.bounding_box.intersects(other.bounding_box)

class Paddle(GameObject):

    PLAYER_ONE = 1
    PLAYER_TWO = 2

    def __init__(self, canvas, x1, y1, x2, y2, speed=10):
        super().__init__(canvas, x1, y1, x2, y2)
        self.canvas_object = canvas.create_rectangle(x1, y1, x2, y2, fill="black")  
        self.speed = speed

    @staticmethod
    def get_player(canvas, player, speed=10):
        """Factory method for creating a player paddle."""
        if player == Paddle.PLAYER_ONE:
            return Paddle(canvas, 25, 180, 35, 220, speed)
        else:
            return Paddle(canvas, 765, 180, 775, 220, speed)

    def move_up(self):
        self.velocity = Point(0, -self.speed)

    def move_down(self):
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
        self.pad1 = Paddle.get_player(self.canvas, Paddle.PLAYER_ONE)
        self.pad2 = Paddle.get_player(self.canvas, Paddle.PLAYER_TWO)

        window.bind('<KeyPress>', lambda event: self.handle_key_pressed(event))
        window.bind('<KeyRelease>', lambda event: self.handle_key_released(event))

    def handle_key_pressed(self, event):
        key = event.keysym.lower()

        if key == 'w':
            self.pad1.move_up()
        elif key == 's':
            self.pad1.move_down()

        if key == 'up':
            self.pad2.move_up()            
        elif key == 'down':
            self.pad2.move_down()
        
    def handle_key_released(self, event):
        key = event.keysym.lower()
        
        if key == 'w' or key == 's':
            self.pad1.velocity = Point()

        if key == 'up' or key == 'down':
            self.pad2.velocity = Point()

    def physics(self):
        x1, y1, x2, y2 = self.ball.get_position()
        pad1_x1, pad1_y1, pad1_x2, pad1_y2 = self.pad1.get_position()
        pad2_x1, pad2_y1, pad2_x2, pad2_y2 = self.pad2.get_position()

    # Check if ball has collided with a paddle.
        if self.ball.intersects(self.pad1) or self.ball.intersects(self.pad2):
            self.ball.velocity.x *= -1

        # TODO: Second paddle
        # TODO: Bounding box
        
    # Check if ball past upper or lower screen bounds. 
        if y1 <= 0 or y2 >= 400:
             self.ball.velocity.y *= -1

        if x1 <= 0 or x2 >= 800:
             self.ball.velocity.x *= -1

        if pad1_y1 < 0 or pad2_y2 > 400:
            self.pad1.velocity = Point()

        if pad2_y1 < 0 or pad2_y2 > 400:
            self.pad2.velocity = Point()

        

    def run(self):
        self.ball.update()
        self.pad1.update()
        self.pad2.update()
        self.physics()
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

