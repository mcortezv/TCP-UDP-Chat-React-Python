import socket
import threading
import time

HOST = "192.168.0.3"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("", 0))  # puerto aleatorio para cada cliente

# funcion que recibe mensajes y calcula latencia
def recv_loop():
    while True:
        try:
            data, addr = client.recvfrom(1024)
            received_time = time.time()

            msg, sent_time = data.decode().split("|")
            latency = (received_time - float(sent_time)) * 1000

            print(f"{msg}  (latencia: {round(latency,2)} ms)")
        except:
            continue

threading.Thread(target=recv_loop, daemon=True).start()

name = input("Ingresa tu nombre: ")

# ciclo principal para enviar mensajes
while True:
    msg = input()
    if msg:
        timestamp = time.time()
        message = f"{name}: {msg}|{timestamp}"
        client.sendto(message.encode(), (HOST, PORT))
