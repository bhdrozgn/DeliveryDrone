import io
import time
import picamera
import numpy as np

def get_frame():
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		camera.start_preview()
		time.sleep(2)
		camera.capture(stream, format='jpeg')
	data = np.fromstring(stream.getvalue(), dtype=np.uint8)
	image = cv2.imdecode(data, 1)
	image = image[:, :, ::-1]
	return image
