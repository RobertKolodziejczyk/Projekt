import random
import socket
from ursina import *

host = ""
port = 1345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    # Tries to connect to server, if it's not up it lets the user know
    try:
        client.connect((host, port))
        break

    except ConnectionRefusedError:
        print("Server is not currently up... ")

# Variable to check if the game should be run or not
game = False

# Creates the game window
app = Ursina(size=(1600, 900))

enemies = []

colors = [color.green, color.red, color.blue, color.cyan, color.black]

score = 0

# Variable to check if the client is connected to the server
is_connected = True


# Tries to recieve high_scores from the server, if a connection error is met, it returns False
def recieve_high_scores():
    try:
        high_score1 = client.recv(1024).decode("utf-8")
        high_score2 = client.recv(1024).decode("utf-8")
        high_score3 = client.recv(1024).decode("utf-8")

        # Puts the highscores on display at the top left corner
        text1 = Text(text=high_score1, position=(-0.8, 0.5))
        text2 = Text(text=high_score2, position=(-0.8, 0.45))
        text3 = Text(text=high_score3, position=(-0.8, 0.4))
        return text1, text2, text3
    except ConnectionError:
        print("You lost connection with the server")
        print("You will now enter offline mode")
        return False


def send_high_score(initials, score):
    # Tries to send the initials and score to the server
    try:
        client.send(bytes(initials, "utf-8"))
        client.send(bytes(str(score), "utf-8"))
    # If a connection error is met it passes
    except ConnectionError:
        pass

    # Calls the recieve_high_scores function and stores it in the variable texts
    texts = recieve_high_scores()

    # If texts contains something it destroys the old high_scores and updates with the new ones
    if texts:
        global text1
        global text2
        global text3
        destroy(text1)
        destroy(text2)
        destroy(text3)
        text1 = texts[0]
        text2 = texts[1]
        text3 = texts[2]

    # If texts is False the is_connected variable is set to False
    else:
        global is_connected
        is_connected = False


# The function that is run when the Button is pressed
def on_mouse_click():
    # Destroys the button to prevent it from being pressed again until you've lost again
    destroy(button)

    # Sets game to True so a new game will start over
    global game
    game = True

    # Destroys the old Player entity and replaces it with a new one with the scale it starts with
    global player
    destroy(player)
    player = Player(0.1, (0, 0))


# The function that is run when the Submit Button is pressed
def submit():
    global score

    # Disables the text that prompts the user for their initials
    initials_prompt.disable()

    # Disables the Submit Button
    submit_button.disable()

    # Calls the send_high_score function with the text from the Input_Field and the score that you got
    send_high_score(initials.text, score)

    # Disables the Input_Field
    initials.disable()

    # Calls the playagain function
    playagain()


# The function to reset the game
def playagain():
    global button

    # Creates a Button that asks if the player wants to play again
    button = Button(
        text="Ouch!, Play Again?",
        color=color.clear,
        highlight_color=color.clear,
        # When the Button is clicked the on_mouse_click function is called
        on_click=on_mouse_click,
    )
    # Resets the score and the score display
    global score_text
    destroy(score_text)
    global score
    score = 0
    score_text = Text(score, position=(0, 0.5))


# Creates a Class Circle that inherits from the Entity Class
class Circle(Entity):
    def __init__(self, radius, color, position):
        super().__init__(model="circle", color=color, scale=radius, position=position)


# Creates the Enemy Class that inherits from the Circle Class
class Enemy(Circle):
    def __init__(self, radius, position):
        super().__init__(radius, color=random.choice(colors), position=position)

        # Sets the speed of the enemy to a random float between -1 and 1
        self.xspeed = random.uniform(-1, 1)
        self.yspeed = random.uniform(-1, 1)

        # Sets up the collider to check for collisions with the player
        self.collider = "sphere"
        # Makes an attribute called radius to be used in calculations later
        self.radius = radius

    # Moves the enemy on the x and y axis by the speed that was randomly chosen
    def move(self):
        self.x += self.xspeed * time.dt
        self.y += self.yspeed * time.dt

    # Disables the enemy and removes it from the enemies list
    def destroy(self):
        self.disable()
        enemies.remove(self)


# Creates the Player Class that inherits from the Circle Class
class Player(Circle):
    def __init__(self, radius, position):
        super().__init__(radius, color=color.white, position=position)

        # Sets up the collider to check for collisions with the enemies
        self.collider = "sphere"
        # Makes an attribute called radius to be used in calculations later
        self.radius = radius


# Function that spawns the enemies
def spawn():
    # Sets up values that will be used for coordinates, these coordinates are just outside the game window
    values = [-7.5, 7.5, -4.5, 4.5]

    # Chooses a random value from the values list
    value = random.choice(values)

    """ If the absolute value of value is 7.5 the x coordinates is set to value 
    and the y coordinates is chosen as a random float between -4.5 and 4.5.
    Otherwise the y coordinate is set as the value and the x coordinate is chosen 
    as a random float between -7.5 and 7.5"""
    if abs(value) == 7.5:
        y = random.uniform(-4.5, 4.5)
        x = value
    else:
        y = value
        x = random.uniform(-7.5, 7.5)

    """ Creates random radius of either -0.1, 0, 0.1, 0.2 or 0.3 the reason for more positive numbers 
    are so that most enemies will be bigger than the player"""
    radius = random.randint(-1, 3) / 10

    """ Creates an enemy with the postion of x,y and a radius that scales with the players radius 
    and adds that enemy to the enemies list"""
    enemies.append(Enemy(player.radius + radius, (x, y)))


# Creates the player
player = Player(0.1, (0, 0))

# Creates the button that once pressed will start the game
button = Button(
    text="Avoid bigger dots eat smaller dots \n Click to Start",
    color=color.clear,
    highlight_color=color.clear,
    on_click=on_mouse_click,
)

# Creates a text that displays the score
score_text = Text(score, position=(0, 0.5))

# Creates an InputField in which the player will write their initials
initials = InputField(
    y=-0.12,
    limit_content_to="abcdefghijklmnopqrstuvxyz",
    character_limit=3,
    max_lines=1,
)

# Creates a text that will prompts the user to enter their initials in the InputField
initials_prompt = Text(text="Enter your initials", position=(-0.15, 0))

# Creates the Button that will submit the initials from the InputField to the server
submit_button = Button(
    text="Submit",
    scale=0.1,
    color=color.red,
    y=-0.26,
    on_click=submit,
)

# Disables these because they won't be used until later
initials.disable()
initials_prompt.disable()
submit_button.disable()

# Calls the recieve_high_scores function and stores it in the variable texts
texts = recieve_high_scores()

# If texts contains something it creates texts to display the top 3 highscores
if texts:
    text1 = texts[0]
    text2 = texts[1]
    text3 = texts[2]

# If texts is False the is_connected variable is set to False
else:
    is_connected = False


def update():
    global score
    global score_text
    global game

    # Starts the game if game == True
    if game == True:
        # Spawns the enemies
        spawn()

        # Moves the player postition towards the mouse with the speed of 8
        player.position = Vec2(mouse.x, mouse.y) * 8

        # Loops through all enemies in the enemies list
        for enemy in enemies:
            # If the position of the enemies are to far away the .destroy method is called on them
            if abs(enemy.x) > 10 or abs(enemy.y) > 7:
                enemy.destroy()

            # Calls the .move method
            enemy.move()

            # Checks if the player has collided with an enemy
            hit_info = player.intersects(enemy)
            """ If the player has collided with an enemy and the radius of the player 
            is greater or equal to the enemy it calls the .destroy method on that enemy"""
            if hit_info.hit and player.radius >= enemy.radius:
                enemy.destroy()
                """ Increases the radius and sets the scale of the player equal to the radius 
                we can't just increase the players scale as the radius attribute is used to scale up the enemies 
                according to the players radius"""
                player.radius += 0.01
                player.scale = player.radius
                # Increases the score and destroy the score_text to create a new one with the updated score
                score += 1
                destroy(score_text)
                score_text = Text(score, position=(0, 0.5))
                break
            # If the player collided with an enemy that is bigger the game is set to False
            elif hit_info.hit and player.radius < enemy.radius:
                game = False

        # If the game is False it destroys all enemies and clears the enemies list
        if game == False:
            for enemy in enemies:
                destroy(enemy)
            enemies.clear()

            # Checks if the client is connected to the server
            if is_connected == True:
                global initials
                global submit_button
                initials.enable()
                submit_button.enable()
                initials_prompt.enable()
            # If the client is not connected it skips the submitting initials part and starts over
            else:
                playagain()


app.run()
