from custom.pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
from scipy.ndimage import interpolation as inter
import numpy as np
import argparse
import cv2
import imutils
import os

from custom.create_today_folder import create_today_folder

preprocessing_folder='./preprocessing_done'

def determine_score(arr, angle):
	try:
	    data = inter.rotate(arr, angle, reshape=False, order=0)
	    histogram = np.sum(data, axis=1, dtype=float)
	    score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
	    return histogram, score
	except Exception as e:
		print(e)


def correct_skew(image, delta=1, limit=5):
	try:
	    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

	    scores = []
	    angles = np.arange(-limit, limit + delta, delta)
	    for angle in angles:
	        histogram, score = determine_score(thresh, angle)
	        scores.append(score)

	    best_angle = angles[scores.index(max(scores))]

	    (h, w) = image.shape[:2]
	    center = (w // 2, h // 2)
	    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
	    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

	    return best_angle, rotated
	except Exception as e:
		print(e)

def shadow_remove(img):
	try:
		dilated_img = cv2.dilate(img, np.ones((7,7), np.uint8)) 
		bg_img = cv2.medianBlur(dilated_img,21)
		# bg_img = cv2.GaussianBlur(dilated_img,(7,7),1)
		diff_img = 255 - cv2.absdiff(img, bg_img)
		norm_img = diff_img.copy() # Needed for 3.x compatibility
		cv2.normalize(diff_img, norm_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
		_, thr_img = cv2.threshold(norm_img,225, 0, cv2.THRESH_TRUNC)
		cv2.normalize(thr_img, thr_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
		# eroded=cv2.erode(thr_img,np.ones((1,1),np.uint8),iterations=1)

		return thr_img
	except Exception as e:
		print(e)


def getwarped(image):
	try:
		imagename=os.path.basename(image)
		ogpath=image
		image=cv2.imread(ogpath)
		ratio = image.shape[0] / 500.0
		orig = image.copy()
		image = imutils.resize(image, height = 500)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (3, 3), 0)
		edged = cv2.Canny(gray, 100,190)
		cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
		# loop over the contours
		isnotfound=False
		for c in cnts:
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.02 * peri, True)
			if len(approx) == 4:
				screenCnt = approx
				x,y,w,h = cv2.boundingRect(screenCnt)
				if int(h)<200:
					print("wrong bounding box")
					isnotfound=True
				break
			else:
				isnotfound=True

		if isnotfound:
			image=cv2.imread(ogpath)
			image=shadow_remove(image)
			warped = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			T = threshold_local(warped, 11, offset = 10, method = "gaussian")
			warped = (warped > T).astype("uint8") * 255
			angle, cured_image= correct_skew(warped)
			folder=create_today_folder(preprocessing_folder)
			writepath=os.path.join(folder,os.path.splitext(imagename)[0]+'_processed.jpg')
			cv2.imwrite(writepath,cured_image)

			return writepath

		else:
			warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
			warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
			T = threshold_local(warped, 11, offset = 10, method = "gaussian")
			warped = (warped > T).astype("uint8") * 255
			angle, warped= correct_skew(warped)
			
			folder=create_today_folder(preprocessing_folder)
			writepath=os.path.join(folder,os.path.splitext(imagename)[0]+'_processed.jpg')
			cv2.imwrite(writepath,warped)

			return writepath

	except Exception as e:
		print(e)




# # imagename = r"C:\Harshil\Study\Semester_3\\capstone_project\data\Proton_Health_AI_API\\custom\Image_41.jpg"
# write_path = getwarped(imagename)

# print(write_path)