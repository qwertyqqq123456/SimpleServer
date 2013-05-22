import socket
from random import randrange

class Client:
    
    def __init__(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect(("54.214.135.159", 36666))
        print "Client initialization completed: Conected to Server."
    
    def sendrecv(self, message):
        self.__sock.send(message)
        response = self.__sock.recv(1024)
        if not response:
            print "not data: socket is closing."
            self.__sock.close()
            return None
        else:
            return response
    
if __name__ == "__main__":
    
    totalnumber = 5000
    times = 5000
    c_dict = {}
    for i in range(1, (totalnumber / 2) + 1):
        reg_message = "R#Client{0}#Client{1}".format(i, (i + totalnumber / 2))
        c_dict[i] = Client()
        print "Client Received:", c_dict[i].sendrecv(reg_message)
    for i in range((totalnumber / 2) + 1, totalnumber + 1):
        reg_message = "R#Client{0}#Client{1}".format(i, (i - totalnumber / 2))
        c_dict[i] = Client()
        print "Client Received:", c_dict[i].sendrecv(reg_message)
    
    for j in range(times):
        randnumber_1 = randrange(1, totalnumber + 101)
        randnumber_2 = randrange(1, totalnumber)
        if randnumber_1 % 2 == 0:
            msg = "D#{0}#Send#Red#20".format(randnumber_2) 
        else:
            msg = "D#{0}#Reply##".format(randnumber_2)
        print "Client Received:", c_dict[randnumber_2].sendrecv(msg)
        
    print "Over"
           

