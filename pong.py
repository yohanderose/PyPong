from tkinter import *
import random
# TODO: Scoring
# TODO: Document Code-


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

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else: # other is a scalar
            return Point(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

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

        x_overlaps = self.top_right().x > other.top_left().x and other.top_right().x > self.top_left().x
        y_overlaps = self.bottom_left().y > other.top_left().y and other.bottom_left().y > self.top_left().y

        return x_overlaps and y_overlaps


class GameObject:
    def __init__(self, canvas, x1, y1, x2, y2, velocity=Point(0, 0)):
        self.canvas = canvas
        self.canvas_object = None
        self.bounding_box = BoundingBox(Point(x1, y1), x2 - x1, y2 - y1)
        self.velocity = velocity

    def update(self):
        self.move(self.velocity)

    def move(self, delta_pos):
        """Move the object by moving its origin to 'origin + delta_pos'"""
        self.bounding_box.origin += delta_pos
        self.canvas.move(self.canvas_object, delta_pos.x, delta_pos.y)

    def get_position(self):
        return self.canvas.coords(self.canvas_object)

    def intersects(self, other):
        assert isinstance(other, GameObject)

        return self.bounding_box.intersects(other.bounding_box)

    def is_out_of_bounds(self):
        x1, y1, x2, y2 = self.get_position()

        return x1 < 0 or x2 > self.canvas.winfo_width() or\
            y1 < 0 or y2 > self.canvas.winfo_height()


class Paddle(GameObject):
    PLAYER_ONE = 1
    PLAYER_TWO = 2

    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 40

    def __init__(self, canvas, x1, y1, x2, y2, speed=8):
        super().__init__(canvas, x1, y1, x2, y2)
        self.canvas_object = canvas.create_rectangle(x1, y1, x2, y2, fill="black")  
        self.speed = speed

    @staticmethod
    def get_paddle(canvas, player, speed=8):
        """Factory method for creating a player paddle."""
        x_offset = 25

        if player == Paddle.PLAYER_ONE:
            x = x_offset
            y = (canvas.winfo_height() - Paddle.PADDLE_HEIGHT) / 2
            return Paddle(canvas, x, y, x + Paddle.PADDLE_WIDTH, y + Paddle.PADDLE_HEIGHT, speed)
        else:
            x = canvas.winfo_width() - x_offset - Paddle.PADDLE_WIDTH
            y = (canvas.winfo_height() - Paddle.PADDLE_HEIGHT) / 2
            return Paddle(canvas, x, y, x + Paddle.PADDLE_WIDTH, y + Paddle.PADDLE_HEIGHT, speed)

    def move_up(self):
        self.velocity = Point(0, -self.speed)

    def move_down(self):
        self.velocity = Point(0, self.speed)

    def update(self):
        super().update()

        _, y1, _, y2 = self.get_position()

        # keep paddle on screen
        dy = 0

        if y1 < 0:
            dy = -y1
        elif y2 > self.canvas.winfo_height():
            dy = self.canvas.winfo_height() - y2

        self.move(Point(0, dy))


class Ball(GameObject):
    BALL_SIZE = 12

    def __init__(self, canvas, x1, y1, x2, y2, speed):
        """Create a ball at the specified location.

        The ball starts moving in a random direction.
        """
        x_dir = -1 if random.gauss(0, 1) < 0 else 1
        y_dir = -1 if random.gauss(0, 1) < 0 else 1

        initial_velocity = speed * Point(x_dir, y_dir)

        super().__init__(canvas, x1, y1, x2, y2, velocity=initial_velocity)
        
        self.canvas_object = canvas.create_oval(x1, y1, x2, y2, fill="red")

    @staticmethod
    def get_centred_ball(canvas, speed=3):
        """Get a ball placed at the centre of the game window."""
        x = canvas.winfo_width() / 2 - Ball.BALL_SIZE / 2
        y = canvas.winfo_height() / 2 - Ball.BALL_SIZE / 2
        
        return Ball(canvas, x, y, x + Ball.BALL_SIZE, y + Ball.BALL_SIZE, speed=speed)

    def update(self):
        super().update()

        _, y1, _, y2 = self.get_position()

        # Check if ball past upper or lower screen bounds.
        if y1 <= 0 or y2 >= self.canvas.winfo_height():
            self.velocity.y *= -1


class PongGame:
    """A game of Pong.

    You can add 'spin' to the ball by hitting the ball with your paddle while moving.
    Each hit speeds up the ball.

    Call run() to start the game.
    """
    def __init__(self, spin=0.2, hit_speedup=1.05, ball_max_speed=10, window_width=800, window_height=400):
        """Set up a game of Pong.

        Arguments:
            spin: ratio of a paddle's y velocity that will be added to the ball's velocity as 'spin' when the ball
                  is hit.
            hit_speedup: multiplier for the ball's x velocity when it bounces off a paddle.
            ball_max_speed: the max speed in either of the x or y axes.
            window_width: the width of the game window. min of 600.
            window_height: the height of the game window. min of 300.
        """
        window = Tk()
        window.title("Pong")
        window.resizable(False, False)
        window.bind('<KeyPress>', lambda event: self.handle_key_pressed(event))
        window.bind('<KeyRelease>', lambda event: self.handle_key_released(event))

        window_width = max(600, window_width)
        window_height = max(300, window_height)

        canvas = Canvas(window, width=window_width, height=window_height)
        canvas.pack()
        canvas.update()

        self.window = window
        self.canvas = canvas

        # paddles and ball setup later in reset()
        self.pad1 = None
        self.pad2 = None
        self.ball = None

        self.spin = spin
        self.ball_max_speed = ball_max_speed
        self.hit_speedup = hit_speedup
        
        self.p1_score = 0
        self.p1_score_display = self.canvas.create_text(10, 10, text=str(self.p1_score))
        self.p2_score = 0        
        self.p2_score_display = self.canvas.create_text(window_width - 10, 10, text=str(self.p2_score))

        self.paused = False
        self.pause_text = self.canvas.create_text(window_width / 2, window_height / 2 - 20, text="Press Space to Start")
        self.reset()

    def reset(self):
        """Reset the game by placing the ball back in the center and the paddles in their starting positions."""
        if self.ball is not None:
            self.canvas.delete(self.ball.canvas_object)

        self.ball = Ball.get_centred_ball(self.canvas)

        if self.pad1 is not None:
            self.canvas.delete(self.pad1.canvas_object)
        if self.pad2 is not None:            
            self.canvas.delete(self.pad2.canvas_object)

        self.pad1 = Paddle.get_paddle(self.canvas, Paddle.PLAYER_ONE)
        self.pad2 = Paddle.get_paddle(self.canvas, Paddle.PLAYER_TWO)

        self.pause()

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

        if key == 'space':
            self.toggle_pause()
        if key == 'r':
            self.reset()
        
    def handle_key_released(self, event):
        key = event.keysym.lower()
        
        if key == 'w' or key == 's':
            self.pad1.velocity = Point()

        if key == 'up' or key == 'down':
            self.pad2.velocity = Point()

    def physics(self):
        if self.ball.intersects(self.pad1):
            self.ball.velocity.x *= -1 * self.hit_speedup
            self.ball.velocity.y += self.spin * self.pad1.velocity.y

            # put ball on the rhs of the paddle
            pad1_x = self.pad1.bounding_box.top_right().x
            ball_x = self.ball.bounding_box.top_left().x
            dx = pad1_x - ball_x

            self.ball.move(Point(dx, 0))

        elif self.ball.intersects(self.pad2):
            self.ball.velocity.x *= -1 * self.hit_speedup
            self.ball.velocity.y += self.spin * self.pad2.velocity.y

            # put ball on the lhs of the paddle
            pad2_x = self.pad2.bounding_box.top_left().x
            ball_x = self.ball.bounding_box.top_right().x
            dx = pad2_x - ball_x

            self.ball.move(Point(dx, 0))

        if self.ball.velocity.x > self.ball_max_speed:
            self.ball.velocity.x = self.ball_max_speed
        if self.ball.velocity.y > self.ball_max_speed:
            self.ball.velocity.y = self.ball_max_speed

        if self.ball.is_out_of_bounds():
            x1, _, x2, _ = self.ball.get_position()

            if x1 < 0:
                self.p2_score += 1
                self.reset()
            elif x2 > self.canvas.winfo_width():
                self.p1_score += 1
                self.reset()

    def toggle_pause(self):
        if self.paused:
            self.unpause()
        else:
            self.pause()

    def pause(self):
        self.paused = True
        self.canvas.itemconfig(self.pause_text, text="Press Space to Start")

    def unpause(self):
        self.paused = False
        self.canvas.itemconfig(self.pause_text, text="")

    def run(self):
        self.mainloop()
        self.window.mainloop()

    def mainloop(self):
        if not self.paused:
            self.update()

        self.canvas.after(16, self.mainloop)

    def update(self):
        self.ball.update()
        self.pad1.update()
        self.pad2.update()
        self.physics()

        self.canvas.itemconfig(self.p1_score_display, text=str(self.p1_score))
        self.canvas.itemconfig(self.p2_score_display, text=str(self.p2_score))


if __name__ == "__main__":
    game = PongGame()
    game.run()

