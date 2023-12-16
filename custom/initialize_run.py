# Libraries for Object Detection
from ultralytics import YOLO
import cv2
from PIL import Image
import imagehash
import cv2
import os
import datetime  
import json
import numpy as np
import re

from custom.runOCR import runOCR,runtableOCR,makedictionary
from custom.global_data import checkpoint_file
from custom.storing import store_image
predicts=[]

def init():
	try :
		global model
		# build the model from a config file and a checkpoint file
		# model = torch.hub.load('ultralytics/yolov5', 'custom', path=checkpoint_file)  # default
		model = YOLO(checkpoint_file)
	except Exception as e:
		print(e)

def process_table(image,x1, y1, x2, y2, acc, class_name):
	rows = runtableOCR(image,x1,y1,x2,y2,class_name)
	dict_cat=makedictionary(rows)
	return dict_cat

def process_entity(image,x1, y1, x2, y2, acc, class_name):
	
	output= runOCR(image,x1,y1,x2,y2,class_name)
	output=output.replace("\n",",")
	output= re.sub(r'\n', ', ', output).rstrip(',')
	output= re.sub(r'(\d+),(\d+)', r'\1.\2', output)
	output=output.replace("\n\n",'')
	output=output.replace("~",'')
	output=output.replace("|",'')

	return output

def run(img):
	try:
		ocrdict={}
		ocrdict.clear()
		dict_cat={}
		dict_cat.clear()
		image_name=os.path.basename(img)
		original=cv2.imread(img)
		image=cv2.imread(img)
		# predictions = model(img)
		results = model.predict(source=image, save=False)
		predicts.clear()		
		for r in results:
			# Extract bounding boxes, classes, names, and confidences
			boxes = results[0].boxes.xyxy.tolist()
			classes = results[0].boxes.cls.tolist()
			names = results[0].names
			confidences = results[0].boxes.conf.tolist()

			# Iterate through the results
			for box, cls, conf in zip(boxes, classes, confidences):
			    x1, y1, x2, y2 = box
			    confidence = conf
			    name = cls
			    detected_class = names[int(cls)]
			    x1,y1,x2,y2,acc,class_name, class_id = float(x1),float(y1),float(x2),float(y2), float(confidence), detected_class, name
			    predicts.append([x1,y1,x2,y2,acc,class_name, class_id])

			for pred in predicts:
				try:
					x1,y1,x2,y2,acc,class_name=int(pred[0]),int(pred[1]),int(pred[2]),int(pred[3]),pred[4],pred[5]
					if class_name=="table":
						dict_cat= process_table(image,x1, y1, x2, y2, acc, class_name)
						ocrdict.update(table = dict_cat)
					else:
						output = process_entity(image,x1, y1, x2, y2, acc, class_name)
						ocrdict[class_name]=output
				except Exception as e:
					print(e)

		return ocrdict
		# cv2.rectangle(image,(x,y),(x+w,y+h),(200,0,0),2)
	except Exception as e:
		print(e)

