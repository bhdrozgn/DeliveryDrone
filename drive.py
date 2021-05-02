from RPIO import PWM

def init():
	roll = PWM.Servo()
	pitch = PWM.Servo()
	throttle = PWM.Servo()
	yaw = PWM.Servo()
	aux = PWM.Servo()

	roll.set_servo(5, 1520)
	pitch.set_servo(6, 1520)
	throttle.set_servo(13, 1100)
	yaw.set_servo(19, 1520)
	aux.set_servo(26, 1010)


def up():
	th = th + 10
	if (th < th_min):
		throttle.set_servo(13,1100)
		th = 1100
	elif (th > th_max):
		throttle.set_servo(13,2400)
		th = 2400
	elif (th > th_min & th < th_max):
		throttle.set_servo(13,th)


def down():
	th = th - 10
	if (th < th_min):
		throttle.set_servo(13,1100)
		th = 1100
	elif (th > th_max):
		throttle.set_servo(13,2400)
		th = 2400
	elif (th > th_min & th < th_max):
		throttle.set_servo(13,th)


def left():
	y = y - 10
	if (y < y_min):
		yaw.set_servo(19,1100)
		y = 1100
	elif (y > y_max):
		yaw.set_servo(19,1900)
		y = 1900
	elif (y > y_min & y < y_max):
		yaw.set_servo(19,y)
		

def right():
	y = y + 10
	if (y < y_min):
		yaw.set_servo(19,1100)
		y = 1100
	elif (y > y_max):
		yaw.set_servo(19,1900)
		y = 1900
	elif (y > y_min & y < y_max):
		yaw.set_servo(19,y)


def forward():
	p = p + 10
	if (p < p_min):
		pitch.set_servo(6,1100)
		p = 1100
	elif (p > p_max):
		pitch.set_servo(6,1900)
		p = 1900
	elif (p > p_min & p < p_max):
		pitch.set_servo(6,p)


def back():
	p = p - 10
	if (p < p_min):
		pitch.set_servo(6,1100)
		p = 1100
	elif (p > p_max):
		pitch.set_servo(6,1900)
		p = 1900
	elif (p > p_min & p < p_max):
		pitch.set_servo(6,p)
						

def stop():
	roll.stop_servo(5)
	pitch.stop_servo(6)
	throttle.stop_servo(13)
	yaw.stop_servo(19)
	aux.stop_servo(26)

