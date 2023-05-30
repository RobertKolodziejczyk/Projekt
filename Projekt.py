import random
import socket
from ursina import *

host = "192.168.10.178"
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

        text1 = Text(text=high_score1, position=(-0.8, 0.5))
        text2 = Text(text=high_score2, position=(-0.8, 0.45))
        text3 = Text(text=high_score3, position=(-0.8, 0.4))
        return text1, text2, text3
    except ConnectionError:
        print("You lost connection with the server")
        print("You will now enter offline mode")
        return False


def write(initials, score):
    try:
        client.send(bytes(initials, "utf-8"))
        client.send(bytes(str(score), "utf-8"))
    except ConnectionError:
        pass
    texts = recieve_high_scores()
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
    else:
        global is_connected
        is_connected = False


def on_mouse_click():
    destroy(button)
    global game
    game = True
    global player
    destroy(player)
    player = Player(0.1, (0, 0))


def submit():
    global score
    initials_prompt.disable()
    submit_button.disable()
    write(initials.text, score)
    initials.disable()
    playagain()


def playagain():
    global button
    button = Button(
        text="Ouch!, Play Again?",
        color=color.clear,
        highlight_color=color.clear,
        on_click=on_mouse_click,
    )
    global score_text
    destroy(score_text)
    global score
    score = 0
    score_text = Text(score, position=(0, 0.5))


class Circle(Entity):
    def __init__(self, radius, color, position):
        super().__init__(model="circle", color=color, scale=radius, position=position)


class Enemy(Circle):
    def __init__(self, radius, position):
        super().__init__(radius, color=random.choice(colors), position=position)
        self.xspeed = random.uniform(-1, 1)
        self.yspeed = random.uniform(-1, 1)
        self.collider = "sphere"
        self.radius = radius

    def move(self):
        self.x += self.xspeed * time.dt
        self.y += self.yspeed * time.dt

    def destroy(self):
        self.disable()
        enemies.remove(self)


class Player(Circle):
    def __init__(self, radius, position):
        super().__init__(radius, color=color.white, position=position)
        self.collider = "sphere"
        self.radius = radius


def spawn():
    values = [-7.5, 7.5, -4.5, 4.5]
    value = random.choice(values)
    if abs(value) == 7.5:
        y = random.uniform(-4.5, 4.5)
        x = value
    else:
        y = value
        x = random.uniform(-7.5, 7.5)

    radius = random.randint(-1, 3) / 10
    enemies.append(Enemy(player.radius + radius, (x, y)))


player = Player(0.1, (0, 0))
button = Button(
    text="Avoid bigger dots eat smaller dots \n Click to Start",
    color=color.clear,
    highlight_color=color.clear,
    on_click=on_mouse_click,
)
score_text = Text(score, position=(0, 0.5))

initials = InputField(
    y=-0.12,
    limit_content_to="abcdefghijklmnopqrstuvxyz",
    character_limit=3,
    max_lines=1,
)

initials_prompt = Text(text="Enter your initials", position=(-0.15, 0))

submit_button = Button(
    text="Submit",
    scale=0.1,
    color=color.red,
    y=-0.26,
    on_click=submit,
)
initials.disable()
initials_prompt.disable()
submit_button.disable()

texts = recieve_high_scores()

if texts:
    text1 = texts[0]
    text2 = texts[1]
    text3 = texts[2]
else:
    is_connected = False


def update():
    global score
    global score_text
    global game
    if game == True:
        spawn()

        player.position = Vec2(mouse.x, mouse.y) * 8

        for enemy in enemies:
            if abs(enemy.x) > 10 or abs(enemy.y) > 7:
                enemy.destroy()
            enemy.move()

            hit_info = player.intersects(enemy)
            if hit_info.hit and player.radius >= enemy.radius:
                enemy.destroy()
                player.radius += 0.01
                player.scale = player.radius
                score += 1
                destroy(score_text)
                score_text = Text(score, position=(0, 0.5))
                break
            elif hit_info.hit and player.radius < enemy.radius:
                game = False

        if game == False:
            for enemy in enemies:
                destroy(enemy)
            enemies.clear()

            if is_connected == True:
                global initials
                global submit_button
                initials.enable()
                submit_button.enable()
                initials_prompt.enable()
            else:
                playagain()


app.run()
