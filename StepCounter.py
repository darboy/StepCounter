import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import re, time, os, sys
import numpy as np

class ScrollingPloter:
    def __init__(self, title_name, plot_num, x_data_num = 300, refresh_rate = 1):
        self.x_data_num = x_data_num
        self.title_name = title_name
        self.plot_num = plot_num
        self.refresh_rate = refresh_rate
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle(self.title_name)
        self.plot_array = []
        self.label = pg.LabelItem()
        self.win.addItem(self.label)
        self.start_step_t = time.time()
        self.last_step_t = time.time()
        self.is_new_step = False
        self.step_count = 0
        self.curve_array = []
        self.data_array = []
        self.timer_array = []
        self.slot_func_array = []
        self.func = []
        for i in range(0, plot_num):
            p = self.win.addPlot(row=i,col=0)
            p.showGrid(x=True,y=True)
            self.plot_array.append(p)
            init_data = np.zeros(x_data_num)
            self.data_array.append(init_data)
            curve = p.plot(self.data_array[i], pen="y", symbolBrush=(255,0,0), symbolPen='w')
            self.win.nextRow()
            self.curve_array.append(curve)
            self.func.append(self.noFunc)

    def noFunc(self):
        pass

    def setFunc(self, plot_index, func):
        self.timer = pg.QtCore.QTimer()
        self.func[plot_index] = func
        self.timer.timeout.connect(func)
        self.timer.start(1)

'''串口接收
********************************************************
'''
# import serial
# ser=serial.Serial("COM7",115200)


# def update():
#     data_str = ser.readline()
#     data_str = data_str.decode("utf-8")
#     data = re.split("[\r\n]", data_str)[0]
#     data = float(data)
#     x.data_array[0][:-1] = x.data_array[0][1:]
#     x.data_array[0][-1] = data
#     x.curve_array[0].setData(x.data_array[0])
#     angle_td = 30.0
#     valid_t = 0.5
    
#     filter_data = data
#     if filter_data < angle_td:
#         x.start_step_t = time.time()
#         x.is_new_step = True
#     else:
#         if (time.time() - x.start_step_t >= valid_t) and x.is_new_step:
#             x.step_count = x.step_count + 1
#             x.last_step_t = time.time()
#             x.is_new_step = False

#     x.label.setText(
#         "<span style='font-size: 50pt; color: white'>step count is %d<span style='color: white'></span>" % (
#             x.step_count))
# '''
# *********************************************************
# '''

'''tcpserver接收
********************************************************
'''
import socket
server_addr = ('192.168.100.148',52333)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(server_addr)
server.listen(5)
ss, addr = server.accept()  
flag = False
data_str = ""
def update():
    global flag
    if (not flag):
        data = ss.recv(2)
        data_str = data.decode('utf-8')
        if (data_str == "A5"):
            flag = True
    if flag:
        data = ss.recv(6)
        data_str = data.decode('utf-8')
        print(data_str)
        flag = False
        x.data_array[0][:-1] = x.data_array[0][1:]
        x.data_array[0][-1] = float(data_str)
        x.curve_array[0].setData(x.data_array[0])
        angle_td = 30.0
        valid_t = 0.5
        
        filter_data = float(data_str)
        if filter_data < angle_td:
            x.start_step_t = time.time()
            x.is_new_step = True
        else:
            if (time.time() - x.start_step_t >= valid_t) and x.is_new_step:
                x.step_count = x.step_count + 1
                x.last_step_t = time.time()
                x.is_new_step = False

        x.label.setText(
            "<span style='font-size: 50pt; color: white'>step count is %d<span style='color: white'></span>" % (
                x.step_count))

x = ScrollingPloter("setp counter", 1)
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()