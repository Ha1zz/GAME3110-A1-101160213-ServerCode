import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      #data = json.load(data)
      position = json.loads(json.dumps(data))
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
         #if 'updateposition' in data:
            #print('CHECK:', data)
            #clients[addr]['position'] = position['position']
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['position'] = 0
            #clients[addr]['color'] = 0
            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
            #for c in clients:
               #for d in clients:
                  #message_all = {"cmd": 0,"player":{"id":str(d)}}
                  #m_all = json.dumps(message_all)
                  #sock.sendto(bytes(m_all,'utf8'), (c[0],c[1]))
            #clients[addr]['position'] = position['position']


def cleanClients(sock):
   while True:
        ExtGameState = {"cmd": 2, "players": []}
        player1 = {}
        for c in list(clients.keys()):
            if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
                print('Dropped Client: ', c)
                player1['id'] = str(c)
                ExtGameState['players'].append(player1)
                clients_lock.acquire()
                del clients[c]
                clients_lock.release()
        #ExtGameState = {"cmd": 2, "players": []}
        #ExtGameState['players'].append(player1)
        exit_all = json.dumps(ExtGameState)
        if (len(ExtGameState) > 0):
            for d in clients:
                sock.sendto(bytes(exit_all,'utf8'), (d[0],d[1]))
        time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         #clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         #clients[c]['position'] = 0
         player['id'] = str(c)
         #player['color'] = clients[c]['color']
         player['position'] = clients[c]['position']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
