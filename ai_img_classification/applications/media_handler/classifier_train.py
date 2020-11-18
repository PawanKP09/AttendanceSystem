# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 21:05:30 2020

@author: pawanprx
"""

## Required Liabrary Imports
import os
import cv2
from datetime import datetime,timedelta,time
import pickle
import requests
# import numpy as np
from time import sleep
from pathlib import Path
import numpy as np
import urllib.request

import face_recognition
from applications.accounts.models import UserImages
## Directory with training images.
def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	# return the image
	return image

# try:
#     known_face = "media/training/2020-04-13"
# except:
#     print("nothing found")
# known_face = "C:/Users/pawanprx/Downloads/dataset_1/database/dataset_27_03/train_dataset"

# Dictionary holding the encoded images along with their labels
known_face_encodings = {}
# url = 'http://127.0.0.1:8080/backend/user-images'
# Method to encode the emagees in the training dataset
# def face_encoder_mul():
#     today = datetime.now().date()
#     get_images = requests.get(url)
#     # faces = UserImages.objects.filter(created__date=today)
#     print(get_images.text)
#     try:
#         data = get_images.json()
#         faces = data["urls"]
#         image_counter = 1
#         print("Initiating the face encoding process for the know faces from the database!!!")
#         # for known_faces in os.listdir(known_face):
#         #     # known_faces = os.path.join(known_face, known_faces)
#         #     if known_faces.endswith(".JPG") or known_faces.endswith(".png"):
#         #         image = cv2.imread(os.path.join(known_face, known_faces))
#         #         image_label = os.path.basename(known_faces)
#         #         image_label = image_label.split("_")[0]
#         #         known_face_encodings[str(image_label)] = face_recognition.face_encodings(image)[0]
#         #         print(str(image_label) + "'s face(s) encoded")
#         #         image_counter += 1
#         #
#         #         # Savings the encoded image along witht he label to a database file
#         # with open('dataset_faces_v2.1.dat', 'wb') as f:
#         #     pickle.dump(known_face_encodings, f)
#         # print("All the faces in the database are encoded and stored for inference!!!")
#         # sleep(2)
#         if faces:
#             for known_face in faces:
#                 print(known_face)
#                 # known_faces = os.path.join(known_face, known_faces)
#                 if known_face["name"].endswith(('.png','.jpg','.jpeg')):
#                     # image = cv2.imread(os.path.join("media", known_face.image.name))
#                     image = url_to_image(known_face["url"])
#                     # image_label = os.path.basename(known_face.image.name)
#                     image_label = known_face["name"]
#                     print(image_label,"dddddddddddddddddddddddddddddddddddd")
#                     # if "_" in known_face.image.name:
#                     if "_" in image_label:
#                         image_label = image_label.split("_")[0]
#                     else:
#                         image_label = image_label.split(".")[0]
#                     known_face_encodings[str(image_label)] = face_recognition.face_encodings(image)[0]
#                     print(str(image_label) + "'s face(s) encoded")
#                     image_counter += 1
#
#                     # Savings the encoded image along witht he label to a database file
#             my_file = Path("http://127.0.0.1:8000/media/dataset_faces_v2.1.dat")
#             face_dict ={}
#             if my_file.is_file():
#                 print("file_exist")
#                 path = 'dataset_faces_v2.1.dat'
#                 with open(path, 'rb') as f:
#                     all_face_encodings = pickle.load(f)
#                     known_face_names = list(all_face_encodings.keys())
#                     print("These are the faces already encoded in the file: ", known_face_names)
#                     face_dict.update(all_face_encodings)
#                 with open(path,"wb") as file:
#                     known_face_encodings.update(face_dict)
#                     pickle.dump(known_face_encodings, file)
#                     print("All the faces in the database are encoded and stored for inference!!!")
#             else:
#                 path = 'http://127.0.0.1:8000/media/dataset_faces_v2.1.dat'
#                 with open(path, 'wb') as f:
#                     pickle.dump(known_face_encodings, f)
#                     file_obj = TrainingFile()
#                     file_obj.dat_file.name = path
#                     file_obj.save()
#                 print("All the faces in the database are encoded and stored for inference!!!")
#                 return True
#         return False
#     except:
#             return "no"

def face_encoder_mul():
	today = datetime.now().date()
	faces = UserImages.objects.filter(created__date=today)
	# faces = UserImages.objects.all()
	image_counter = 1
	print("Initiating the face encoding process for the know faces from the database!!!")
	if len(faces) > 0:
		for known_face in faces:
			print(known_face)
			# known_faces = os.path.join(known_face, known_faces)
			if known_face.image.name.endswith(('.png', '.jpg', '.jpeg')):
				image = cv2.imread(os.path.join("media", known_face.image.name))
				# image = url_to_image(known_face["url"])
				image_label = os.path.basename(known_face.image.name)
				# image_label = known_face["name"]
				# if "_" in known_face.image.name:
				if "_" in image_label:
					image_label = image_label.split("_")[0]
				else:
					image_label = image_label.split(".")[0]
				known_face_encodings[str(image_label)] = face_recognition.face_encodings(image)[0]
				print(str(image_label) + "'s face(s) encoded")
				image_counter += 1

			# Savings the encoded image along witht he label to a database file
		my_file = Path("dataset_faces_v2.1.dat")
		face_dict = {}
		if my_file.is_file():
			print("file_exist")
			path = 'dataset_faces_v2.1.dat'
			with open(path, 'rb') as f:
				all_face_encodings = pickle.load(f)
				print(all_face_encodings)
				known_face_names = list(all_face_encodings.keys())
				print("These are the faces already encoded in the file: ", known_face_names)
				face_dict.update(all_face_encodings)
			with open(path, "wb") as file:
				known_face_encodings.update(face_dict)
				pickle.dump(known_face_encodings, file)
				print("All the faces in the database are encoded and stored for inference!!!")
				return "Training Completed"
		else:
			path = 'dataset_faces_v2.1.dat'
			with open(path, 'wb') as f:
				pickle.dump(known_face_encodings, f)
			print("All the faces in the database are encoded and stored for inference!!!")
			return "Training Completed"
	else:
		return "No faces to train"
