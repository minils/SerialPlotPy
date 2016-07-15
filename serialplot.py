#!/bin/env python3
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from threading import Thread
from threading import Timer
import serial
import argparse
import serial.tools.list_ports
import signal
import sys
import time

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
plt = pg.plot(title="SerialPlotPy")
plt.addLegend()

pause = False

data = []
plots = []
colors = []
colors.append(QtGui.QColor(255,0,0));
colors.append(QtGui.QColor(0,200,0));
colors.append(QtGui.QColor(0,0,255));
colors.append(QtGui.QColor(255,0,255));
colors.append(QtGui.QColor(0,0,0));
colors.append(QtGui.QColor(103,48,175));
colors.append(QtGui.QColor(239,239,57));

def signal_handler(signal, frame):
        print ("\nQuitting...")
        app.closeAllWindows()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def check_port(value):
    ports = serial.tools.list_ports.comports()
    for v in ports:
        if v[0] == value:
            return str(value)
    raise argparse.ArgumentTypeError("%s is not a serial port" % value)

def check_baud(value):
    ival = int(value)
    baud_rates = [4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    for b in baud_rates:
        if b == ival:
            return ival
    raise argparse.ArgumentTypeError("%s is not a valid baud rate" % value)

def listen(port, baud, range, display):
    _sum = 0
    print("[SerialPlotPy] Connecting to " + str(args.port) + " at " + str(args.baud) + " Bps ...")
    ser = serial.Serial(port, baud)
    print("[SerialPlotPy] Connected")
    m = 0
    n = 0
    while True:
        try:
            val = ser.readline().decode("utf-8").rstrip()
            print(val)
        except UnicodeDecodeError:
            conn_timer.cancel()
            print("No serial connection. Wrong baud rate?")
            app.closeAllWindows()
            sys.exit(1)
        if "#" in val:
            # used for comments
            continue
        d = val.split(",")
        i = 0
        while i < len(data):
            try:
                data[i].append(float(d[i]))
            except:
                data[i].append(0.0)
            i = i + 1
        m = m + 1
        n = n + 1
        if m > 10:
            i = 0
            while i < len(data):
                plots[i].setData(data[i])
                i = i + 1
            m = 0
        plt.setXRange(n-range, n)

def check_connection():
    for i in range(len(data)):
        if len(data[i]) != 0:
            return
    print("There is no incoming data. Wrong baud rate?")
    app.closeAllWindows()
    sys.exit(1)

def exitHandler():
    print("Quitting...")
    sys.exit(0)

parser = argparse.ArgumentParser(description="Plot live data from serial. Default: /dev/ttyUSB0 with 115200.")
parser.add_argument("-p", "--port", help="serial port", default="/dev/ttyUSB0", type=check_port)
parser.add_argument("-b", "--baud", help="baud rate", default="115200", type=check_baud)
parser.add_argument("-d", "--display", help="displayed values", default=1, type=int)
parser.add_argument("-r", "--range", help="displayed range", default="200", type=int)
parser.add_argument("-f", "--file", help="save values to csv file FILE", default="", type=str)
parser.add_argument("-l", "--labels", help="labels of values in DISPLAY separated by comma", default="-1", type=str)
args = parser.parse_args()

# parse labels
if args.labels == "-1":
    labels = []
    for i in range(args.display):
        labels.append(str(i+1))
else:
    labels = args.labels.replace(" ", "").split(",")
if len(labels) != args.display:
    print("Amount of labels needs to be the same as DISPLAY!")
    sys.exit(1)

for i in range(args.display):
    d = []
    data.append(d)
    p = plt.plot(pen=pg.mkPen(color=colors[i % (len(colors))], style=QtCore.Qt.SolidLine), name=labels[i])
    plots.append(p)

serial_thread = Thread(target=listen, args=(args.port, args.baud, args.range, args.display,))
serial_thread.daemon = True
serial_thread.start()

# after 2 seconds the connection is checked
conn_timer = Timer(2.0, check_connection)
conn_timer.start()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        app.aboutToQuit.connect(exitHandler)
        app.exec_()
