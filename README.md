# SerialPlotPy

Python script to plot serial input.

It can be used to display data that is read through a serial connection.

### Version
0.0.1

### Installation
Install dependecies:
- [Python][python] 2.7 or 3.4
- [PyQt][pyqt]
- [pyqtgraph][pyqtgraph]
- [pySerial][pyserial]

Make script executable:
```sh
$ chmod +x serialplot.py
```

### Usage

To run the script:
```sh
$ ./serialplot.py
```

Command line options:
```sh
serialplot.py [-h] [-p PORT] [-b BAUD] [-d DISPLAY] [-r RANGE] [-f FILE] [-l LABELS]
```

### Arduino Example

One could use an **Arduino** to read a sensor and print the sensor values to the serial connection:
```c
void setup() {
  Serial.begin(115200);
}

void loop() {
  // acquire sensor values
  float x = sensor.measure_x();
  float y = sensor.measure_y();
  float z = sensor.measure_z();
  
  // Print values to serial
  Serial.print(x); Serial.print(",");
  Serial.print(y); Serial.print(",");
  Serial.print(z); Serial.prinln();
  Serial.flush();
  
  delay(50);
}
```

The data could then be displayed as follows:
```sh
./serialplot.py -p /dev/ttyUSB0 -b 115200 -d 3 -r 200 -l "x-axis,y-axis,z-axis"
```

### Todos

 - Add csv export

License
----

MIT

[//]: # (Links:)


   [python]: <https://www.python.org/>
   [pyqt]: <https://wiki.python.org/moin/PyQt>
   [pyqtgraph]: <http://www.pyqtgraph.org/>
   [pyserial]: <https://github.com/pyserial/pyserial>



