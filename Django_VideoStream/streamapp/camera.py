import cv2,os,urllib.request, json
import requests
from django.http import JsonResponse
import numpy as np
from time import sleep
import face_recognition
from django.conf import settings
face_detection_videocam = cv2.CascadeClassifier(os.path.join(
			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
face_detection_webcam = cv2.CascadeClassifier(os.path.join(
			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))

url = "http://127.0.0.1:8000/accounts/process/"


# Defining configs
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2


class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		self.video.release()
		
	# Returns (R, G, B) from name
	def name_to_color(name):
		# Take 3 first letters, tolower()
		# lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
		color = [(ord(c.lower())-97)*8 for c in name[:3]]
		return color

	def get_frame(self):
	
		print("Loading the encoded faces from the saved file!!!")
		# Load face encodings from saved files.
		# with open('dataset_faces_v2.1.dat', 'rb') as f:
		#     all_face_encodings = pickle.load(f)
		get_encodings = requests.get("http://127.0.0.1:8000/accounts/user-encodes")
		data = get_encodings.json()
		if "data" in data.keys():
			alert = data["data"]
			return JsonResponse({"success": alert})
		if "message" in data.keys():
			alert = data["message"]
			return JsonResponse({"success": alert})
		# faces = data["data"]
		# print(faces)

		# Grab the list of names and the list of encodings
		# known_face_names = list(all_face_encodings.keys())
		# known_face_encodings = np.array(list(all_face_encodings.values()))
		known_face_names = data["names"]
		encodings = eval(data["encodings"])
		known_face_encodings = list(np.asarray(encodings["array"]))
		print("Loaded the saved encodes and labels from the database file!!!")

		print("Initiating the predictions!!!")

		## Print Texts
		# when no face detected in the frame.
		no_face = "No face(s) detected in the frame!!!"
		# When known face is detected in the frame.
		known_face = "Known face(s) detected in the frame!!!"
		# When unknown face is detected in the frame.
		unknown_face = "Unknow face(s) detected in the frame!!!"
		success, image = self.video.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
		face_picture = image
		# cv2.imshow("Live Feed", face_picture)
		face_locations = face_recognition.face_locations(face_picture)
		if len(face_locations) == 0:
			print("\r", end='')
			print("{}".format(no_face), end="", sep=" ", flush=True)

		elif len(face_locations) > 1:
			print("Multiple Faces detected")
			
		else:
			# Encode faces from the live input
			face_encodings = face_recognition.face_encodings(face_picture, face_locations)
			# Show the live input from the camera.
			# cv2.imshow("Live Feed", face_picture)
			# Quit if   is pressed.5q
			# if cv2.waitKey(1) & 0xff==ord('q'):
			# break

			# Loop in all detected faces
			for face_encoding in face_encodings:

				# See if the face is a match for the known face (that we saved in the precedent step)
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
				match = None

				if True in matches:
					# print("Known face in the frame")
					print("\r", end='')
					print("{}".format(known_face), end="", sep=" ", flush=True)

					# winsound.Beep(frequency, duration)

					# check the known face with the smallest distance to the new face
					face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

					# Take the best one
					best_match_index = np.argmin(face_distances)

					# if we have a match:
					if matches[best_match_index]:
						# Give the detected face the name of the employee that match
						name = known_face_names[best_match_index]
						print("")
						print("Hi " + str(name) + " Welcome to UST GLobal!!!")
						headers = {'Content-type': 'application/json',
								   'Accept': 'text/plain'}
						post_data = {"name": str(name)}
						print(post_data)
						
						# Drawing box around the faces
						top_left = (face_locations[0][3], face_locations[0][0])
						bottom_right = (face_locations[0][1], face_locations[0][2])

						# Get color by name using our fancy function
						color = [0, 255, 0]
						

						# Paint frame
						cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

						# Drawing box for name below the detected face.
						top_left = (face_locations[0][3], face_locations[0][2])
						bottom_right = (face_locations[0][1], face_locations[0][2] + 22)
						
						# Paint frame
						cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

						check = requests.post(url, data=json.dumps(post_data),
											  headers=headers)
						
						# Wite name on the deteced faces
						cv2.putText(image, name, (face_locations[0][3] + 10, face_locations[0][2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), FONT_THICKNESS)
						
						"""
						print(check)
						cv2.putText(face_picture, str(name), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
						"""

					else:
						print("\r", end='')
						print("{}".format(unknown_face), end="", sep=" ", flush=True)

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		ret, jpeg = cv2.imencode('.jpg', image)
		return jpeg.tobytes()


# class IPWebCam(object):
# 	def __init__(self):
# 		self.url = "http://192.168.0.100:8080/shot.jpg"
#
#
# 	def __del__(self):
# 		cv2.destroyAllWindows()
#
# 	def get_frame(self):
# 		imgResp = urllib.request.urlopen(self.url)
# 		imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
# 		img= cv2.imdecode(imgNp,-1)
# 		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
# 		# so we must encode it into JPEG in order to correctly display the
# 		# video stream
# 		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 		faces_detected = face_detection_webcam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
# 		for (x, y, w, h) in faces_detected:
# 			cv2.rectangle(img, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
# 		resize = cv2.resize(img, (640, 480), interpolation = cv2.INTER_LINEAR)
# 		frame_flip = cv2.flip(resize,1)
# 		ret, jpeg = cv2.imencode('.jpg', frame_flip)
# 		return jpeg.tobytes()