from custom.create_today_folder import create_today_folder
from custom.generate_voc import generate_xml

import cv2
import os
import json
from datetime import datetime


def store_image(imgpath,original,image,image_name,hashvalue,predicts,ocrdict):
    try :
        output_dir="./api_output"
        jsondata=json.dumps(ocrdict)  
        folder=create_today_folder(output_dir)
        predictionpath=os.path.join(folder,os.path.splitext(image_name)[0]+'_output.jpg')
        cv2.imwrite(predictionpath,image)
        generate_xml(original,image,image_name,predicts,folder)
        # insert_table(hashvalue,imgpath,predictionpath,jsondata)                   
    except Exception as e:
        print(e)

def store_excel(df):
    try :
        output_dir="./api_output"  
        folder=create_today_folder(output_dir)
        today = datetime.now()
        if today.hour < 12:
                h = "00"
        else:
            h = "12"

        timestring=today.strftime('%Y%m%d%H%M%S')
        outputpath=os.path.join(folder,'run'+timestring+'_output.xlsx')
        df.to_excel(outputpath, index = False)
    except Exception as e:
        print(e)


def store_json(json_obj):
    try :
        output_dir="./api_output"  
        folder=create_today_folder(output_dir)
        today = datetime.now()
        if today.hour < 12:
                h = "00"
        else:
            h = "12"

        timestring=today.strftime('%Y%m%d%H%M%S')
        outputpath=os.path.join(folder,'run'+timestring+'_output.json')
        with open(outputpath,'w') as j_file:
            json.dump(json_obj, j_file)
    except Exception as e:
        print(e)