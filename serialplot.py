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
magPlot = pg.plot()
magPlot.setWindowTitle('live plot from ble')
magPlot.addLegend()

data_x  = []
data_y  = []
data_z  = []
data_ir = []

freq = 0.0
freq_zc = 0.0

def signal_handler(signal, frame):
        print ('Good bye!')
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
    # start serial connection
    print("[SerialListener] Connecting to ", args.port, " at ", args.baud, " Bps ...")
    ser = serial.Serial(port, baud)
    print("[SerialListener] Connected")
    i = 0
    n = 0
    while True:
        try:
            val = ser.readline().decode("utf-8")[:-2]
        except UnicodeDecodeError:
            conn_timer.cancel()
            print("No serial connection. Wrong baud rate?")
            app.closeAllWindows()
            sys.exit(1)
        #print(val)
        if "#" in val:
            # used for comments
            continue
        d = val.split(",")
        if "x" in display:
            try:
                data_x.append(float(d[0]))
            except:
                data_x.append(0);
        if "y" in display:
            try:
                data_y.append(float(d[1]))
            except:
                data_y.append(0)
        if "z" in display:
            try:
                data_z.append(float(d[2]))
            except:
                data_z.append(0)
        if "i" in display:
            try:
                data_ir.append((float(d[3]) - 40000)/20)
            except:
                data_ir.append(0)
        i = i + 1
        n = n + 1
        if i > 10:
            if "x" in display:
                x.setData(data_x)
            if "y" in display:
                y.setData(data_y)
            if "z" in display:
                z.setData(data_z)
            if "i" in display:
                ir.setData(data_ir)
            i = 0
        magPlot.setXRange(n-range, n)

def check_connection():
    if (len(data_x) == 0 and len(data_y) == 0 and len(data_z) == 0 and len(data_ir) == 0):
        print("There is no incoming data. Wrong baud rate?")
        app.closeAllWindows()
        sys.exit(1)

def exitHandler():
    print("X pressed")
    quit = True
    sys.exit(0)

parser = argparse.ArgumentParser(description="Plot live magnetic data read from serial.")
parser.add_argument("-p", "--port", help="Serial port", default="/dev/ttyUSB0", type=check_port)
parser.add_argument("-b", "--baud", help="Baud rate", default="115200", type=check_baud)
parser.add_argument("-d", "--display", help="Values to display (x,y,z,i)", default="x")
parser.add_argument("-r", "--range", help="What range to use", default="200", type=int)
args = parser.parse_args()

if "x" in args.display:
    x = magPlot.plot(pen=pg.mkPen(color=QtGui.QColor(255,0,0), style=QtCore.Qt.SolidLine), name='Magnetic x')
if "y" in args.display:
    y = magPlot.plot(pen=pg.mkPen(color=QtGui.QColor(0,255,0), style=QtCore.Qt.SolidLine), name='Magnetic y')
if "z" in args.display:
    z = magPlot.plot(pen=pg.mkPen(color=QtGui.QColor(0,255,255), style=QtCore.Qt.SolidLine), name='Magnetic z')
if "i" in args.display:
    ir = magPlot.plot(pen=pg.mkPen(color=QtGui.QColor(0,0,255), style=QtCore.Qt.SolidLine), name='Infra-Red')

serial_thread = Thread(target=listen, args=(args.port, args.baud, args.range, args.display,))
serial_thread.daemon = True
debug("Starting serial thread")
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
