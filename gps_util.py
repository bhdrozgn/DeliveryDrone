import sys
import serial


def get_coordinates():
	received_data = (str)(serial.Serial("/dev/ttyS0").readline())
	GPGGA_data_available = received_data.find("$GPGGA,")
	if GPGGA_data_available:
		GPGGA_buffer = received_data.split("$GPGGA," ,1)[1] 
		NMEA_buff = (GPGGA_buffer.split(','))
		lat_in_degrees, long_in_degrees = GPS_Info()
		return lat_in_degrees, long_in_degrees
	else:
		return 0, 0


def GPS_info():
    global NMEA_buff
    nmea_latitude = []
    nmea_longitude = []
    nmea_latitude = NMEA_buff[1]                # latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               # longitude from GPGGA string
    
    lat = float(nmea_latitude)               
    longi = float(nmea_longitude)
    
	return convert_to_degrees(lat), convert_to_degrees(longi)


def convert_to_degrees(raw_value):
    decimal_value = raw_value / 100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value)) / 0.6
    position = degrees + mm_mmmm
    return position
