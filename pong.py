from tkinter import *
# TODO: Scoring
# TODO: Document Code


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
        self.canvas_object = None
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

    def is_out_of_bounds(self):
        x1, y1, x2, y2 = self.get_position()

        return x1 < 0 or x2 > self.canvas.winfo_width() or\
            y1 < 0 or y2 > self.canvas.winfo_height()


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

    def update(self):
        super().update()

        x1, y1, x2, y2 = self.get_position()

        # keep paddle on screen
        dy = 0

        if y1 < 0:
            dy = -y1
        elif y2 > self.canvas.winfo_height():
            dy = self.canvas.winfo_height() - y2

        self.canvas.move(self.canvas_object, 0, dy)
        self.bounding_box.origin += Point(0, dy)


class Ball(GameObject):
    def __init__(self, canvas, x1, y1, x2, y2, speed):
        super().__init__(canvas, x1, y1, x2, y2, velocity=Point(speed, speed))
        
        self.canvas_object = canvas.create_oval(x1, y1, x2, y2, fill="red")

    def update(self):
        super().update()

        x1, y1, x2, y2 = self.get_position()

        # Check if ball past upper or lower screen bounds.
        if y1 <= 0 or y2 >= self.canvas.winfo_height():
            self.velocity.y *= -1

        # if x1 <= 0 or x2 >= self.canvas.winfo_width():
        #     self.velocity.x *= -1


class PongGame:
    def __init__(self, window, canvas, friction=0.8, ball_max_speed=10):
        self.window = window
        self.canvas = canvas
        self.ball = Ball(self.canvas, 400, 200, 412, 212, speed=3)
        self.pad1 = Paddle.get_player(self.canvas, Paddle.PLAYER_ONE)
        self.pad2 = Paddle.get_player(self.canvas, Paddle.PLAYER_TWO)
        self.friction = friction  # How much of a paddle's velocity will be added to the ball's velocity as 'spin'.
        self.ball_max_speed = ball_max_speed

        self.p1_score = 0
        self.p1_score_display = self.canvas.create_text(10, 10, text=str(self.p1_score))
        self.p2_score = 0
        w = self.canvas.winfo_width()
        ## TODO: calculate text pos instead of hardcoding it
        self.p2_score_display = self.canvas.create_text(790, 10, text=str(self.p2_score))

        window.bind('<KeyPress>', lambda event: self.handle_key_pressed(event))
        window.bind('<KeyRelease>', lambda event: self.handle_key_released(event))

        self.paused = False
            ## TODO: calculate pos instead of hardcoding it"Press Space to Start"
        self.pause_text = self.canvas.create_text(400, 180, text="Press Space to Start")
        self.toggle_pause()

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
        
    def handle_key_released(self, event):
        key = event.keysym.lower()
        
        if key == 'w' or key == 's':
            self.pad1.velocity = Point()

        if key == 'up' or key == 'down':
            self.pad2.velocity = Point()

    def physics(self):
        if self.ball.intersects(self.pad1):
            self.ball.velocity.x *= -1
            self.ball.velocity.y += (1 - self.friction) * self.pad1.velocity.y
        elif self.ball.intersects(self.pad2):
            self.ball.velocity.x *= -1
            self.ball.velocity.y += (1 - self.friction) * self.pad2.velocity.y

        if self.ball.velocity.x > self.ball_max_speed:
            self.ball.velocity.x = self.ball_max_speed
        if self.ball.velocity.y > self.ball_max_speed:
            self.ball.velocity.y = self.ball_max_speed

        if self.ball.is_out_of_bounds():
            x1, _, x2, _ = self.ball.get_position()

            if x1 < 0:
                self.p2_score += 1
                self.serve()
            elif x2 > self.canvas.winfo_width():
                self.p1_score += 1
                self.serve()

    def serve(self):
        self.canvas.delete(self.ball.canvas_object)

        ball_width = 12
        x = self.canvas.winfo_width() / 2 - ball_width / 2
        y = self.canvas.winfo_height() / 2 - ball_width / 2
        self.ball = Ball(self.canvas, x, y, x + ball_width, y + ball_width, speed=3)

        self.canvas.delete(self.pad1.canvas_object)
        self.pad1 = Paddle.get_player(self.canvas, Paddle.PLAYER_ONE)
        self.canvas.delete(self.pad2.canvas_object)
        self.pad2 = Paddle.get_player(self.canvas, Paddle.PLAYER_TWO)


        self.toggle_pause()

    def toggle_pause(self):
        self.paused = not self.paused

        if self.paused:
            self.canvas.itemconfig(self.pause_text, text="Press Space to Start")
        else:
            self.canvas.itemconfig(self.pause_text, text="")

    def run(self):
        if not self.paused:
            self.update()

        self.canvas.after(16, self.run)

    def update(self):
        self.ball.update()
        self.pad1.update()
        self.pad2.update()
        self.physics()

        self.canvas.itemconfig(self.p1_score_display, text=str(self.p1_score))
        self.canvas.itemconfig(self.p2_score_display, text=str(self.p2_score))
        

def main():
    # Setup.
    window = Tk()
    window.title("Pong")
    window.resizable(False,False)
    canvas = Canvas(window, width=800, height=400)
    canvas.pack()

    # Main game.
    game = PongGame(window, canvas)
    game.run()
    window.mainloop()

if __name__ == "__main__":
    main()

