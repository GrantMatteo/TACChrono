# coding=utf-8
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
from Chrono import DosePhraseEntity as dp
from Chrono import LabelPhraseEntity as tp
import re
import csv
from Chrono import referenceToken
from collections import OrderedDict
import numpy as np
import spacy
# from word2number import w2n
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

    # sent_tokenize_list = sent_tokenize(text)
    sent_boundaries = [0] * len(tokenized_text)

    ## figure out which tokens are at the end of a sentence
    tok_counter = 0

    return text, tokenized_text, spans, tags, sent_boundaries

## Does some processing that is necessary before constructing entities
# @author Grant Matteo
# @param phraseList the list of freqPhrases
# @return the modified list
def preProcessPhrases(phraseList):
    #combine "4 to 3" into one refTok for easier recognition
    for phrase in phraseList:
        tokList=phrase.getItems()
        n=1
        while n <len(tokList)-1:
            cleanText=re.sub("["+string.punctuation+"]", "", tokList[n].getText()).lower().strip()
            if (tokList[n-1].isNumericOnly() and cleanText=="to" and tokList[n+1].isNumericOnly()):
                fullText=tokList[n-1].getText()+" "+tokList[n].getText()+" " +tokList[n+1].getText()
                fullSpan= [tokList[n-1].getSpan()[0], tokList[n+1].getSpan()[1]]
                tokList[n]=referenceToken.refToken(id=tokList[n-1].getID(), text=fullText, start_span=fullSpan[0], end_span=fullSpan[1], pos=tokList[n-1].getPos(),
                             temporal=False)
                tokList[n].setNumericRange(True)
                tokList.pop(n-1)
                tokList.pop(n+1)
                n-=1
                print("New entity",fullText, fullSpan)
            n+=1
        phrase.setItems(tokList)
    #combine "four (4)" into one numeric refTok
    for phrase in phraseList:
        tokList=phrase.getItems()
        n=0
        while n <len(tokList)-1:
            cleanText=re.sub("["+string.punctuation+"]", "", tokList[n].getText()).lower().strip()
            if (cleanText in w2n.american_number_system.keys() and tokList[n+1].isNumeric()
                    and re.search("\(\d+\)", tokList[n+1].getText())):
                fullText=tokList[n].getText()+" " +tokList[n+1].getText()
                fullSpan= [tokList[n].getSpan()[0], tokList[n+1].getSpan()[1]]
                tokList[n]=referenceToken.refToken(id=tokList[n].getID(), text=fullText, start_span=fullSpan[0], end_span=fullSpan[1], pos=tokList[n].getPos(),
                             temporal=False)
                tokList[n].setNumeric(True)
                tokList.pop(n+1)
                n-=1
                print("New num entity",fullText, fullSpan)
            n+=1
        phrase.setItems(tokList)
## Writes out the full XML file for all T6entities in list.
# @author Amy Olex
# @param chrono_list The list of Chrono objects needed to be written in the file.
# @param outfile A string containing the output file location and name.
def write_xml(chrono_list, outfile):
    fout = open(outfile + ".ann", "w")
    for c in chrono_list:
        try:
            fout.write(str(c.print_xml()) + "\n")
        except:
            try:
                # print(c)
                fout.write(str(c[0].print_xml() + "\n"))
            except:
                print("MISSION FAILED")

    fout.close()


####
# END_MODULE
####

def write_ann(chrono_list, outfile):
    with open(outfile + ".ann", "w") as fout:
        for c in chrono_list:
            if not type(c) == list:
                fout.write(str(c.print_ann()) + "\n")


## Marks all the reference tokens that show up in the TimePhrase entity list.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @param tpList The list of TimePhrase entities to compare against
### I don't think we need/use this any longer.  Maybe can be recycled for something else.
# def markTemporalRefToks(refToks, tpList):
#    for ref in refToks:
#        for tp in tpList:
#            tpStart, tpEnd = tp.getSpan()
#            if ref.spanOverlap(tpStart, tpEnd):
#                ref.setTemporal(True)
#        if ref.isTemporal() is None:
#            ref.setTemporal(False)
#    return refToks
####
# END_MODULE
####

## Takes in a text string and returns the numerical value
# @author Amy Olex
# @param text The string containing our number
# @return value The numerical value of the text string, None is returned if there is no number
def getNumberFromText(text):
    try:
        number = w2n.word_to_num(text)
    except ValueError:
        number = None
    number= None if isOrdinal(text) is not None else number# This never occurs in Frequencies

    return number


## Checks to see if each dose phrase is part of a compound "body weight" unit (for TAC)
# @author Neha Dil
# @param text The whole text currently being parsed
# @param dosePhrases List of all the dosePhrases found
# @return The modified list of dose phrases
def compoundPhrase(text, dosePhrases):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    chunks = []
    for chunk in doc.noun_chunks:
        chunks.append(chunk.text)
    for dose in dosePhrases:
        for chunk in chunks:
            if dose.getText() in chunk and ("bw" in chunk.lower() or "b.w" in chunk.lower() or "body" in chunk.lower()):
                startpoint = text.find(chunk)
                endpoint = startpoint + len(chunk)
                if dose.getSpan()[0] >= startpoint and dose.getSpan()[1] <= endpoint:
                    start = chunk.find(dose.getText())
                    end = start + len(dose.getText())
                    rest = chunk[end:]
                    dose.setText(dose.getText() + rest)
                    dose.setSpan(dose.getSpan()[0], len(dose.getText()))
                    break
    return dosePhrases


####
# END_MODULE
####

## Function to identify an ordinal number
# @author Amy Olex
# @param text The text string to be tested for an ordinal.
def isOrdinal(text):
    text_lower = text.lower()
    if text_lower == '1st' or text_lower == 'first':  # re.search('1st|first', text_lower) is not None):
        number = 1
    elif text_lower == '2nd' or text_lower == 'second':
        number = 2
    elif text_lower == '3rd' or text_lower == 'third':
        number = 3
    elif text_lower == '4th' or text_lower == 'fourth':
        number = 4
    elif text_lower == '5th' or text_lower == 'fifth':
        number = 5
    elif text_lower == '6th' or text_lower == 'sixth':
        number = 6
    elif text_lower == '7th' or text_lower == 'seventh':
        number = 7
    elif text_lower == '8th' or text_lower == 'eighth':
        number = 8
    elif text_lower == '9th' or text_lower == 'nineth':
        number = 9
    elif text_lower == '10th' or text_lower == 'tenth':
        number = 10
    elif text_lower == '11th' or text_lower == 'eleventh':
        number = 11
    elif text_lower == '12th' or text_lower == 'twelveth':
        number = 12
    elif text_lower == '13th' or text_lower == 'thirteenth':
        number = 13
    elif text_lower == '14th' or text_lower == 'fourteenth':
        number = 14
    elif text_lower == '15th' or text_lower == 'fifteenth':
        number = 15
    elif text_lower == '16th' or text_lower == 'sixteenth':
        number = 16
    elif text_lower == '17th' or text_lower == 'seventeenth':
        number = 17
    elif text_lower == '18th' or text_lower == 'eighteenth':
        number = 18
    elif text_lower == '19th' or text_lower == 'nineteenth':
        number = 19
    elif text_lower == '20th' or text_lower == 'twentieth':
        number = 20
    elif text_lower == '21st' or text_lower == 'twenty first':
        number = 21
    elif text_lower == '22nd' or text_lower == 'twenty second':
        number = 22
    elif text_lower == '23rd' or text_lower == 'twenty third':
        number = 23
    elif text_lower == '24th' or text_lower == 'twenty fourth':
        number = 24
    elif text_lower == '25th' or text_lower == 'twenty fifth':
        number = 25
    elif text_lower == '26th' or text_lower == 'twenty sixth':
        number = 26
    elif text_lower == '27th' or text_lower == 'twenty seventh':
        number = 27
    elif text_lower == '28th' or text_lower == 'twenty eighth':
        number = 28
    elif text_lower == '29th' or text_lower == 'twenty nineth':
        number = 29
    elif text_lower == '30th' or text_lower == 'thirtieth':
        number = 30
    elif text_lower == '31st' or text_lower == 'thirty first':
        number = 31
    else:
        number = None

    return number


####
# END_MODULE
####

## Function to get the integer representation of a text month
# @author Amy Olex
# @param text The text string to be converted to an integer.
def getMonthNumber(text):
    month_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8,
                  'September': 9, 'October': 10, 'November': 11, 'December': 12,
                  'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
                  'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12,
                  'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6, 'july': 7, 'august': 8,
                  'september': 9, 'october': 10, 'november': 11, 'december': 12,
                  'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sept': 9, 'Sep': 9, 'Oct': 10,
                  'Nov': 11, 'Dec': 12,
                  'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sept': 9, 'sep': 9, 'oct': 10,
                  'nov': 11, 'dec': 12,
                  'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEPT': 9, 'SEP': 9, 'OCT': 10,
                  'NOV': 11, 'DEC': 12,
                  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12,
                  '01': 1, '02': 2, '03': 3, '04': 4, '05': 5, '06': 6, '07': 7, '08': 8, '09': 9, '10': 10, '11': 11,
                  '12': 12}
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
def overlap(sp1, sp2):
    x = set(range(int(sp1[0]), int(sp1[1])))
    y = set(range(int(sp2[0]), int(sp2[1])))
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
def extract_prediction_features(reftok_list, reftok_idx, feature_dict):
    reftok = reftok_list[reftok_idx]
    window = 5

    ### Extract the stem feature
    my_str = reftok.getText()
    stemmer = SnowballStemmer("english")
    my_stem = stemmer.stem(reftok.getText().lower())
    if (my_stem in feature_dict.keys()):
        feature_dict[my_stem] = '1'

    ### identify the numeric feature
    before = max(reftok_idx - 1, 0)
    after = min(reftok_idx + 1, len(reftok_list) - 1)

    if (before != reftok_idx and isinstance(getNumberFromText(reftok_list[before].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    elif (after != reftok_idx and isinstance(getNumberFromText(reftok_list[after].getText()), (int))):
        feature_dict['feat_numeric'] = '1'
    else:
        feature_dict['feat_numeric'] = '0'

    ## identify bow feature
    start = max(reftok_idx - window, 0)
    end = min(reftok_idx + (window + 1), len(reftok_list) - 1)

    for r in range(start, end):
        if r != reftok_idx:
            num_check = getNumberFromText(reftok_list[r].getText())
            if (isinstance(num_check, (int))):
                if (num_check in feature_dict.keys()):
                    feature_dict[num_check] = '1'
            else:
                txt = reftok_list[r].getText()
                if (txt in feature_dict.keys()):
                    feature_dict[txt] = '1'

    ## identify temp_self feature
    if reftok.isTemporal():
        feature_dict['feat_temp_self'] = '1'

    ## identify temp_context within 3 words to either side of the target.
    start = max(reftok_idx - window, 0)
    end = min(reftok_idx + (window + 1), len(reftok_list) - 1)
    for r in range(start, end):
        if r != reftok_idx:
            if reftok_list[r].isTemporal():
                feature_dict['feat_temp_context'] = '1'
                break

    return (feature_dict)


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

    dic = OrderedDict(zip(dict_keys, list(np.repeat('0', len(dict_keys)))))

    return (dic)


######
## END Function
######

## Marks all the reference tokens that are identified as notable.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
def markNotable(refToks):
    refToks = markDose(refToks)
    refToks = markFrequency(refToks)
    for ref in refToks:
        ref.setNumeric(numericTest(ref.getText(), ref.getPos()))
        boole, tID = temporalTest(ref.getText())
        ref.setTemporal(boole)
        ref.setTemporalType(tID)
    return refToks


## Marks reference tokens that are Frequency-related
#  @author Grant Matteo
# @param refToks The list of reference tokens
# @return modified list of reftoks

def markFrequency(refToks):
    for ref in refToks:
        ref.setNumericRange(isNumericRange(ref.getText()))
        ref.setAcronym(isAcronym(ref.getText()))
        ref.setQInterval(isQStatement(ref.getText()))
        ref.setFreqModifier(isFreqModifier(ref.getText()))
        ref.setFreqTransition(isFreqTransition(ref.getText()))
    return refToks


## Marks reference tokens that are dose-related (i.e., dose, dose units, conjunctions)
# @author Neha Dil
# @param refToks The list of reference tokens
# @return modified list of reftoks

def markDose(refToks):
    i = 0
    # Some tokens can be part of a dose phrase regardless of whether it on its own is a dose unit
    # I use a flag to indicate whether the current token should be included as a dose unit
    flag = False  # indicates whether this word should counted as a dose unit regardless of its test results

    while i < len(refToks):
        if "diss" in refToks[i].getText() or "suspend" in refToks[i].getText() or "containing" in refToks[
            i].getText():  # don't include solvents or solutes
            opt1 = re.compile(r'\.$')
            while (i < len(refToks) and "isomer" not in refToks[i].getText() and opt1.match(
                    refToks[i].getText()) != None):
                i = i + 1

        if (i >= len(refToks)): break
        if refToks[i].getText() == "and" or refToks[i].getText() == "or":
            refToks[i].setConjunction(True)  # mark up conjunctions
        if flag == True:  # means current token should be marked as dose unit
            refToks[i].setDoseUnit(True)
            refToks[i].setCombdose(False)
            refToks[i].setNumeric(numericTest(refToks[i].getText(), refToks[i].getPos()))
            flag = False
        else:  # test if token is dose-related
            temp, flag = unitTest(refToks[i].getText())
            refToks[i].setDoseUnit(temp)
            if flag != True:
                temp2, flag = combdoseTest(refToks[i].getText())
                if temp == True:
                    temp2 = False
            else:
                temp2, fill = combdoseTest(refToks[i].getText())
            refToks[i].setCombdose(temp2)
            refToks[i].setNumeric(numericTest(refToks[i].getText(), refToks[i].getPos()))
        i = i + 1

    return refToks


def isQStatement(tok):
    tok = re.sub('[' + string.punctuation + ']', '', tok).strip()
    tok = tok.lower();
    return re.search('q\d{1,2}(h|hr|hrs)?', tok) is not None


## Marks all the reference tokens that are identified as temporal.
# @author Amy Olex
# @param refToks The list of reference Tokens
# @return modified list of reftoks
def isAcronym(tok):
    acronyms = ["hs", "qhs", "bid", "qid", "qod", "tid", "prn", "qam", "qpm", "q", "asdir", "qd", "qmonth"];
    tok = re.sub('[' + string.punctuation + ']', ' ', tok).strip()
    tok = tok.lower();
    subtoks = tok.split()  # check if it exists anywhere in the string EX: DAILY:PRN
    intersect = [value for value in acronyms if value in subtoks]
    tok = re.sub(' ', '', tok)
    return (len(intersect) > 0) or tok in acronyms


def isFreqModifier(tok):
    modifiers = ["once", "twice", "each", "every", "daily", "nightly", "at", "as", "ongoing", "needed", "wmeals", "with", "w"
                 "meals"]
    tok = re.sub('[' + string.punctuation + ']', '', tok).strip()
    tok = tok.lower()
    return tok in modifiers


##These should only show up in the middle of a Frequency phrase, otherwise, something is wrong.
def isFreqTransition(tok):
    modifiers = ["if", "times", "time", "per", "a", "and"]
    tok = re.sub('[' + string.punctuation + ']', '', tok).strip()
    tok = tok.lower()
    return tok in modifiers


####
# END_MODULE
####

## Tests to see if token contains both dose and dose unit and if the next token should be counted as a part of the unit phrase
# @author Neha Dil
# @param tok The token string
# @returnBoolean True if token contains both dose and dose unit, False if not, followed by Boolean True if next token is part of the unit phrase, False if not


def combdoseTest(tok):  # may have to fix later
    token = re.sub(r'[!"\#$&()*+,\-.:;\'<=>?@\[\\\]^_`{|}~]', '', tok)

    units = ["μl",
             "μtrms",
             "mtrms",
             "µTrms",
             "g",
             "μw",
             "NP",
             "μg",
             "bpa"
             "kg",
             "bw",
             "ml",
             # "μg/105 cells",
             # "μg/25 μL",
             # "μg/gland",
             "kg",
             "µg",
             "µt",
             "mt",
             "pfus",
             # "particles/cm3",
             "m",
             "ml",
             "fu",
             "y",
             "mg",
             "mcg",
             "l",
             "μm",
             "mg",
             "kgbw•d",
             "kgbw",
             "u",
             "ml",
             "ac",
             "fus",
             "lm",
             "db",
             "spl",
             "ddt",
             "m3",
             "kpa",
             "trms",
             "ng",
             "μg",
             "np",
             "bwt",
             "l",
             "moi",
             "CFU",
             "Bq",
             "Gy",
             "μL",
             "μM",
             "ppm",
             "ppb",
             "µg",
             "pfus",
             "pfu",
             "pb",
             "μg"
             "ng",
             "wlm"]

    pattern = re.compile('^\d+')
    try:
        token = re.sub(r'^\d+', "", token)
        if "/" in token:
            temp = re.sub(r'[0-9]', '', token)
            words = temp.split("/")
            for word in words:
                for unit in units:
                    if word == unit and words[len(words) - 1] == "":
                        return True, True

                    elif word == unit:
                        return True, False
        else:
            for unit in units:
                if token == unit:
                    return True, False
        return False, False
    except:
        return False, False


## Tests to see if the token is a number.
# @author Amy Olex
# @param tok The token string
# @return Boolean true if numeric, false otherwise
def numericTest(tok, pos):

    if re.search("\d:[0-5]\d", tok) is not None:
        return False
    # Times are not numeric
    if "[" in tok.lower() and "]" in tok.lower():
        return False
    tok = tok.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()
    tok = re.sub("–", "", tok)
    tok = re.sub(" ", "", tok)
    if pos == "CD" and not isOrdinal(tok):
        return True
    else:
        # remove punctuation

        # test for a number
        # tok.strip(",.")
        val = getNumberFromText(tok)
        if val is not None:
            return True
        return False


####
# END_MODULE
####

##Tests to see if a value is a range of numbers, to be treated like a number
# @author Grant Matteo
# @param tok the token string
# @return True if a range, False otherwise
def isNumericRange(tok):
    tok = tok.translate(str.maketrans(string.punctuation.replace('-', ''), ' ' * (len(string.punctuation) - 1))).strip()
    return (re.search('\d{1,2}\-\d{1,2}', tok) is not None and re.search('\d{1,2}\-\d{1,2}\-\d', tok) is None)


## Tests to see if the token is a temporal value.
# @author Amy Olex
# @param tok The token string
# @return (Boolean true if temporal), (number indicating which temporal type was found)

def temporalTest(tok):
    # remove punctuation

    # if the token has a dollar sign or percent sign it is not temporal
    m = re.search('[#$%]', tok)
    if m is not None:
        return False, -1
    # look for date patterns mm[/-]dd[/-]yyyy, mm[/-]dd[/-]yy, yyyy[/-]mm[/-]dd, yy[/-]mm[/-]dd
    # m = re.search('([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', tok)
    # if m is not None:
    #    return True, 12
    # looks for a string of 8 digits that could possibly be a date in the format 19980304 or 03041998 or 980304
    # m = re.search('([0-9]{4,8})', tok)
    # if m is not None:
    # if tt.has24HourTime(m.group(0)):
    #    return True, 0
    # if tt.hasDateOrTime(m.group(0)):
    #    return True, 12
    ### NOT USEFUL FOR FREQUENCY ###

    # look for time patterns hh:mm:ss
    # m = re.search('([0-9]{2}:[0-9]{2}:[0-9]{2})', tok)
    # if m is not None:
    #    return True, 1
    # if tt.hasTextMonth(tok):
    # return True, 2
    ## THIS RETURNS TRUE FOR STRINGS SUCH AS "DOCTOR" BECAUSE it contains "OCT"
    if tt.hasDayOfWeek(tok):
        return True, 3
    if tt.hasPeriodInterval(tok):
        return True, 4
    if tt.hasAMPM(tok):
        return True, 5
    #if tt.hasPartOfWeek(tok):
    #    return True, 6
    # if tt.hasSeasonOfYear(tok):
    #    return True, 7
    if tt.hasPartOfDay(tok):
        return True, 8
    #if tt.hasTimeZone(tok):
    #    return True, 9
    # if tt.hasTempText(tok):
    #    return True, 10
    # not useful to us
    if tt.hasDoseDuration(tok):
        return True, -1
    # if tt.hasFor(tok):     I'm not sure if I'm going to use this or not yet
    #   return True, -1
    else:
        return False, -1


## Tests to see if token is a unit and if the next token is a part of the unit phrase
# @author Neha Dil
# @param tok The token string
# @return Boolean True if token is unit, False if not, followed by Boolean True if next token is part of the unit phrase, False if not
def unitTest(tok):
    tok = re.sub(r'[!"\#$&()*+,\-.:;\'<=>?@\[\\\]^_`{|}~]', '', tok)  # removes all punctuation except for "/"
    tok = tok.lower()
    units = ["μl",  # list of possible units
             "μtrms",
             "mtrms",
             "g",
             "μw",
             "mcg",
             "μg",
             "CFU",
             "bpa"
             "kg",
             "bw",
             "ml",
             # "μg/105 cells",
             # "μg/25 μL",
             # "μg/gland",
             "kg",
             "µg",
             "µt",
             "mt",
             "pfus",
             "NP",
             # "particles/cm3",
             "m",
             "ml",
             "fu",
             "y",
             "mg",
             "l"
             "μm",
             "mg",
             "kgbw•d",
             "kgbw",
             "u",
             "ml",
             "ac",
             "fus",
             "μM",
             "μm",
             "μg",
             "lm",
             "db",
             "spl",
             "ddt",
             "m3",
             "kpa",
             "trms",
             "ng"
             "np",
             "bwt",
             "μL",
             "l",
             "Bq",
             "Gy",
             "moi",
             "ppm",
             "ppb",
             "µg",
             "pfus",
             "pfu",
             "pb",
             "μg"
             "ng",
             "wlm"]
    # print(set("µg") & set(tok))
    if "/" in tok and not re.match(r"^\d", tok):  # if there's a '/' in the unit, evaluate each piece individually
        temp = re.sub(r'[0-9]', '', tok)  # remove numbers
        words = temp.split("/")
        for word in words:  # if one piece is a unit, the whole token is a unit
            for unit in units:
                if word == unit and words[
                    len(words) - 1] == "":  # if the last piece is empty, that means it was a number
                    return True, True  # if the last piece was a number, then the next token should be a part of the unit phrase
                elif word == unit:
                    return True, False
    else:  # if there's no "/" in the token, treat the token as a single piece
        for unit in units:
            if tok == unit:
                return True, False
    return False, False


####
# END_MODULE
####

## Extract dose phrases
# @author Neha Dil
# @param chroList List of marked reference tokens
# @return List of dose duration phrases
def getDoseDurationPhrases(chroList):
    id_counter = 0

    phrases = []  # the empty phrases list of TimePhrase entities
    tmpPhrase = []  # the temporary phrases list.
    inPhrase = False
    for n in range(0, len(chroList)):
        if chroList[n].isTemporal():
            if not inPhrase:
                inPhrase = True
            # in phrase, so add new element
            tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList) - 1:

                if inPhrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inPhrase = False
            else:
                s1, e1 = chroList[n].getSpan()
                s2, e2 = chroList[n + 1].getSpan()

                if e1 + 1 != s2 and inPhrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inPhrase = False


        elif chroList[n].isNumeric():
            # if the token has a dollar sign or percent sign do not count it as temporal
            m = re.search('[#$%]', chroList[n].getText())
            if m is None:
                # check for the "million" text phrase
                answer = next((m for m in ["million", "billion", "trillion"] if m in chroList[n].getText().lower()),
                              None)
                if answer is None:
                    # print("No million/billion/trillion: " + str(chroList[n]))
                    if not inPhrase:
                        inPhrase = True
                    # in phrase, so add new element
                    tmpPhrase.append(copy.copy(chroList[n]))
            # test to see if a new line is present.  If it is AND we are in a temporal phrase, end the phrase and start a new one.
            # if this is the last token of the file, end the phrase.
            if n == len(chroList) - 1:

                if inPhrase:
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inPhrase = False
            else:
                s1, e1 = chroList[n].getSpan()
                s2, e2 = chroList[n + 1].getSpan()
                if e1 + 1 != s2 and inPhrase:
                    # print("has new line: " + str(chroList[n]))
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter = id_counter + 1
                    tmpPhrase = []
                    inPhrase = False

        else:
            if inPhrase:
                inPhrase = False
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


## Takes in a Reference List that has had numeric and Frequency tokens marked, and identifies all the
## temporal phrases by finding consecutive temporal tokens.
# @author Amy Olex
# @param chroList The list of temporally marked reference tokens
# @return A list of temporal phrases for parsing
def getFrequencyPhrases(chroList, text):
    id_counter = 0
    text = re.sub("\r", "", text)
    phrases = []  # the empty phrases list of TimePhrase entities
    tmpPhrase = []  # the temporary phrases list.
    inPhrase = False

    for n in range(0, len(chroList)):
        start, end = chroList[n].getSpan()
        normalizedTxt = chroList[n].getText().lower().translate(
            str.maketrans(string.punctuation, ' ' * len(string.punctuation))).strip()
        if chroList[n].isFreqComp() or (chroList[n].isFreqTransition() and inPhrase):
            inPhrase = True
            tmpPhrase.append(chroList[n])
            if n == len(chroList) - 1:
                tmpPhrase = trimExcess(tmpPhrase)
                if isValidFreqPhrase(tmpPhrase):
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter += 1
                tmpPhrase = []
                inPhrase = False
        elif inPhrase:
            if (n < len(chroList) - 1 and chroList[n - 1].isNumeric() and chroList[
                n + 1].isNumeric() and normalizedTxt == "to"):  # check for ranges of numbers like "one to three"
                tmpPhrase.append(chroList[n])
            else:
                inPhrase = False
                tmpPhrase = trimExcess(tmpPhrase)
                if isValidFreqPhrase(tmpPhrase):
                    phrases.append(createTPEntity(tmpPhrase, id_counter))
                    id_counter += 1
                tmpPhrase = []
    return phrases


## Takes in a list of reference tokens and returns the list with any excess from the end removed
# @author Grant Matteo
# @param items The list of reference tokens
def trimExcess(items):
    deb = False
    # if ("Q" in [item.getText() for item in items]):
    #    deb=True
    #    print("trim: ", [item.getText() for item in items])
    n = 0
    nonQillegals = ["days", "month", "months", "weeks"]  # none of these can be a word in a phrase, unless proceeded by a q
    illegalPartials = ["date"]  # none of these can exist in the string at all
    while n < len(items):  # get rid of all illegal strings (Strings that are never used, but useful for DoseDuration)
        normalizedTextUpper = re.sub('[' + string.punctuation + ']', '', items[n].getText()).strip()
        normalizedText=normalizedTextUpper.lower()
        hasIllegalParts = False
        hasIllegalParts = [True for partial in illegalPartials if
                           re.search(partial, normalizedText)]  # if any of them match
        hasIllegalParts= hasIllegalParts or normalizedTextUpper=="HR" #HR means HeartRate
        if normalizedText in nonQillegals:
            if (n == 0 or re.sub('[' + string.punctuation + ']', '', items[n - 1].getText()).lower().strip() != "q"):
                if n < len(items) / 2:  # get rid of the part before/after the illegal word, whichever is smaller.
                    items = items[n + 1:len(items) - 1]
                else:
                    items = items[0:n - 1]
        elif hasIllegalParts:
            if n < len(items) / 2:  # get rid of the part before/after the illegal word, whichever is smaller.
                items = items[n + 1:len(items) - 1]
            else:
                items = items[0:n - 1]
        n += 1
    while len(items) > 0 and (items[len(items) - 1].isFreqTransition() or items[len(items) - 1].isNumericOnly() or \
                              items[len(items) - 1].getPos() == "IN" or items[len(items) - 1].getPos() == "TO"):
        items.pop()  # removing trailing numbers or transitions

    firstNonNum = 0
    while (firstNonNum < len(items) - 1) and (items[firstNonNum].isNumeric()):
        firstNonNum += 1
    while len(items) > 1 and items[0].isNumeric() and (
            items[firstNonNum].isQInterval() or items[firstNonNum].isFreqModifier()):
        items.pop(0)
        firstNonNum -= 1;
    asFollowers = ["needed", "directed"]
    # AS should always be followed by "needed" or "directed", and needed and directed should always be preceded by "as"
    foundAs = False
    n = 0
    while (n < len(items)):
        normalizedText = re.sub('[' + string.punctuation + ']', '', items[n].getText()).lower().strip()
        if (normalizedText == "as"):
            foundAs = True
            if (n == len(items) - 1):
                items.pop(n)
        elif (normalizedText in asFollowers and not foundAs):
            items.pop(n)
            foundAs = False
        elif (foundAs and normalizedText not in asFollowers):
            items.pop(n)
            foundAs = False
        else:
            foundAs = False
        n += 1
    # if (deb):
    #    print("post: ", [item.getText() for item in items])
    return items


## Checks if there is a number in the phrase
# @author Neha Dil
# @param tmpPhrase List of the reference tokens in a phrase
# @return True if there is a number; otherwise, False
def containsNumericToken(tmpPhrase):
    for tok in tmpPhrase:
        if tok.isNumeric():
            return True

    return False


## Checks if there is a duration word in the phrase
# @author Neha Dil
# @param tmpPhrase List of the reference tokens in a phrase
# @return True if there is a duration word; otherwise, False
def containsDurationToken(tmpPhrase):
    terms = ["day", "week", "minute", "second", "hour",
             "days", "weeks", "months", "minutes", "seconds", "hours", "hr", "hrs", "min", "mins"]
    for tok in tmpPhrase:

        print("tok:", tok.getText())
        if tok.getText().lower() in terms:
            return True
    return False


## Takes in a list of reference tokens and returns true if it contains something that can be considered a valid Frequency on its own
# @author Grant Matteo
# @param items The list of reference tokens
def isValidFreqPhrase(items):
    # if ("Once" in [item.getText() for item in items]):
    #    print("valid?: ",[item.getText() for item in items])
    if len(items) > 1:
        fullText = "".join([item.getText() for item in items])
        return (re.search("\%", fullText) is None)
    else:
        for item in items:
            if item.isQInterval() or item.isAcronym():
                return True

        texts = [re.sub("[" + string.punctuation + "]", "", item.getText().lower().strip()) for item in items]

        text_norm = "".join(texts).strip()

        singulars = ["daily", "nightly", "tuthsa", "mowefr", "qmowefr", "qtuthsa", "bedtime",
                     "qmonth", "qday", "once", "ongoing", "noon"]
        # find if the texts has any singulars in it
        return text_norm in singulars or re.search("\d+xweek", text_norm) #check for 4xweek, etc


## Extract dose phrases (strength phrases in N2C2) from the marked list of reference tokens
# @author Neha Dil
# @param chroList The marked list of reference tokens
# @return phrases List of the dose phrases
def getDosePhrases(chroList):
    # TimePhraseEntity(id=id_counter, text=j['text'], start_span=j['start'], end_span=j['end'], temptype=j['type'], tempvalue=j['value']=doctime)

    phrases = []  # the empty phrases list of TimePhrase entities
    dosePhrase = []  # the temporary phrases list.
    counter = 1
    for n in range(0, len(chroList)):
        if (chroList[n].isCombdose()):
            if (len(dosePhrase) >= 1 and (
                    dosePhrase[len(dosePhrase) - 1].isDoseunit() or dosePhrase[len(dosePhrase) - 1].isCombdose())):
                phrases.append(createDPEntity(dosePhrase, counter))
                counter = counter + 1
                dosePhrase = []
            dosePhrase.append(copy.copy(chroList[n]))
        elif (chroList[n].isNumeric()):
            if (len(dosePhrase) >= 1 and (
                    dosePhrase[len(dosePhrase) - 1].isDoseunit() or dosePhrase[len(dosePhrase) - 1].isCombdose())):
                phrases.append(createDPEntity(dosePhrase, counter))
                counter = counter + 1
                dosePhrase = []

            dosePhrase.append(copy.copy(chroList[n]))
        elif (chroList[n].isDoseunit()):
            if (len(dosePhrase) > 0):
                dosePhrase.append(copy.copy(chroList[n]))
        elif (chroList[n].isConjunction() and len(dosePhrase) > 0):
            if (len(dosePhrase) >= 1 and (
                    dosePhrase[len(dosePhrase) - 1].isDoseunit() or dosePhrase[len(dosePhrase) - 1].isCombdose())):
                phrases.append(createDPEntity(dosePhrase, counter))
                counter = counter + 1
            dosePhrase.append(copy.copy(chroList[n]))
        else:
            if (len(dosePhrase) >= 1 and (
                    dosePhrase[len(dosePhrase) - 1].isDoseunit() or dosePhrase[len(dosePhrase) - 1].isCombdose())):
                phrases.append(createDPEntity(dosePhrase, counter))
                counter = counter + 1
            dosePhrase = []
    if (len(dosePhrase) >= 1):
        if dosePhrase[len(dosePhrase) - 1].isDoseunit() or dosePhrase[len(dosePhrase) - 1].isCombdose():
            phrases.append(createDPEntity(dosePhrase, counter))

    return phrases


####
# END_MODULE
####


## Takes in a list of reference tokens identified as a temporal phrase and returns one TimePhraseEntity.
# @author Amy Olex
# @param items The list of reference tokesn
# @param counter The ID this TimePhrase entity should have
# @param doctime The document time.
# @return A single TimePhrase entity with the text span and string concatenated.
def createTPEntity(items, counter):
    start_span, tmp = items[0].getSpan()
    tmp, end_span = items[len(items) - 1].getSpan()
    text = ""
    for i in items:
        text = text + ' ' + i.getText()

    return tp.LabelPhraseEntity(id=counter, text=text.strip(), start_span=start_span, end_span=end_span, temptype=None,
                                tempvalue=None, items=items)


## Takes in the list of reference tokens identified as a dose/strength phrase and returns one DosePhraseEntity
# @author Neha Dil
# @param items The list of reference tokens
# @param counter The ID for this DosePhrase entity
# @return A single DosePhrase entity with the text span and string concatenated.
def createDPEntity(items, counter):
    start_span, tmp = items[0].getSpan()
    tmp, end_span = items[len(items) - 1].getSpan()
    allspans = []
    text = ""
    for i in items:
        allspans.append(i.getSpan())
        if (len(text) > 0 and text[len(text) - 1] != "/"):
            text += ' '
        text += i.getText()

    return dp.DosePhraseEntity(id=counter, text=text.strip(), start_span=start_span, end_span=end_span, temptype=None,
                               tempvalue=None, allspans=allspans)


####
# END_MODULE
####


## Takes in a reference list of tokens, a start span and an end span
# @author Amy Olex
# @param ref_list The list of reference tokens we want an index for.
# @param start_span The start span of the token we need to find in ref_list
# @param end_span The ending span of the token we need to find
# @return Returns the index of the ref_list token that overlaps the start and end spans provided, or -1 if not found.
def getRefIdx(ref_list, start_span, end_span):
    for i in range(0, len(ref_list)):
        if (overlap(ref_list[i].getSpan(), (start_span, end_span))):
            return i
    return -1


####
# END_MODULE
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