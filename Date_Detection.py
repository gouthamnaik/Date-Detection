import re
import datetime
import cv2
import os

# From resizeimage import resizeimage

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import PIL.Image

from tqdm import tqdm

import pytesseract
from pytesseract import image_to_string

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Imgs folder name
path = "imgs"
results = []
month_dict = dict(jan='01', feb='02', mar='03', apr='04', may='05', jun='06', jul='07', aug='08', sep='09', oct='10', nov='11', dec='12')

def word_to_num(string):
    """
    This function converts a string to lowercase and only accepts the first three letter.
    This is to prepare a string for month_dict
    Example:
        word_to_num('January') -> jan
    """

    s = string.lower()[:3]
    return month_dict[s]

def date_converter(string):
    """
    This function extracts dates in every format from text and converts them to YYYYMMDD.
    Example:
        date_converter("It was the May/1/2009") -> 01-05-2009
    """
    results = []
    day = '01'
    month = '01'
    year = '1900'

    # This is in the form of DD-MM-YYYY or DD.MM.YYYY or DD/MM/YYYY
    date = re.search('(0?[1-9]|[12][0-9]|3[0-1])(\.|-|/)(0?[1-9]|1[0-2])(\.|-|/)(20[01][0-9]|\d\d)', string)
    
    # This is in the form of MM-DD-YYYY or MM.DD.YYYY or MM/DD/YYYY
    date1 = re.search('(0?[1-9]|1[0-2])(\.|-|/)(0?[1-9]|[12][0-9]|3[0-1]|[00])(\.|-|/)(20[01][0-9]|\d\d)', string)

    # Removes Single quotes from string and creates spaces
    string = string.replace("'", ' ').replace("Jan", " Jan ").replace("JAN", " Jan ").replace("Feb", " Feb ").replace("FEB", 
      " Feb ").replace("Mar", " Mar ").replace("MAR", " Mar ").replace("Apr", " Apr ").replace("APR", " Apr ").replace("May",
      " May ").replace("MAY", " May ").replace("Jun", " Jun ").replace("JUN", " Jun ").replace("Jul", " Jul ").replace("JUL", 
      " Jul ").replace("Aug", " Aug ").replace("AUG", " Aug ").replace("Sep", " Sep ").replace("SEP", " Sep ").replace("Oct", 
      " Oct ").replace("OCT", " Oct ").replace("Nov", " Nov ").replace("NOV", " Nov ").replace("Dec", " Dec ").replace("DEC", 
      " Dec ")
    
    # This is in the form of DD-Month-YYYY or DD.Month.YYYY or DD/Month/YYYY
    month1 = re.search(
        '(0?[1-9]|[12][0-9]|3[0-1])(?:st|nd|rd|th)?\s*[-|/|.\s]\s*(Jan(?:uary)?|JAN(?:UARY)?|Feb(?:ruary)?|FEB(?:RUARY)?|Mar(?:ch)'
        '?|MAR(?:CH)?|Apr(?:il)?|APR(?:IL)?|May|MAY|June?|JUNE?|July?|JULY?|Aug(?:ust)?|AUG(?:UST)?|Sept(?:ember)?|SEPT'
        '(?:EMBER)?|Sep(?:tember)?|SEP(?:TEMBER)?|Oct(?:ober)?|OCT(?:OBER)?|Nov(?:ember)?|NOV(?:EMBER)?|Dec(?:ember)?|DEC(?:EMB'
        'ER)?).?\s*[-|/|.\s]\s*(20[01][0-9]|\d\d)', string)
    
    # This is in the form of Month-DD-YYYY or Month.DD.YYYY or Month/DD/YYYY
    month2= re.search(
        '(Jan(?:uary)?|JAN(?:UARY)?|Feb(?:ruary)?|FEB(?:RUARY)?|Mar(?:ch)?|MAR(?:CH)?|Apr(?:il)?|APR(?:IL)?|May|June?|JUNE?|'
        'July?|JULY?|Aug(?:ust)?|AUG(?:UST)?|Sept(?:ember)?|SEPT(?:EMBER)?|Sep(?:tember)?|SEP(?:TEMBER)?|Oct(?:ober)?|OCT(?:OBER)?|Nov(?:ember)?|NOV(?:EM'
        'BER)?|Dec(?:ember)?|DEC(?:EMBER)?).?\s*[-|/|.\s]\s*(0?[1-9]|[12][0-9]|3[0-1])(?:st|nd|rd|th)?\s*[-|/|.,\s]\s*(20[01][0-9]|\d\d)'
        , string)
    
    if date:
        day = date.group(1)
        month = date.group(3)
        year = date.group(5)
    elif date1:
        day = date1.group(3)
        month = date1.group(1)
        year = date1.group(5)
    elif month1:
        day = month1.group(1)
        month = word_to_num(month1.group(2))
        year = month1.group(3)
    elif month2:
        day = month2.group(2)
        month = word_to_num(month2.group(1))
        year = month2.group(3)
    else:
        return "Not Found"
    
    # Make sure all variables have correct number, add zeros if necessary
    month = month.zfill(2)
    day = day.zfill(2)
    if day == '00':
        day = '01'
    if year is not None and len(year) == 2:
        year = '20' + year

    # Day-Month-Year        
    results.append(day + "-" + month + "-" + year)
    return results


count = 0

for r, d, f in (os.walk(path)):
    a = f.sort(key=len)
    for file in f:
        if '.jpg' in file:
            a = (os.path.join(r, file))
            print("=" * 50)
            print(a)
            img = cv2.imread(a)
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
            img = cv2.blur(img, (2, 2))
            img = cv2.GaussianBlur(img, (1, 1), 0)
            text = pytesseract.image_to_string(img)
            D = date_converter(text) 
            if D == "Not Found":
                output = pytesseract.image_to_string(PIL.Image.open(a).convert("RGB"), lang='eng', config='--psm 1')
                D = date_converter(output)
                if D == "Not Found":
                    im = PIL.Image.open(a)
                    dimg = ImageOps.grayscale(im)
                    contrast = ImageEnhance.Contrast(dimg)
                    eimg = contrast.enhance(5.5)
                    out_text = pytesseract.image_to_string(eimg)
                    D = date_converter(out_text)
                    if D == "Not Found":
                        print("Date not found")
                        continue
            print(D)

            # Num of dates found in a folder
            count = count + 1
            #print(count)