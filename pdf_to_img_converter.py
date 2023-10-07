# Convert PDF file into image

# pip install pdf2image

from pdf2image import convert_from_path

import os
from os import listdir
from os.path import isfile, join

# dir_path = os.path.splitext("D:\Tarun_workspace\projects_development\PDF_3_dataset\images")[0]

# input_dir = "D:\Tarun_workspace\projects_development\PDF_3_dataset\pdf"
# output_dir = "D:\Tarun_workspace\projects_development\PDF_3_dataset\images"

input_dir = r"C:\Harshil\Study\Semester_3\\capstone_project\data\10_templates\shivam\pdfs"
output_dir = input_dir + "\\images"

# Check if 'image' directory exist or not. Create if not exist.
if not os.path.exists(output_dir):
	os.makedirs(output_dir)


print("Converting:")
n=1

for file in listdir(input_dir):
	# print(os.path.splitext(file)[0])

	if file.endswith(".PDF") or file.endswith(".pdf"):
		pdf_path = os.path.join(input_dir, file)
		print(pdf_path)	# here we get the path of each pdf file in the directory

		# Now, convert each pdf file into image and save in the destination folder
		pages = convert_from_path(pdf_path)

		img_path = os.path.join(output_dir, os.path.splitext(file)[0])
		# print(img_path)

		print("   ...... file - ", n)
		n+=1

		i=1
		for page in pages:
			print("   ............ page - ", i)
			page.save(img_path + str(i) + '.jpg', 'JPEG')
			i+=1

	# print(img)

