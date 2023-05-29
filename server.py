import socket
import threading
import csv
from time import sleep

host = "192.168.10.178"
port = 1345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()


def high_score(client):
    initials = client.recv(1024).decode("utf-8").upper()
    score = client.recv(1024).decode("utf-8")
    if score:
        with open("high_scores.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([initials, score])
    handle(client)


def send_high_score(client):
    highest_scores = ["", 0, "", 0, "", 0]

    with open("high_scores.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            initials = row[0]
            score = int(row[1])
            if score >= highest_scores[1]:
                highest_scores[3] = highest_scores[1]
                highest_scores[2] = highest_scores[0]
                highest_scores[1] = score  # mnhgbfvdsca<
                highest_scores[0] = initials
            elif score <= highest_scores[1] and score >= highest_scores[3]:
                highest_scores[5] = highest_scores[3]
                highest_scores[4] = highest_scores[2]
                highest_scores[3] = score
                highest_scores[2] = initials
            elif (
                score <= highest_scores[1]
                and score <= highest_scores[3]
                and score >= highest_scores[5]
            ):
                highest_scores[5] = score
                highest_scores[4] = initials

            else:
                continue

        client.send(bytes(highest_scores[0] + " " + str(highest_scores[1]), "utf-8"))
        sleep(2)
        client.send(bytes(highest_scores[2] + " " + str(highest_scores[3]), "utf-8"))
        sleep(2)
        client.send(bytes(highest_scores[4] + " " + str(highest_scores[5]), "utf-8"))


def handle(client):
    send_high_score(client)
    high_score(client)


def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with " + str(address))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
