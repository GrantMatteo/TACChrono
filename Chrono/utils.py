# Copyright (c) 2018 
# Amy L. Olex, Virginia Commonwealth University
# alolex at vcu.edu
#
# Luke Maffey, Virginia Commonwealth University
# maffeyl at vcu.edu
#
# Nicholas Morton,  Virginia Commonwealth University 
# nmorton at vcu.edu
#
# Bridget T. McInnes, Virginia Commonwealth University
# btmcinnes at vcu.edu
#
# This file is part of Chrono
#
# Chrono is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Chrono is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chrono; if not, write to 
#
# The Free Software Foundation, Inc., 
# 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.



## Provides all helper functions for Chrono methods. 


import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import sent_tokenize
from nltk.stem.snowball import SnowballStemmer
# from Chrono import chronoEntities as t6
from Chrono import temporalTest as tt
import dateutil.parser
# import datetime
# from Chrono import TimePhrase_to_Chrono
from Chrono import LabelPhraseEntity as tp
import re
import csv
from collections import OrderedDict
import numpy as np
#from word2number import w2n
from Chrono import w2ny as w2n
import string
import copy
## Parses a text file to idenitfy all tokens seperated by white space with their original file span coordinates.
# @author Amy Olex
# @param file_path The path and file name of the text file to be parsed.
# @return text String containing the raw text blob from reading in the file.
# @return tokenized_text A list containing each token that was seperated by white space.
# @return spans The coordinates for each token.

def getWhitespaceTokens(file_path):
    file = open(file_path, "r")
    text = file.read()
    ## Testing the replacement of all "=" signs by spaces before tokenizing.
    text = text.translate(str.maketrans("=", ' '))

    span_generator = WhitespaceTokenizer().span_tokenize(text)
    spans = [span for span in span_generator]
    tokenized_text = WhitespaceTokenizer().tokenize(text)
    tags = nltk.pos_tag(tokenized_text)

    sent_tokenize_list = sent_tokenize(text)
    sent_boundaries = [0] * len(tokenized_text)

    ## figure out which tokens are at the end of a sentence
    tok_counter = 0


    for s in range(0, len(sent_tokenize_list)):
        sent = sent_tokenize_list[s]

        if "\n" in sent:
            sent_newline = sent.split("\n")
            for sn in sent_newline:
                sent_split = WhitespaceTokenizer().tokenize(sn)
                nw_idx = len(sent_split) + tok_counter - 1
                sent_boundaries[nw_idx] = 1
                tok_counter = tok_counter + len(sent_split)


        else:
            sent_split = WhitespaceTokenizer().tokenize(sent)
            nw_idx = len(sent_split) + tok_counter - 1
            sent_boundaries[nw_idx] = 1
            tok_counter = tok_counter + len(sent_split)


    return text, tokenized_text, spans, tags, sent_boundaries
## Reads in the dct file and converts it to a datetime object.
# @author Amy Olex
# @param file_path The path and file name of the dct file.
# @return A datetime object

## Writes out the full XML file for all T6entities in list.
# @author Amy Olex
# @param chrono_list The list of Chrono objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
def write_xml(chrono_list, outfile):
    fout = open(outfile + ".completed.xml", "w")
    fout.write("<data>\n<annotations>\n")
    for c in chrono_list :
        fout.write(str(c.print_xml()))
    
    fout.write("\n</annotations>\n</data>")
    fout.close()
 ####
 #END_MODULE
 ####   


## Marks all the reference tokens that show up in the TimePhrase entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param tpList The list of TimePhrase entities to compare against
### I don't think we need/use this any longer.  Maybe can be recycled for something else.
#def markTemporalRefToks(refToks, tpList):
#    for ref in refToks:
#        for tp in tpList:
#            tpStart, tpEnd = tp.getSpan()
#            if ref.spanOverlap(tpStart, tpEnd):
#                ref.setTemporal(True)
#        if ref.isTemporal() is None:
#            ref.setTemporal(False)
#    return refToks
####
#END_MODULE
####
    
## Takes in a text string and returns the numerical value
# @author Amy Olex
# @param text The string containing our number
# @return value The numerical value of the text string, None is returned if there is no number
def getNumberFromText(text):
    try :
        number = w2n.word_to_num(text)
    except ValueError:
        number = isOrdinal(text)
    return number
####
#END_MODULE
####  

## Function to identify an ordinal number
# @author Amy Olex
# @param text The text string to be tested for an ordinal.
def isOrdinal(text):
    text_lower = text.lower()
    if text_lower == '1st' or text_lower== 'first': #re.search('1st|first', text_lower) is not None):
        number = 1
    elif text_lower == '2nd' or text_lower== 'second':
        number = 2
    elif text_lower == '3rd' or text_lower== 'third':
        number = 3
    elif text_lower == '4th' or text_lower== 'fourth':
        number = 4
    elif text_lower == '5th' or text_lower== 'fifth':
        number = 5
    elif text_lower == '6th' or text_lower== 'sixth':
        number = 6
    elif text_lower == '7th' or text_lower== 'seventh':
        number = 7
    elif text_lower == '8th' or text_lower== 'eighth':
        number = 8
    elif text_lower == '9th' or text_lower== 'nineth':
        number = 9
    elif text_lower == '10th' or text_lower== 'tenth':
        number = 10
    elif text_lower == '11th' or text_lower== 'eleventh':
        number = 11
    elif text_lower == '12th' or text_lower== 'twelveth':
        number = 12
    elif text_lower == '13th' or text_lower== 'thirteenth':
        number = 13
    elif text_lower == '14th' or text_lower== 'fourteenth':
        number = 14
    elif text_lower == '15th' or text_lower== 'fifteenth':
        number = 15
    elif text_lower == '16th' or text_lower== 'sixteenth':
        number = 16
    elif text_lower == '17th' or text_lower== 'seventeenth':
        number = 17
    elif text_lower == '18th' or text_lower== 'eighteenth':
        number = 18
    elif text_lower == '19th' or text_lower== 'nineteenth':
        number = 19
    elif text_lower == '20th' or text_lower== 'twentieth':
        number = 20
    elif text_lower == '21st' or text_lower== 'twenty first':
        number = 21
    elif text_lower == '22nd' or text_lower== 'twenty second':
        number = 22
    elif text_lower == '23rd' or text_lower== 'twenty third':
        number = 23
    elif text_lower == '24th' or text_lower== 'twenty fourth':
        number = 24
    elif text_lower == '25th' or text_lower== 'twenty fifth':
        number = 25
    elif text_lower == '26th' or text_lower== 'twenty sixth':
        number = 26
    elif text_lower == '27th' or text_lower== 'twenty seventh':
        number = 27
    elif text_lower == '28th' or text_lower== 'twenty eighth':
        number = 28
    elif text_lower == '29th' or text_lower== 'twenty nineth':
        number = 29
    elif text_lower == '30th' or text_lower== 'thirtieth':
        number = 30
    elif text_lower == '31st' or text_lower== 'thirty first':
        number = 31
    else:
        number = None
    
    return number
       
####
#END_MODULE
####    
  
## Function to get the integer representation of a text month
# @author Amy Olex  
# @param text The text string to be converted to an integer.
def getMonthNumber(text):
    month_dict = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10,'November':11, 'December':12,
                  'JANUARY':1, 'FEBRUARY':2, 'MARCH':3, 'APRIL':4, 'MAY':5, 'JUNE':6, 'JULY':7, 'AUGUST':8, 'SEPTEMBER':9, 'OCTOBER':10,'NOVEMBER':11, 'DECEMBER':12, 
                  'january':1, 'february':2, 'march':3, 'april':4, 'june':6, 'july':7, 'august':8, 'september':9, 'october':10,'november':11, 'december':12,
                  'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'Jun':6, 'Jul':7, 'Aug':8, 'Sept':9, 'Sep':9, 'Oct':10,'Nov':11, 'Dec':12,
                  'jan':1, 'feb':2, 'mar':3, 'apr':4, 'jun':6, 'jul':7, 'aug':8, 'sept':9, 'sep':9, 'oct':10,'nov':11, 'dec':12,
                  'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'JUN':6, 'JUL':7, 'AUG':8, 'SEPT':9, 'SEP':9, 'OCT':10,'NOV':11, 'DEC':12,
                  '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, '11':11, '12':12,
                  '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        value = month_dict[text]
    except KeyError:
        value = 100
    
    return value
   
## Function to determine if the input span overlaps this objects span
# @author Amy Olex
# @param sp1 a 2-tuple with the first start and end span
# @param sp2 a 2-tuple with the second start and end span
# @output True or False
def overlap(sp1, sp2) :
    x=set(range(int(sp1[0]), int(sp1[1])))
    y=set(range(int(sp2[0]), int(sp2[1])))
    if list(set(x) & set(y)) != []:
        return True
    else:
        return False 
        
        
        
## Function to extract prediction features
# @author Amy Olex
# @param reftok_list The full document being parsed as a list of tokens.
# @param reftok_idx The index of the target token in the reference list.
# @param feature_dict A dictionary with the features to be extracted listed as the keys and the values all set to zero.
# @return A dictionary with the features as keys and the values set to 0 if not present, and 1 if present for the target word.
def extract_prediction_features(reftok_list, reftok_idx, feature_dict) :

    reftok = reftok_list[reftok_idx]
    window = 5
    
    ### Extract the stem feature
    my_str = reftok.getText()
    stemmer = SnowballStemmer("english")
    my_stem = stemmer.stem(reftok.getText().lower())
    if(my_stem in feature_dict.keys()):
        feature_dict[my_stem] = '1'
    
    
    ### identify the numeric feature
    before = max(reftok_idx-1,0)
    after = min(reftok_idx+1,len(reftok_list)-1)
    
    if(before != reftok_idx and isinstance(getNumberFromText(reftok_list[before].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    elif(after != reftok_idx and isinstance(getNumberFromText(reftok_list[after].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    else:
        feature_dict['feat_numeric'] = '0'


    ## identify bow feature
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)
    
    for r in range(start, end):
        if r != reftok_idx:
            num_check = getNumberFromText(reftok_list[r].getText())
            if(isinstance(num_check, (int))):
                if(num_check in feature_dict.keys()):
                    feature_dict[num_check] = '1'
            else:
                txt = reftok_list[r].getText()
                if(txt in feature_dict.keys()):
                    feature_dict[txt] = '1'

    ## identify temp_self feature    
    if reftok.isTemporal():
        feature_dict['feat_temp_self'] = '1'
    
    ## identify temp_context within 3 words to either side of the target.
    start = max(reftok_idx-window,0)
    end = min(reftok_idx+(window+1),len(reftok_list)-1)
    for r in range(start, end):
        if r != reftok_idx:
            if reftok_list[r].isTemporal():
                feature_dict['feat_temp_context'] = '1'
                break

    return(feature_dict)
######
## END Function
###### 


## Function that get the list of features to extract from the input training data matrix file.
# @author Amy Olex
# @param data_file The name and path the the data file that contains the training matrix.  The first row is assumed to be the list of features.
# @return A dictionary with all the features stored as keys and the values set to zero.
def get_features(data_file):
    ## Import csv files
    data_list = []
    with open(data_file) as file:
        reader = csv.DictReader(file)
        data_list = [row for row in reader]

    ## Create the empty orderedDict to pass back for use in the other methods.
    dict_keys = data_list[0].keys()

    dic = OrderedDict(zip(dict_keys, list(np.repeat('0',len(dict_keys)))))
    
    return(dic)
######
## END Function
###### 

## Marks all the reference tokens that are identified as notable.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
def markNotable(refToks):
    for ref in refToks:
        ref.setNumeric(numericTest(ref.getText(), ref.getPos()))
        boole, tID =(temporalTest(ref.getText()))
        ref.setTemporal(boole)
        ref.setTemporalType(tID)
        ref.setNumericRange(isNumericRange(ref.getText()))
        ref.setAcronym(isAcronym(ref.getText()))
        ref
    return refToks

## Marks all the reference tokens that are identified as temporal.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
def isAcronym(tok):
    acronyms= ["hs","qhs","bid","qid","qod","tid","prn", "qam", "qpm", "w", "q"];
    tok = re.sub('['+string.punctuation+']', '', tok).strip()
    tok=tok.lower();
    return tok in acronyms

####
#END_MODULE
####

## Tests to see if the token is a number.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if numeric, false otherwise
def numericTest(tok, pos):
    
    if pos == "CD":
        return True
    else:
        #remove punctuation
        tok = tok.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).strip()
    
        #test for a number
        #tok.strip(",.")
        val = getNumberFromText(tok)
        if val is not None:
            return True
        return False
####
#END_MODULE
#### 

##Tests to see if a value is a range of numbers, to be treated like a number
# @author Grant Matteo
# @param tok the token string
# @return True if a range, False otherwise
def isNumericRange(tok):
    tok=tok.translate(str.maketrans(string.punctuation.replace('-', ''), ' '*(len(string.punctuation)-1))).strip()
    return (re.search('\d{1,2}\-\d{1,2}', tok) is not None)
## Tests to see if the token is a temporal value.
# @author Amy Olex
# @param tok The token string
# @return (Boolean true if temporal), (number indicating which temporal type was found)

def temporalTest(tok):
    #remove punctuation

    #if the token has a dollar sign or percent sign it is not temporal
    m = re.search('[#$%]', tok)
    if m is not None:
        return False, -1

    #look for date patterns mm[/-]dd[/-]yyyy, mm[/-]dd[/-]yy, yyyy[/-]mm[/-]dd, yy[/-]mm[/-]dd
    m = re.search('([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', tok)
    if m is not None:
        return True, 12
    #looks for a string of 8 digits that could possibly be a date in the format 19980304 or 03041998 or 980304
    m = re.search('([0-9]{4,8})', tok)
    if m is not None:
        if tt.has24HourTime(m.group(0)):
            return True, 0
        if tt.hasDateOrTime(m.group(0)):
            return True, 12



    #look for time patterns hh:mm:ss

    m = re.search('([0-9]{2}:[0-9]{2}:[0-9]{2})', tok)
    if m is not None:
        return True, 1
    if tt.hasTextMonth(tok):
        return True, 2
    if tt.hasDayOfWeek(tok):
        return True, 3
    if tt.hasPeriodInterval(tok):
        return True, 4
    if tt.hasAMPM(tok):
        return True, 5
    if tt.hasPartOfWeek(tok):
        return True, 6
    if tt.hasSeasonOfYear(tok):
        return True, 7
    if tt.hasPartOfDay(tok):
        return True, 8
    if tt.hasTimeZone(tok):
        return True, 9
    if tt.hasTempText(tok):
        return True, 10
    if tt.hasModifierText(tok):
        return True, 11

####
#END_MODULE
#### 

## Takes in a Reference List that has had numeric and temporal tokens marked, and identifies all the 
## temporal phrases by finding consecutive temporal tokens.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing
def getTemporalPhrases(chroList):
    #TimePhraseEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], temptype=j['type'], tempvalue=j['value'], =doctime)
    id_counter = 0
    
    phrases = [] #the empty phrases list of TimePhrase entities
    tmpPhrase = [] #the temporary phrases list.
    inphrase = False
    for n in range(0,len(chroList)):
        if chroList[n].isTemporal():
            print(chroList[n].getText() +"is temporal");
        elif chroList[n].isNumeric():
            print(chroList[n].getText() +"is numeric");
        elif chroList[n].isNumericRange():
            print(chroList[n].getText() +"is a range");
        else:
            if inphrase:
                inphrase = False
                if len(tmpPhrase) != 1:
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif not tmpPhrase[0].isNumeric():
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                elif tmpPhrase[0].isNumeric() and tmpPhrase[0].isTemporal():
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                else:
                    tmpPhrase = []
        
            
    return phrases

####
#END_MODULE
#### 


## Takes in a list of reference tokens identified as a temporal phrase and returns one TimePhraseEntity.
# @author Amy Olex
# @param items The list of reference tokesn
# @param counter The ID this TimePhrase entity should have
# @param doctime The document time.
# @return A single TimePhrase entity with the text span and string concatenated.
def createTPEntity(items, counter):
    start_span, tmp = items[0].getSpan()
    tmp, end_span = items[len(items)-1].getSpan()
    text = ""
    for i in items:
        text = text + ' ' + i.getText()
    
    return tp.LabelPhraseEntity(id=counter, text=text.strip(), start_span=start_span, end_span=end_span, temptype=None, tempvalue=None)

####
#END_MODULE
####   


## Takes in a reference list of tokens, a start span and an end span
# @author Amy Olex
# @param ref_list The list of reference tokens we want an index for.
# @param start_span The start span of the token we need to find in ref_list
# @param end_span The ending span of the token we need to find
# @return Returns the index of the ref_list token that overlaps the start and end spans provided, or -1 if not found.
def getRefIdx(ref_list, start_span, end_span):
    for i in range(0,len(ref_list)):
        if(overlap(ref_list[i].getSpan(),(start_span,end_span))):
            return i              
    return -1
    
####
#END_MODULE
####           

## Identifies the local span of the serach_text in the input "text"
# @author Amy Olex
# @param text The text to be searched
# @param search_text The text to search for.
# @return The start index and end index of the search_text string.
def calculateSpan(text, search_text):
    try:
        start_idx = text.index(search_text)
        end_idx = start_idx + len(search_text)
    except ValueError:
        return None, None

    return start_idx, end_idx