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



## Converts temporal phrases into Chrono Entities


from Chrono.TimePhraseToChrono import *
from Chrono import referenceToken
from Chrono import chronoEntities as chrono
from Chrono import utils
import re
from chronoML import FrequencyRNN as rnn
import string

#Example TimePhrase List
#Wsj_0152
#0 11/02/89 <12,20> DATE 1989-11-02
#1 Nov. 9 11/02/89 <145,160> DATE 1989-11-02
#2 5 p.m. EST Nov. 9 <393,410> TIME 2017-11-09T17:00-0500
#3 Nov. 6 <536,542> DATE 2017-11-06

## Takes in list of TimePhrase output and converts to ChronoEntity
# @author Nicholas Morton
# @param list of TimePhrase Output
# @param document creation time (optional)
# @return List of Chrono entities and the ChronoID
from Chrono.TimePhraseToChrono import DoseDuration

def buildChronoList(TimePhraseList, chrono_id, ref_list):
    chrono_list = []

    ## Do some further pre-processing on the ref token list
    ## Replace all punctuation with spaces
    ref_list = referenceToken.replacePunctuation(ref_list)
    ## Convert to lowercase
    ref_list = referenceToken.lowercase(ref_list)
    for s in TimePhraseList:
        chrono_tmp_list = []
        # this is the new chrono time flags so we don't duplicate effort.  Will ned to eventually re-write this flow.
        # The flags are in the order: [loneDigitYear, month, day, hour, minute, second]




        #chrono_tmp_list, chrono_id = DoseDuration.buildDoseDuration(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
        chrono_tmp_list, chrono_id = buildFrequency(s, chrono_id, chrono_tmp_list, ref_list)
        chrono_list = chrono_list+chrono_tmp_list
        chrono_tmp_list=[]
        # tmplist, chrono_id = buildSubIntervals(chrono_tmp_list, chrono_id, dct, ref_list)


    return chrono_list, chrono_id

def buildChronoListML(TimePhraseList, chrono_id, ref_list, X, classifier):
    chrono_list = []

    ## Do some further pre-processing on the ref token list
    ## Replace all punctuation with spaces
    ref_list = referenceToken.replacePunctuation(ref_list)
    ## Convert to lowercase
    ref_list = referenceToken.lowercase(ref_list)
    n=0
    while n <len(TimePhraseList):
        s=TimePhraseList[n]
        if (hasSingular(s.getItems())):
            chrono_list.append(chrono.ChronoFrequencyEntity(id=str(chrono_id) + "entity", label="Frequency", span=s.getSpan(),
                                             text=s.getText()))
            chrono_id+=1
            TimePhraseList.pop(n)
            n-=1
        n+=1
    if len(TimePhraseList)!=len(X):
        print("FATAL ERROR: LEN(PHRASE FEATURES)!=LEN(PHRASES)")
        exit(1)
    for s, x in zip(TimePhraseList, X):
        chrono_tmp_list = []
        # this is the new chrono time flags so we don't duplicate effort.  Will ned to eventually re-write this flow.
        # The flags are in the order: [loneDigitYear, month, day, hour, minute, second]



        #chrono_tmp_list, chrono_id = DoseDuration.buildDoseDuration(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
        chrono_tmp_list, chrono_id = buildFrequencyML(s, chrono_id, chrono_tmp_list, x, classifier)
        chrono_list = chrono_list+chrono_tmp_list
        chrono_tmp_list=[]
        # tmplist, chrono_id = buildSubIntervals(chrono_tmp_list, chrono_id, dct, ref_list)
    return chrono_list, chrono_id



def getMLFeats(TimePhraseList, currentFile=None):
    frequencySpans = []
    freqPhrases= []
    if currentFile is not None:
        with open(currentFile, "r") as annFile:
            anns = annFile.readlines()
        for ann in anns:
            if "Frequency" in ann:
                while re.search("\d+;\d+", ann) is not None:
                    ann = re.sub(" \d+;\d+ ", " ", ann)
                match = re.search("^T\d+\tFrequency (?P<start>\d+)\ (?P<end>\d+)(?P<phrase>.*)", ann)
                if match is not None:
                    frequencySpans.append([match.group('start'), match.group('end')])
                    freqPhrases.append(match.group('phrase'))

    nnXList = []  # a 3d vector of features for all phrases
    nnYList = []
    deb = open("/home/garnt/Documents/MLCheckingGenned.out", "a")
    deb2 = open("/home/garnt/Documents/MLCheckingGold.out", "a")
    matches=0
    for span, phrase in zip(frequencySpans, freqPhrases):
        goldStart = int(span[0])
        goldEnd = int(span[1])
        deb2.write("\nGold Start: " + str(goldStart) + "\nGoldEnd " + str(goldEnd) + "\n"+phrase)
    deb2.write("\n"+currentFile)
    deb2.close()
    for s in TimePhraseList:
        # this is the new chrono time flags so we don't duplicate effort.  Will ned to eventually re-write this flow.
        # The flags are in the order: [loneDigitYear, month, day, hour, minute, second]

        # chrono_tmp_list, chrono_id = DoseDuration.buildDoseDuration(s, chrono_id, chrono_tmp_list, ref_list, PIclassifier, PIfeatures)
        nnPhrase = getNN(s)

        if hasSingular(s.getItems()):
            continue
        gennedStart = s.getSpan()[0]
        gennedEnd = s.getSpan()[1]
        deb.write("\nGenned Start: " + str(gennedStart) + "\nGennedEnd " + str(gennedEnd)+ "\n"+s.getText())

        isReal = False
        for span, phrase in zip(frequencySpans, freqPhrases):
            goldStart = int(span[0])
            goldEnd = int(span[1])
            if (gennedStart < goldStart and gennedEnd > goldEnd) or (abs(gennedStart - goldStart) < 6 and abs(gennedEnd - goldEnd) < 6):
                isReal = True
                matches+=1
        deb.write("\nMATCHED: " + str(isReal))
        nnYList.append(isReal)
        nnXList.append(nnPhrase)
        # tmplist, chrono_id = buildSubIntervals(chrono_tmp_list, chrono_id, dct, ref_list)
        chrono_tmp_list = []
    if currentFile is not None:
        deb.write("\n"+currentFile+" "+str(matches))
        deb.close()
        return nnYList, nnXList
    else:
        return None, nnXList

####
#END_MODULE
####
def buildFrequency(s, chrono_id, chrono_tmp_list, ref_list):
    flag= hasFrequency(s)
    #print([chroE.getText() for chroE in s.getItems()])
    #flag=True

    if (flag):
        chrono_tmp_list.append(chrono.ChronoFrequencyEntity(id=str(chrono_id) + "entity", label="Frequency",span=s.getSpan(), text=s.getText()))
    chrono_id+=1
    return chrono_tmp_list, chrono_id
def buildFrequencyML(s, chrono_id, chrono_tmp_list, x, classifier):
    flag= rnn.classify(classifier, x) or hasSingular(s.getItems())
    #print(flag, "  TEXT: ", s.getText())
    if (flag):
        chrono_tmp_list.append(chrono.ChronoFrequencyEntity(id=str(chrono_id) + "entity", label="Frequency",span=s.getSpan(), text=s.getText()))
        chrono_id+=1
    chrono_id+=1
    return chrono_tmp_list, chrono_id
def getNN(s):
    thisPhrase=[]
    for refTok in s.getItems():
        thisPhrase.append([
            isIn(refTok, "once", "twice"),
            isIn(refTok, "a","per", "each", "every"),
            isIn(refTok, "times"),
            isIn(refTok, "as"),
            isIn(refTok, "needed", "directed"),
            isIn(refTok, "at"),
            isIn(refTok, "q"),
            isIn(refTok, "other"),
            isIn(refTok, "with"),
            isIn(refTok, "meals","breakfast", "lunch", "dinner"),
            isIn(refTok, "weekly"),
            isIn(refTok, "only"),
            isIn(refTok, "if"),
            isIn(refTok, "necessary"),
            isIn(refTok, "period"),
            isIn(refTok, "on"),
            isNumericOnly(refTok),
            temporalTypeCheck(refTok, 4),
            temporalTypeCheck(refTok, 5),
            temporalTypeCheck(refTok, 8),
            timeTestStrong(refTok),
            timeTestWeak(refTok),
        ])
    return thisPhrase

##Checks for a variety of patterns using lists of functions; functions are organized in lists. If the chronoentities match any one of the patterns, it has Frequency.
# @author Grant Matteo
# @param s Time phrase to check
# @return True if matches any of the patterns, False otherwise
def hasFrequency(s):
    flag=False
    refToks=s.getItems()
    if (hasSingular(refToks)):
        return True

    #list of functions. The phrases must match
    dict_of_funct_lists = {
        "<once-twice> <a-per-etc> <timeunit>": [isIn, isIn, temporalTypeCheck],
        "<n> times <a-per-etc> <timeunit>": [isNumericOnly, isIn, isIn, temporalTypeCheck],
        "every <n> <timeunit>": [isIn, isNumericOnly, temporalTypeCheck],
        "as <needed, directed>": [isIn, isIn],
        "at <time of day>": [isIn, temporalTypeCheck],
        "at <hour>": [isIn, timeTestStrong],
        "at <n> <AM-PM>": [isIn, timeTestWeak, temporalTypeCheck],
        "q <n> (<timeunit>?)": [isIn, isNumericOnly],
        "q <timeunit>": [isIn, temporalTypeCheck],
        "every other <timeunit>": [isIn, isIn, temporalTypeCheck],
        "every <timeunit>": [isIn, temporalTypeCheck],
        "<n> times <daily-weekly>": [isNumericOnly, isIn, isIn],
        "with meals": [isIn, isIn],
        "<n> <a-per-each-every> <timeunit>": [isNumericOnly, isIn, temporalTypeCheck],
        "breakfast lunch dinner": [isIn, isIn, isIn],
        "only if necessary": [isIn, isIn],
        "<n> <timeunit> on": [isNumericOnly, isIn, isIn],
        "<n> <timeunit> period": [isNumericOnly, temporalTypeCheck, isIn]

    }


    # used when functions need additional input, EG: isIn() needs a list of Strings
    dict_of_funct_inputs = {
        "<once-twice> <a-per-etc> <timeunit>": [["once", "twice"], ["a", "per", "each", "every"], [4]],
        "<n> times <a-per-etc> <timeunit>": [[], ["times"], ["a", "per", "each", "every"], [4]],
        "every <n> <timeunit>": [["every"], [], [4]],
        "as <needed, directed>": [["as"], ["needed", "directed"]],
        "at <time of day>": [["at"], [4, 8]],
        "at <hour>": [["at"], []],
        "at <n> <AM-PM>": [["at"], [], [5]],
        "q <n> (<timeunit>?)": [["q"], []],
        "q <timeunit>": [["q"], [4,8]],
        "every other <timeunit>": [["every"], ["other"], [4,8]],
        "every <timeunit>": [["each", "every"], [4, 8]],
        "<n> times <daily-weekly>": [[], ["times"], ["daily", "weekly"]],
        "with meals": [["with"], ["meals"]],
        "<n> <a-per-each-every> <timeunit>": [[], ["a", "per", "each", "every"], [4]],
        "breakfast lunch dinner": [["breakfast"], ["lunch"], ["dinner"]],
        "only if necessary": [["if"], ["necessary"]],
        "<n> <timeunit> on": [[], ["day", "week", "month", "hour", "days", "weeks", "months","hours","hr", "hrs"], ["on"]],
        "<n> <timeunit> period": [[], [4], ["period"]]
    }


    # used to keep track of where in the pattern we are
    funct_iterators={key:0 for key in dict_of_funct_inputs}
    # for every reference token, iterate through the patterns, trying to find matches; if each method in a list in
    # dict_of_funct_lists returns true sequentially, the pattern matches!
    for refTok in refToks:
        for key, functList in dict_of_funct_lists.items():
            position=funct_iterators[key]#where we are in this pattern
            if (functList[position](refTok, *dict_of_funct_inputs[key][position])):
                funct_iterators[key]+=1 #we passed this one, so iterate the position of the match
                if funct_iterators[key]>=len(functList):

                    return True #if we have progressed to the end of a pattern, we did it!
            else:
                funct_iterators[key]=0

    return flag
         ##FUNCTIONS TO BE USED IN PATTERN RECOGNITION##
def isFreqComp(refTok):
    if refTok.doseunit or refTok.combdose:  # don't want to capture doseunits which may precede frequencies
        return False
    return refTok.temporal or \
           refTok.acronym or refTok.numericRange or refTok.numeric or refTok.freqModifier or refTok.qInterval
#returns true if refTok's text is in the list
def isIn(refTok, *list):
    text_norm=re.sub('[' + string.punctuation+']', "", refTok.getText().lower().strip())
    return text_norm in list
def temporalTypeCheck(refTok, *nums):
    return refTok.temporalType in nums
def timeTestStrong(refTok):
    result=re.search("^\d{1,2}\:\d{1,2}$", refTok.getText().strip())
    return result is not None
def timeTestWeak(refTok):
    result = re.search("^\d{1,2}\:\d{1,2}$", refTok.getText().strip())

    if result is None:
        result =re.search("^\d$", refTok.getText().strip())
    return result is not None
def isNumericOnly(refTok):
    return (refTok.numeric or refTok.numericRange) and not (refTok.temporal or \
                                                        refTok.acronym or refTok.freqModifier or refTok.qInterval)
def isFreqModifier(refTok):
    return refTok.freqModifier
def isFreqTransition(refTok):
    return refTok.frequencyTransition
def isQInterval(refTok):
    return refTok.qInterval
def isAcronym(refTok):
    return refTok.acronym
def isNumericRange(refTok):
    return refTok.numericRange
def isTemporal(refTok):
    return (refTok.temporal)
def isDoseunit(refTok):
    return (refTok.doseunit)
def isNumeric(refTok):
    return (refTok.numeric)
def isCombdose(refTok):
    return refTok.combdose
def hasSingular(refToks): #this defines things that, if the phrase contains, we can safely assume it is a Frequency
    for item in refToks:
        if item.isQInterval() or item.isAcronym():
            return True

    texts = [re.sub("[" + string.punctuation + "]", "", item.getText().lower().strip()) for item in refToks]

    text_norm = "".join(texts).strip()

    singulars = ["daily", "nightly", "tuthsa", "mowefr", "qmowefr", "qtuthsa", "bedtime",
                 "qmonth", "qday", "once", "ongoing", "noon", "generally", "week", "day", "wmeals", "q"]    # find if the texts has any singulars in it
    overlap = [text for text in texts if text in singulars] #if any chroEntity is in singulars
    return len(overlap)>0 or text_norm in singulars or re.search("\d+x(week|month|day)", text_norm) is not None # check for 4xweek, etc
        ##END OF FUNCTIONS TO BE USED IN PATTERN RECOGNITION##