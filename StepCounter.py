import numpy as np
import scipy.signal as signal
import serial,re,time,math,socket

class recDataBase:
    '''
        recData base
        override: func __init__() to add pattern to fetch useful data
        override: func rec() to realize other ways of transmission
    '''
    def __init__(self, slide_size):
        self.__slide_size = slide_size
        self.__data = np.zeros(slide_size, float)

    def insert(self, data):
        self.__data[:-1] = self.__data[1:]
        try:
            data = float(data)
        except:
            data = self.__data[-2]
            self.log("data convert to float failed:"+str(data))
        self.__data[-1] = data
    
    def rec(self):
        pass

    def get(self):
        return np.mean(self.__data)
        # return self.__data

    def size(self):
        return self.__slide_size

    def clear(self):
        self.__data = np.zeros(self.__slide_size)

    def log(self,str):
        print(str)

class recDataBySerial(recDataBase):
    '''
        by serial
    '''
    def __init__(self, com, baudrate, slide_size, pattern, data_index):
        super().__init__(slide_size)
        self.ser=serial.Serial(com, baudrate)
        self.__pattern = pattern
        self.__data_index = data_index

    def rec(self):
        data_str = self.ser.readline()
        data_str = data_str.decode("utf-8")
        data = re.split(self.__pattern, data_str)[self.__data_index]
        super().insert(data)
        return float(data)

class recDataByTcp(recDataBase):
    '''
        by tcp
    '''
    def __init__(self,ip,port,slide_size,pattern,data_index):
        super().__init__(slide_size)
        self.ip = ip
        self.port = port
        self.__pattern = pattern
        self.__data_index = data_index
        server_addr = (ip,port)
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind(server_addr)
        server.listen(5)
        self.ss, addr = server.accept() 
    
    def rec(self):
        data_str = self.ss.recv()
        data_str = data_str.decode("utf-8")
        data = re.split(self.__pattern, data_str)[self.__data_index]
        super().insert(data)
        return float(data)

class stepCounter:
    def __init__(self, angle_threshold, valid_time):
        '''
            angle_threshold: minimun angle at which the legs stand upright and step (degree)
            valid_time: time between two steps (ms)
        '''
        self.__angle_td = angle_threshold
        self.__valid_t = valid_time
        self.rec_data = recDataBySerial("COM7",115200,20,"[\r\n]",0)
        # self.rec_data = recDataBase(20)
        self.last_step_t = time.time()
        self.start_step_t = time.time()
        self.valid_step_record = []
        self.step_count = 0
        self.count = 0
        self.is_new_step = False

    def run(self):
        filter_data = self.rec_data.rec()
        # filter_data = self.rec_data.get()
        if filter_data < self.__angle_td:
            self.start_step_t = time.time()
            self.valid_step_record.clear()
            self.is_new_step = True
        else:
            self.valid_step_record.append(filter_data)
            if (time.time() - self.start_step_t >= self.__valid_t) and self.is_new_step:
                self.step_count = self.step_count + 1
                self.last_step_t = time.time()
                self.is_new_step = False
                # signal.argrelextrema(self.valid_step_record, np.greater_equal)
        print("pitch is %03f, step is %d" % (filter_data, self.step_count))

if __name__ == "__main__":
    # size = 200
    # ex = recDataBase(size)
    # for i in range(1,size):
    #     import math
    #     ex.insert(math.cos(i))
    # print(ex.get())
    ex = stepCounter(30.0,0.5)
    while True:
        ex.run()
        # time.sleep(0.1)