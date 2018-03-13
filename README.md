# pi-nav

Experiments in GPS with Raspberry Pi. See pi folder for instructions on setting up PI.

Instructions on setting up the Adafruit GPS can be found here:

<https://learn.adafruit.com/downloads/pdf/adafruit-ultimate-gps-on-the-raspberry-pi.pdf>

An example of accessing GPSD using the python-gps library (used as the basis for this implementation) is here:

<http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/>

And after much searching, an explanation of the values returned by the GPS is in these two links:

<http://theshipcomputer.blogspot.co.uk/2013/11/setting-up-gps-i-have-been-lucky-on-this.html>
<http://http://catb.org/gpsd/gpsd_json.html>

## Fields in use

I'm interested in the following fields (condensed from table by George Theotokis in first reference above).  The python library typically
returns "nan" (Not a number) when values are not present.  Note these properties are available from the <b>gps.fix</b> object.

<table>
	<thead>
		<tr><th>Name</th><th>Always returned?</th><th >Type</th><th >Notes</th></tr>
	</thead>
	<tbody>
		<tr><td>mode</td><td>Yes</td><td>numeric</td><td>0=no mode value yet seen, 1=no fix, 2=2D, 3=3D.  Used to determine if GPS has a fix.</td></tr>
		<tr><td>time</td><td>No</td><td>string</td><td>Time/date stamp in ISO8601 format, UTC.  Might use to set system clock and/or for logging</td></tr>
		<tr><td>lat</td><td>No</td><td>numeric</td><td>Latitude in degrees: +/- signifies West/East.  Present when mode is 2 or 3.</td></tr>
		<tr><td>lon</td><td>No</td><td>numeric</td><td>Longitude in degrees: +/- signifies North/South. Present when mode is 2 or 3.</td></tr>
		<tr><td>alt</td><td>No</td><td>numeric</td><td>Altitude in meters. Present if mode is 3.  Don't care for this project</td></tr>
		<tr><td>track</td><td>No</td><td>numeric</td><td>Course over ground, degrees from true north.</td></tr>
		<tr><td>speed</td><td>No</td><td>numeric</td><td>Speed over ground, meters per second.</td></tr>
		<tr><td>climb</td><td>No</td><td>numeric</td><td>Climb (positive) or sink (negative) rate, meters per second. Not used on this project</td></tr>
		<tr><td>epx</td><td>No</td><td>numeric</td><td>Longitude error estimate in meters, 95% confidence. Present
        if mode is 2 or 3 and DOPs can be calculated from the satellite
        view.</td></tr>
		<tr><td>epy</td><td>No</td><td>numeric</td><td>Latitude error estimate in meters, 95% confidence. Present
        if mode is 2 or 3 and DOPs can be calculated from the satellite
        view.</td></tr>
		<tr><td>epv</td><td>No</td><td>numeric</td><td>Estimated vertical error in meters, 95% confidence. Present
        if mode is 3 and DOPs can be calculated from the satellite
        view.</td></tr>
		<tr><td>ept</td><td>No</td><td>numeric</td><td>Estimated timestamp error. Present if time is present.</td></tr>
		<tr><td>epd</td><td>No</td><td>numeric</td><td>Direction error estimate in degrees, 95% confidence.</td></tr>
		<tr><td>eps</td><td>No</td><td>numeric</td><td>Speed error estimate in meters/sec, 95% confidence.</td></tr>
		<tr><td>epc</td><td>No</td><td>numeric</td><td>Climb/sink error estimate in meters/sec, 95% confidence.</td></tr>
</tbody>
</table>

## Other interesting contents

* Controlling servos via the Polulu servo controller
* Interfacing to the Adafruit combined compass accelerometer Adafruit LSM303DLHC, including tilt corrected compass
* Using the I2C interface
* Interfacing to a AS5048B rotatry shaft encoder via I2C, for a wind direction sensor
