import sys
import cv2
import os
import time
import numpy as np
import argparse
from sys import platform
from math import sqrt, acos, degrees, atan, degrees
import requests
from cam import get_frame
from gps_util import get_coordinates
from dist import distance_from_floor
from decode_poly import decode_polyline
from drive import right, left, forward, back, up, down, init, stop

#-----------------------Angle Functions------------------------

def get_angle(a,b):
    print("a=", a, "b=", b)
    del_y = a[1]-b[1]
    del_x = b[0]-a[0]
    if del_x == 0:
        del_x = 0.1
    print("Del_X : "+str(del_x)+"-----Del_Y: "+str(del_y))
    angle = 0
    if del_x > 0 and del_y > 0:
        angle = degrees(atan(del_y / del_x))
    elif del_x < 0 and del_y > 0:
        angle = degrees(atan(del_y / del_x)) + 180
    return angle

def angle_gor(a,b,c,d):
    ab=[a[0]-b[0],a[1]-b[1]]
    ab1=[c[0]-d[0],c[1]-d[1]]
    cos=abs(ab[0]*ab1[0]+ab[1]*ab1[1])/(sqrt(ab[0]**2+ab[1]**2)*sqrt(ab1[0]**2+ab1[1]**2))
    ang = acos(cos)
    return ang*180/np.pi


def sit_ang(a,b,c,d):
	ang=angle_gor(a,b,c,d)
	s1=0
	if ang != None:
		#print("Angle",ang)
		if ang < 120 and ang>40:
			s1=1
	return s1

def sit_rec(a,b,c,d):
	ab = [a[0] - b[0], a[1] - b[1]]
	ab1 = [c[0] - d[0], c[1] - d[1]]
	l1=sqrt(ab[0]**2+ab[1]**2)
	l2=sqrt(ab1[0]**2+ab1[1]**2)
	s=0
	if l1!=0 and l2!=0:
		#print(l1,l2, "---------->>>")
		if l2/l1>=1.5:
			s=1
	return s

def getFrameDimension(im):
	height, width, shape = im.shape
	return height, width

def defineCenterArea(height, width):
	_x1 = width - width * (60/100)
	_x4 = width - width * (40/100)
	_y1 = height - height * (70/100)
	_y4 = height / 2
	return _x1, _x4, _y1, _y4

def checkIfInRange(datum, _x1, _x4, _y1, _y4, detectedperson):
	pos = [int(datum.poseKeypoints[detectedperson][1][0]), int(datum.poseKeypoints[detectedperson][1][1])]		# w,h
	print(pos)
	if ((_x1 < pos[0] < _x4) and (_y1 < pos[1] < _y4)):
		return [0,0]
	else:
		return pos

def trackObject(im, datum, detectedperson):
	height, width = getFrameDimension(im)
	_x1, _x4, _y1, _y4 = defineCenterArea(height, width)
	pos = checkIfInRange(datum, _x1, _x4, _y1, _y4, detectedperson)
	if (pos == [0,0]):
		print("Already In Center")
	else: 
		if (pos[0] < _x1):
			print("Move Left")
			left()
		elif (pos[0] > _x4):
			print("Move Right")
			right()
		if (pos[1] < _y1):
			print("Move Up")
			up()
		elif (pos[1] > _y4):
			print("Move Down")
			down()

#--------------------------------------------------------------

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = "C:/openpose/build_windows/examples/tutorial_api_python"
try:
    # Windows Import
    if platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../../python/openpose/Release');
        #os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
        os.add_dll_directory(dir_path + '/../../x64/Release')
        os.add_dll_directory(dir_path + '/../../bin')
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('../../python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

# Flags
parser = argparse.ArgumentParser()
parser.add_argument("--image_path", default="Resources/001.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
args = parser.parse_known_args()

# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "Resources/models/"
params["net_resolution"] = "-1x192"
#params["model_pose"] = "COCO"
## Çıkan json dosyasında x0,y0,c0,x1,y1,c1,... şeklinde tutuluyor 18 + 18 + 18
#params["write_json"] = "Output"
## [0,1] arasına normalize ediyoruz, (0,0) sol üst, (1,1) sağ alt
#params["keypoint_scale"] = 3
# Add others in path?

for i in range(0, len(args[1])):
    curr_item = args[1][i]
    if i != len(args[1])-1: next_item = args[1][i+1]
    else: next_item = "1"
    if "--" in curr_item and "--" in next_item:
        key = curr_item.replace('-','')
        if key not in params:  params[key] = "1"
    elif "--" in curr_item and "--" not in next_item:
        key = curr_item.replace('-','')
        if key not in params: params[key] = next_item

# Construct it from system arguments
# op.init_argv(args[1])
# oppython = op.OpenposePython()

c=0
# Starting OpenPose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

#--------------------------------------------------------------
#----------------------------Main------------------------------

starttime = time.time()
while True:
	try:
		raw_resp = requests.get("http://xxx.xxx.xxx.xxx/coordinates?dId=3")
		resp = raw_resp.json()
		lat_to_go = resp["lat"]
		long_to_go = resp["long"]
	
		curr_lat, curr_long = get_coordinates()
		if curr_lat != 0 or curr_long != 0:
			break

		time.sleep(60.0 - ((time.time() - starttime) % 5))

	except KeyboardInterrupt:			# debug
		break

polyline_req_str = """
		https://maps.googleapis.com/maps/api/directions/json?
		origin={0},{1}
		&destination={2},{3}
		&key=XXXXXX
	""".format(curr_lat, curr_long, lat_to_go, long_to_go)
polyline_resp = requests.get(polylines_req_str)
polyline = polyline_resp["overview_polyline"]
route_coords = decode_polyline(polyline)
	
init()			# drive.init()

dist_from_floor = distance_from_floor()
while dist_from_floor < 2000:
	up()
	dist_from_floor = distance_from_floor()

for next_lat, next_long in route_coords:
	while next_lat - curr_lat != 0 and next_long - curr_long != 0:
		if next_lat > curr_lat:
			right()
		elif next_lat < curr_lat:
			left()
		if next_long > curr_long:
			forward()
		elif next_long < curr_long:
			back()
		curr_lat, curr_long = get_coordinates()

dist_from_floor = distance_from_floor()
while distance_from_floor > 500:
	down()
	dist_from_floor = distance_from_floor()
		
#-----------------Search for a customer and go------------------
customer_found = false
deg = 0
cam = cv2.VideoCapture(1)
while customer_found != true and deg <= 720:
	left()
	deg += 5
	image_from_cam = get_frame()
	for i in range(1000):
		# Process Image
		datum = op.Datum()
		s, im = cam.read() # captures image
		image1 = im
		c+=1
		if c==8:
			c=0
			datum.cvInputData = image1
			opWrapper.emplaceAndPop(op.VectorDatum([datum]))     # OpenPose being applied to the frame image.
			# Display Image
			#print("Body keypoints: \n" + str(datum.poseKeypoints))
			#print(datum.poseKeypoints.shape)
			#arr = np.array([datum.poseKeypoints])
			detectedperson = 0
			found_flag = 0

			try:
				if len(datum.poseKeypoints.shape)>=2:
					start = time.time()
					x1=0
					x2=0
					for j in range(len(datum.poseKeypoints)):
						x1=0
						x2=0
						s=0
						s1=0
						ang1 = get_angle(datum.poseKeypoints[j][3], datum.poseKeypoints[j][4])			# right elbow to right wrist
						ang2 = get_angle(datum.poseKeypoints[j][6], datum.poseKeypoints[j][7])			# left elbow to left wrist
						ang3 = get_angle(datum.poseKeypoints[j][2], datum.poseKeypoints[j][3])			# right arm to right elbow
						ang4 = get_angle(datum.poseKeypoints[j][5], datum.poseKeypoints[j][6])			# left arm to left elbow
						if ((30 < ang1 < 150) and (90 < ang3 < 180)):
							x1 = 1
						if ((30 < ang2 < 150) and (0 < ang4 < 90)):
							x2 = 1
						x3 = x1+x2
						if (x3 == 1):
							print("The {} person is WAVING !".format(j+1))
							detectedperson = j
							customer_found = True
						else: 
							print("The {} person is NOT WAVING !".format(j+1))
							customer_found = False
						if customer_found:
							try:
								trackObject(image1, datum, detectedperson)
								forward()
							except:
								print("exception")
							dist_from_floor = distance_from_floor()
							while dist_from_floor > 50:
								down()
								dist_from_floor = distance_from_floor()
							drop_package()

					print("___________________________")
					print("      ")
					end = time.time()
					print("Step time: " + str(end - start) + " seconds")
					im=cv2.resize(datum.cvOutputData,(864,540), interpolation = cv2.INTER_AREA)
					cv2.imshow("Camera", im)
					cv2.waitKey(1)
			except:
				#im=cv2.resize(im, (864,540), interpolation = cv2.INTER_AREA)
				#cv2.imshow("Camera", im)
				print("NO HUMAN detected")

#--------------------------------------------------------------

dist_from_floor = distance_from_floor()
while dist_from_floor < 2000:
	up()
	dist_from_floor = distance_from_floor()

lat_to_go, long_to_go = curr_lat, curr_long
curr_lat, curr_long = get_coordinates()

polyline_req_str = """
		https://maps.googleapis.com/maps/api/directions/json?
		origin={0},{1}
		&destination={2},{3}
		&key=XXXXXX
	""".format(curr_lat, curr_long, lat_to_go, long_to_go)
polyline_resp = requests.get(polylines_req_str)
polyline = polyline_resp["overview_polyline"]
route_coords = decode_polyline(polyline)

dist_from_floor = distance_from_floor()
while dist_from_floor < 2000:
	up()
	dist_from_floor = distance_from_floor()

for next_lat, next_long in route_coords:
	while next_lat - curr_lat != 0 and next_long - curr_long != 0:
		if next_lat > curr_lat:
			right()
		elif next_lat < curr_lat:
			left()
		
		if next_long > curr_long:
			forward()
		elif next_long < curr_long:
			back()
			
		curr_lat, curr_long = get_coordinates()

dist_from_floor = distance_from_floor()
while dist_from_floor > 50:
	down()
	dist_from_floor = distance_from_floor()
		
stop()

#--------------------------------------------------------------
#--------------------------------------------------------------

#cam = cv2.VideoCapture(1)
#for i in range(1000):
#	# Process Image
#	datum = op.Datum()
#	s, im = cam.read() # captures image
#	image1 = im
#	c+=1
#	if c==8:
#		c=0
#		datum.cvInputData = image1
#		opWrapper.emplaceAndPop(op.VectorDatum([datum]))     # OpenPose being applied to the frame image.
#		# Display Image
#		#print("Body keypoints: \n" + str(datum.poseKeypoints))
#		#print(datum.poseKeypoints.shape)
#		#arr = np.array([datum.poseKeypoints])
#		detectedperson = 0

#		try:
#			if len(datum.poseKeypoints.shape)>=2:
#				start = time.time()
#				x1=0
#				x2=0
#				for j in range(len(datum.poseKeypoints)):
#					x1=0
#					x2=0
#					s=0
#					s1=0
#					ang1 = get_angle(datum.poseKeypoints[j][3], datum.poseKeypoints[j][4])			# right elbow to right wrist
#					ang2 = get_angle(datum.poseKeypoints[j][6], datum.poseKeypoints[j][7])			# left elbow to left wrist
#					ang3 = get_angle(datum.poseKeypoints[j][2], datum.poseKeypoints[j][3])			# right arm to right elbow
#					ang4 = get_angle(datum.poseKeypoints[j][5], datum.poseKeypoints[j][6])			# left arm to left elbow
#					if ((30 < ang1 < 150) and (90 < ang3 < 180)):
#						x1 = 1
#					if ((30 < ang2 < 150) and (0 < ang4 < 90)):
#						x2 = 1
#					x3 = x1+x2
#					if (x3 == 1):
#						print("The {} person is WAWING !".format(j+1))
#						detectedperson = j
#						found_flag = j
#					else: 
#						print("The {} person is NOT WAWING !".format(j+1))
#						found_flag = 0
#					try:
#						trackObject(image1, datum, detectedperson)
#					except:
#						print("exception")
#				print("___________________________")
#				print("      ")
#				end = time.time()
#				print("Step time: " + str(end - start) + " seconds")
#				im=cv2.resize(datum.cvOutputData,(864,540), interpolation = cv2.INTER_AREA)
#				cv2.imshow("Camera", im)
#				cv2.waitKey(1)
#		except:
#			#im=cv2.resize(im, (864,540), interpolation = cv2.INTER_AREA)
#			#cv2.imshow("Camera", im)
#			print("NO HUMAN detected")

		