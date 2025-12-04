import socket
import threading
import time

HOST = '192.168.0.3'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def recv_loop():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break

            received_time = time.time()

            # decodificar y separar mensaje timestamp
            try:
                msg, ts = data.decode().split("|")
                latency = (received_time - float(ts)) * 1000
                print(f"{msg}   [{round(latency,2)} ms]")
            except:
                print(data.decode())

        except:
            break

threading.Thread(target=recv_loop, daemon=True).start()

name = input("Ingresa tu nombre: ")
while True:
    msg = input()
    if msg:
        timestamp = time.time()
        client.sendall(f"{name}: {msg}|{timestamp}".encode())
