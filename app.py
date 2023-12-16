# Importing essential libraries
from flask import Flask,render_template,request,redirect,url_for,send_from_directory,jsonify,flash
from werkzeug.utils import secure_filename
import os
import socket
import re
import pandas as pd
import cv2
import pytesseract

############################################################
## Custom imports that are implemented for our application ##

import custom.initialize_run as initrun
from custom.create_today_folder import create_today_folder
from custom.storing import store_excel, store_json
#############################################################
custom_config=r'--psm 6 --tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'


# defining our flask application
app = Flask(__name__)


# When the file will uploaded it will be in this api_input folder
api_input= r'./api_input'
folder=create_today_folder(api_input)
UPLOAD_FOLDER=folder
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

'''Get host IP address'''
hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)


## initializing our model and tesseract config
initrun.init()

# a final dictionary to contain our final data
dictimages={}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_api', methods=['GET', 'POST'])
def upload_api():
    if request.method == 'POST':
        # check if the post request has the file part
        file_flag = 0
        if 'files' not in request.files:
            flash('Error accured')
            return redirect(request.url)
        files = request.files.getlist('files')
        for file in files:
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder=create_today_folder(api_input)
                UPLOAD_FOLDER=folder
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                try :
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    txt_img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    txt_out=pytesseract.image_to_string(txt_img,config=custom_config)
                    print(len(txt_out))
                    if len(txt_out)<50:
                        file_flag = 1
                        break
                    dictpred = initrun.run(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    dictimages[filename]= dictpred.copy()

                except Exception as e:
                    print(e) 
        
        if file_flag==1:
           resp = "Image does not contain enough text to extract"
           resp = jsonify(resp)
        else:            
            resp = jsonify(dictimages)
            resp.status_code = 201
            final_dict_df = pd.DataFrame.from_dict(dictimages,orient='index')
            # print(final_dict_df)
            store_json(dictimages)
            store_excel(final_dict_df)
            dictimages.clear()
    
    return resp

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        file_flag = 0
        if 'files' not in request.files:
            flash('Error accured')
            return redirect(request.url)
        files = request.files.getlist('files')
        images = []
        for file in files:
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder=create_today_folder(api_input)
                UPLOAD_FOLDER=folder
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                try :
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    txt_img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    txt_out= pytesseract.image_to_string(txt_img,config=custom_config)
                    print(len(txt_out))
                    if len(txt_out)<50:
                        file_flag = 1
                        break
                    dictpred = initrun.run(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    dictimages[filename]= dictpred.copy()

                except Exception as e:
                    print(e) 
        
        if file_flag==1:
           resp = "Image does not contain enough text to extract"
           resp = jsonify(resp)
           return resp
        else:            
            resp = jsonify(dictimages)
            resp.status_code = 201
            final_dict_df = pd.DataFrame.from_dict(dictimages)
            orient_df = pd.DataFrame.from_dict(dictimages, orient = 'index')
            # final_dict_df['Images'] = images
            print(final_dict_df)    
            store_json(dictimages)
            store_excel(orient_df)
            dictimages.clear()

            return render_template('ide_result.html', data = final_dict_df)
    # return resp
    return render_template('ide_home.html', result = dictimages)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5051,debug = True)