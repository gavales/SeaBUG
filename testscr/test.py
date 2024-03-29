# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# MS5803_14BA
# This code is designed to work with the MS5803_14BA_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Analog-Digital-Converters?sku=MS5803-14BA_I2CS#tabs-0-product_tabset-2

import rospy
from std_msgs.msg import Float64
import smbus
import time

# Get I2C bus
bus = smbus.SMBus(1)

addr = 0x76

# MS5803_14BA address, addr(118)
#		0x1E(30)	Reset command
bus.write_byte(addr, 0x1E)

time.sleep(0.5)

# Read 12 bytes of calibration data
# Read pressure sensitivity
data = bus.read_i2c_block_data(addr, 0xA2, 2)
C1 = data[0] * 256 + data[1]

# Read pressure offset
data = bus.read_i2c_block_data(addr, 0xA4, 2)
C2 = data[0] * 256 + data[1]

# Read temperature coefficient of pressure sensitivity
data = bus.read_i2c_block_data(addr, 0xA6, 2)
C3 = data[0] * 256 + data[1]

# Read temperature coefficient of pressure offset
data = bus.read_i2c_block_data(addr, 0xA8, 2)
C4 = data[0] * 256 + data[1]

# Read reference temperature
data = bus.read_i2c_block_data(addr, 0xAA, 2)
C5 = data[0] * 256 + data[1]

# Read temperature coefficient of the temperature
data = bus.read_i2c_block_data(addr, 0xAC, 2)
C6 = data[0] * 256 + data[1]

# MS5803_14BA address, addr(119)
#		0x40(64)	Pressure conversion(OSR = 256) command
bus.write_byte(addr, 0x40)

time.sleep(0.5)

# Read digital pressure value
# Read data back from 0x00(0), 3 bytes
# D1 MSB2, D1 MSB1, D1 LSB
value = bus.read_i2c_block_data(addr, 0x00, 3)
D1 = value[0] * 65536 + value[1] * 256 + value[2]

# MS5803_14BA address, addr(119)
#		0x50(64)	Temperature conversion(OSR = 256) command
bus.write_byte(addr, 0x50)

time.sleep(0.5)

# Read digital temperature value
# Read data back from 0x00(0), 3 bytes
# D2 MSB2, D2 MSB1, D2 LSB
value = bus.read_i2c_block_data(addr, 0x00, 3)
D2 = value[0] * 65536 + value[1] * 256 + value[2]

dT = D2 - C5 * 256
TEMP = 2000 + dT * C6 / 8388608
OFF = C2 * 65536 + (C4 * dT) / 128
SENS = C1 * 32768 + (C3 * dT ) / 256
T2 = 0
OFF2 = 0
SENS2 = 0

if TEMP > 2000 :
    T2 = 7 * (dT * dT)/ 137438953472
    OFF2 = ((TEMP - 2000) * (TEMP - 2000)) / 16
    SENS2= 0
elif TEMP < 2000 :
	T2 = 3 * (dT * dT) / 8589934592
	OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 8
	SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 8
	if TEMP < -1500:
		OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
		SENS2 = SENS2 + 4 * ((TEMP + 1500) * (TEMP + 1500))

TEMP = TEMP - T2
OFF = OFF - OFF2
SENS = SENS - SENS2
press = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
cTemp = TEMP / 100.0
fTemp = cTemp * 1.8 + 32

# Output data to screen
print "Pressure : %.2f mbar" %press
print "Temperature in Celsius : %.2f C" %cTemp
print "Temperature in Fahrenheit : %.2f F" %fTemp

#def press_publisher():
#
#    pub = rospy.Publisher('press_publish', Float64, queue_size=10)
#
#    rate = rospy.Rate(2)
#
#    msg_to_publish = Float64()
#
#    press = 0
#
#    while not rospy.is_shutdown():
#        press_to_publish = press
#
#
#        msg_to_publish.data = press_to_publish
#
#        pub.publish(msg_to_publish)
#
#        rospy.loginfo(press_to_publish)
#
#        rate.sleep()
#
#if __name__ == "__main__":
#    rospy.init_node("press_publisher")
#    press_publisher()
