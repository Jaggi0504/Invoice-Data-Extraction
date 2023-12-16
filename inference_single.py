from ultralytics import YOLO
import cv2
from ultralytics.utils.plotting import Annotator 

import matplotlib.pyplot as plt
import os
import json
import cv2 
import pytesseract
import numpy as np
import imagehash
from PIL import Image
import re

import pdb 
###################
# custome imports
###################

from custom.runOCR import runOCR, runtableOCR
from custom.create_today_folder import create_today_folder

checkpoint_file = r"C:\Harshil\Study\Semester_3\\capstone_project\Final_project\Invoice_data_extractor_API\model_checkpoints\Invoice_data_extractor_model.pt"

model = YOLO(checkpoint_file)

img=r"C:\Harshil\Study\Semester_3\\capstone_project\Final_project\Invoice_data_extractor_API\test_3.JPG"

image=cv2.imread(img)

# hashvalue= imagehash.average_hash(Image.open(img))
# result = inference_detector(model,img)
# predicts=[]

results = model.predict(source=image)
# print(results)

# for r in results:

#         boxes = r.boxes
#         for box in boxes:
#             b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
#             c = box.cls
#             print(b)
#             print(c)


predicts = []
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

# for res, cname in zip(result,class_names):
# 		try:
# 			# print(res[0])
# 			r=list(res[0])
# 			r.append(cname)
# 			predicts.append(r)
# 		except Exception as e:
# 			print(e)

# print(predicts)
ocrdict = {}
bad_count=0
dict_cat={}

for pred in predicts:
	try:
		x1,y1,x2,y2,acc,class_name=int(pred[0]),int(pred[1]),int(pred[2]),int(pred[3]),pred[4],pred[5]
		if(class_name =="table"):
			rows = runtableOCR(image,x1,y1,x2,y2,class_name)
			for i,row in enumerate(rows):
				if i==0:
					vals=[]
					keyname=i
					for r in row:
						vals.append(r[4])
					dict_cat[keyname]=vals

				else:
					vals=[]
					for j,r in enumerate(row):
						vals.append(r[4])
					if(len(vals)==1):
						vals=vals[0]
					dict_key=i		
					dict_cat[dict_key]=vals
			# ocrdict['table'] = dict_cat
		else:
			output= runOCR(image,x1,y1,x2,y2,class_name)	
			output=output.replace("\n",",")
			output = re.sub(r'\n', ', ', output).rstrip(',')
			output = re.sub(r'(\d+),(\d+)', r'\1.\2', output)
			ocrdict[class_name]=output

		# cv2.rectangle(image,(x1,y1),(x2,y2),(36,255,12),1)

	except Exception as e:
		print(e)

# if bad_count>3 or len(predicts)<=2: 
# 	print("bad called")
# 	cv2.imwrite("./failed_images/og_failed.jpg",ogimage)
# 	cv2.imwrite("./failed_images_w_boxes/predicted_failed.jpg",image)


ocrdict['table'] = dict_cat

print(ocrdict)
cv2.imwrite("test_output.jpg",image)

json_output=json.dumps(ocrdict,indent=4)

with open("json_output.json","w") as f:
	json.dump(ocrdict,f)

