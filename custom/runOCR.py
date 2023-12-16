import cv2 
import pytesseract
import pdb
import re
# Adding custom options

pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
tessdata_dir_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'

custom_config=r'--psm 6 --tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'
# custom_config= r'--oem 3 --psm 11'
# custom_config =r'--psm 6 --oem 3'

def runOCR(img,x1,y1,x2,y2,cname):
    try :
        roi=img[y1:y2,x1:x2]
        output=pytesseract.image_to_string(roi,config=custom_config)
        return output
    except Exception as e:
        print(e)


def runtableOCR(img,x1,y1,x2,y2,cname):
    try :
        roi=img[y1:y2,x1:x2]
        cv2.imwrite('table.jpg',roi)
        cord_text=[]
        table_data = pytesseract.image_to_data(roi,config=custom_config)
        # print(table_data)
        parse_text = []
        last_word = ''
        # pdb.set_trace()
        for x,b in enumerate(table_data.splitlines()):
            if x!=0:
                b=b.split()
                if len(b)==12:
                    x, y, w, h, text= int(b[6]),int(b[7]),int(b[8]),int(b[9]),b[11]
                    if re.fullmatch(r'—', text) or re.fullmatch(r'=', text):
                        continue      
                    else:
                        text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)
                        cord_text.append([x,y,x+w,h+y,text])
        print(cord_text)
        sortedcord=runsorting(cord_text)
        # print(sortedcord)
        if(sortedcord==1):
            sortedcord=pytesseract.image_to_string(roi,config=custom_config)

        return sortedcord

    except Exception as e:
        print(e)


def cellconcate(oglist):
    # print(oglist)
    try:
        newlist=[]
        for cell in oglist:
            newcell=[]
            for i,c in enumerate(cell):            
                if i==0:
                    newcell.append(c)

                elif abs(c[0]-newcell[len(newcell)-1][2]) < 60:
                    newcell[len(newcell)-1][2],newcell[len(newcell)-1][3] = c[2],c[3]
                    newcell[len(newcell)-1][4] = newcell[len(newcell)-1][4]+' '+c[4]
                else:
                    newcell.insert(len(newcell),c)
            newcell=colsort(newcell)
            newlist.append(newcell)
        for cell in newlist:
            for c in cell:
                if c[4]=='.':
                    cell.remove(c)    
        return newlist
    except Exception as e:
        print(e)

def rowsort(oglist):

    ## row wise sorting
    ysort=sorted(oglist, key= lambda x : [x[1],x[3]])   
    return ysort


def colsort(oglist):
    ## column wise sorting
    xsort=sorted(oglist, key= lambda x : [x[0],x[2]])   
    return xsort

def runsorting(oglist):
    rows=[]
    tmp=[]

    ysorted=rowsort(oglist)
    # print(ysorted)
    thresh=30
    for i,t in enumerate(ysorted):
        if i==0:
            first=t
            tmp.append(t)

        elif t[1] in range(first[1]-thresh,first[1]+thresh):
            first=t
            tmp.append(t)

        else:
            rows.append(colsort(tmp))
            tmp=[]
            first=t
            tmp.append(t)
    rows.append(colsort(tmp))    
    print("rows :",rows)
    new_rows= cellconcate(rows)
    
    return new_rows

def makedictionary(rows):
    dict_cat={}
    # for i,row in enumerate(rows):
    #     vals=[]
    #     for j,r in enumerate(row):
    #         if j==0:
    #             dict_key=r[4]
    #         else:
    #             vals.append(r[4])

    #     if(len(vals)==1):
    #         vals=vals[0]        
    #     dict_cat[dict_key]=vals
    # return dict_cat
    # print(rows)
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
    return dict_cat
