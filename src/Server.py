import socket
import time 
import select
import Queue

devlist_pairinfo = 0
devlist_connected = 1
devlist_isalive = 2
devlist_queue = 3

devicelist = {}
devicenumber_index = {}


class Server:
    
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
        self.__sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock1.setblocking(0)
        self.__sock1.bind((ip, port))
        self.__sock1.listen(5)
        self.__inputs = [self.__sock1]
        self.__outputs = []
        self.__messageQueues = {}
        print "Server initialization done."
        
    def serve(self):
        print "The server is serving..."
        while(self.__inputs):
            print "server waiting for request..."
            readable, writable, exceptional = select.select(self.__inputs, self.__outputs, self.__inputs)
            print "accepted."
            for s in readable:
                if s is self.__sock1:
                    sock2, c_address = s.accept()
                    sock2.setblocking(0)
                    self.__inputs.append(sock2)
                    self.__messageQueues[sock2] = Queue.Queue()
                else:
                    data = s.recv(1024)
                    if data: 
                        self.__messageQueues[s].put(self.processing(data))
                        if s not in self.__outputs:
                            self.__outputs.append(s)
                    else:
                        if s in self.__outputs:
                            self.__outputs.remove(s)
                        self.__inputs.remove(s)
                        s.close()
                        
                        del self.__messageQueues[s]
            
            for s in writable:
                try:
                    msg_tosend = self.__messageQueues[s].get_nowait()
                except Queue.Empty:
                    self.__outputs.remove(s)
                else:
                    s.send(msg_tosend)
            
            for s in exceptional:
                print "handling exceptional..."
                self.__inputs.remove(s)
                if s in self.__outputs:
                    self.__outputs.remove(s)
                s.close()
                
                del self.__messageQueues[s]
                
    def processing(self, data):
        'This function processes the request'
        paralist = data.split("#")
        
        if paralist[0] == "R":          
            device_name = paralist[1]
            pairing_info = paralist[2]
            connected = False
            isalive = True
            
            if device_name not in devicelist:
                devicelist[device_name] = [pairing_info, connected, isalive]
                
                devicenumber = len(devicenumber_index) + 1
                devicenumber_index[devicenumber] = device_name
                
                if pairing_info in devicelist:
                    if devicelist[pairing_info][devlist_pairinfo] == device_name:
                                                
                        devicelist[pairing_info][devlist_connected] = True                  
                        devicelist[device_name][devlist_connected] = True 
                        devicelist[pairing_info].append(Queue.Queue(5))   
                        devicelist[device_name].append(Queue.Queue(5))  
                    else:
                        print "Some error in devicelist: [name mismatching]"
                    
                response = "{0} registered as {1}" .format(device_name, devicenumber)
            else:
                response = "{0} has already been registered.".format(device_name)
              
        
        elif paralist[0] == "D":
            sender_number = int(paralist[1])
            code = paralist[2]             
            if code == "Send":
                color = paralist[3]
                brightness = paralist[4]
                         
            if sender_number in devicenumber_index:
                sender_name = devicenumber_index[sender_number]

                if sender_name in devicelist:                  
                    if devicelist[sender_name][devlist_pairinfo] in devicelist:                  
                        if devicelist[sender_name][devlist_connected] == True \
                        and devicelist[devicelist[sender_name][devlist_pairinfo]][devlist_connected] == True:
                        
                            'Response'    
                            try:
                                response = devicelist[sender_name][devlist_queue].get(False)
                                devicelist[sender_name][devlist_queue].task_done()
                            except Queue.Empty:
                                response = "No message this time"
                                
                            response = sender_name + ": " + response
                        
                            'Send msg'
                            if code == "Send":
                                operation = "Send " + color + " " + brightness
                            elif code == "Reply":
                                operation = "Reply"
                            else:
                                print "error code"                                                          
                            # print"operation:", operation
                            
                            try:
                                devicelist[devicelist[sender_name][devlist_pairinfo]][devlist_queue].put(operation, False)
                            except Queue.Full:
                                print "The queue is full, try again later"
                                
                        else:
                            response = "Warning: This device is not connected."
                    else:
                        response = "Warning: The pair information is not recorded."
                else:
                    response = "Error: This email appears in index list but not the devicelist."               
            else:
                response = "Error: Didn't find this device number in system!"
        
        elif paralist[0] == "N":
            sender_number = int(paralist[1])
            if sender_number in devicenumber_index:
                sender_name = devicenumber_index[sender_number]
                if sender_name in devicelist:                  
                    'Response'    
                    try:
                        response = devicelist[sender_name][devlist_queue].get(False)
                        devicelist[sender_name][devlist_queue].task_done()
                    except Queue.Empty:
                        response = "No message this time"
                                
                    response = sender_name + ": " + response                   
                else:
                    response = "Error: This email appears in index list but not the devicelist."               
            else:
                response = "Error: Didn't find this device number in system!"
        else:
            response = "Error Op Code."   
        
        return response
    
    
    def client_die(self, devicename):
        'Performing operations when the server thinks this device is dead'
        if devicelist[devicename][devlist_pairinfo] in devicelist:
            devicelist[devicename][devlist_connected] = False
            devicelist[devicelist[devicename][devlist_pairinfo]][devlist_connected] = False
            try:
                devicelist[devicename][devlist_queue].clear()
                devicelist[devicelist[devicename][devlist_pairinfo]][devlist_queue].clear()
            except Queue.Empty:
                print "This queue is already empty, no need to clear."
        else:
            print "Warning: missing the pair information, cannot make it disconnected, die alone"
        devicelist[devicename][devlist_isalive] = False
        # May include another timer to indicate when to clear the long-dead device record
       

if __name__ == "__main__":
      
    mserver = Server("localhost", 36666)    
    print "Server serving...."
    mserver.serve()
    
    print "Over"
