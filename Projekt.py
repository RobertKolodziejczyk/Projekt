import random
import socket
from ursina import *

host = "192.168.10.178"
port = 1345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    # Tries to connect to server, if it's not running it lets the user know
    try:
        client.connect((host, port))
        break

    except ConnectionRefusedError:
        print("Server is not currently running... ")

# Variable to check if the game should be run or not
game = False

app = Ursina(size=(1600, 900))

enemies = []

colors = [color.green, color.red, color.blue, color.cyan, color.black]

score = 0


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


def write(initials, score):
    try:
        client.send(bytes(initials, "utf-8"))
        client.send(bytes(str(score), "utf-8"))
    except ConnectionError:
        print("You lost connection with the server")
    texts = recieve_high_scores()
    global text1
    global text2
    global text3
    destroy(text1)
    destroy(text2)
    destroy(text3)
    text1 = texts[0]
    text2 = texts[1]
    text3 = texts[2]


def on_mouse_click():
    destroy(button)
    global game
    game = True
    global player
    destroy(player)
    player = Player(0.1, (0, 0))


def submit():
    global score
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
    global text
    destroy(text)
    global score
    score = 0
    text = Text(score)


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
    text="Click to Start",
    color=color.clear,
    highlight_color=color.clear,
    on_click=on_mouse_click,
)
text = Text(score)

initials = InputField(
    y=-0.12,
    limit_content_to="abcdefghijklmnopqrstuvxyz",
    character_limit=3,
    max_lines=1,
)

submit_button = Button(
    text="Submit",
    scale=0.1,
    color=color.red,
    y=-0.26,
    on_click=submit,
)
initials.disable()
submit_button.disable()

texts = recieve_high_scores()

text1 = texts[0]
text2 = texts[1]
text3 = texts[2]


def update():
    global score
    global text
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
                destroy(text)
                text = Text(score)
                break
            elif hit_info.hit and player.radius < enemy.radius:
                game = False

        if game == False:
            for enemy in enemies:
                destroy(enemy)
            enemies.clear()

            global initials
            global submit_button
            initials.enable()
            submit_button.enable()


app.run()
