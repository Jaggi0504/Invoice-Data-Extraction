import cv2
import numpy as np


def shadow_remove(image)
	dilated_img = cv2.dilate(img, np.ones((7,7), np.uint8)) 
	bg_img = cv2.medianBlur(dilated_img,21)
	# bg_img = cv2.GaussianBlur(dilated_img,(7,7),1)
	diff_img = 255 - cv2.absdiff(img, bg_img)
	norm_img = diff_img.copy() # Needed for 3.x compatibility
	cv2.normalize(diff_img, norm_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
	_, thr_img = cv2.threshold(norm_img, 230, 0, cv2.THRESH_TRUNC)
	cv2.normalize(thr_img, thr_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

	# cv2.imwrite('faiz1_ouput.jpg',thr_img)

	# img_erosion = cv2.erode(thr_img, np.ones((3,3), np.uint8), iterations=1)
	# cv2.imwrite('faiz1_ouput.jpg',img_erosion)
	
	return thr_img