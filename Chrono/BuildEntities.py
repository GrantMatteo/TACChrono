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

def buildChronoList(TimePhraseList, chrono_id, ref_list, PIClassifier, PIStuff):
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


        # tmplist, chrono_id = buildSubIntervals(chrono_tmp_list, chrono_id, dct, ref_list)
        chrono_list = chrono_list+chrono_tmp_list
        chrono_tmp_list=[]

      
    return chrono_list, chrono_id
    
####
#END_MODULE
####
def buildFrequency(s, chrono_id, chrono_tmp_list, ref_list):
    flag= hasFrequency(s)
    flag=True
    if (flag):
        chrono_tmp_list.append(chrono.ChronoFrequencyEntity(id=str(chrono_id) + "entity", label="Frequency",span=s.getSpan(), text=s.getText()))
    chrono_id+=1
    return chrono_tmp_list, chrono_id
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
        "q <n> <timeunit>": [isIn, isNumericOnly, temporalTypeCheck],
        "q <timeunit>": [isIn, temporalTypeCheck],
        "every other <timeunit>": [isIn, isIn, temporalTypeCheck]
    }

    #"morning","breakfast","lunch", "dinner", "evening","afternoon","night","nights",
    # "mornings","evenings","afternoons","noon","bedtime", "meals"]
    # hasDayOfWeek(tok):3
    # hasPeriodInterval(tok): 4
    # hasAMPM(tok): 5
    # hasPartOfDay(tok): 8

    # used when functions need additional input, EG: isIn() needs a list of Strings
    dict_of_funct_inputs = {
        "<once-twice> <a-per-etc> <timeunit>": [["once", "twice"], ["a", "per", "each", "every"], [4]],
        "<n> times <a-per-etc> <timeunit>": [[], ["times"], ["a", "per", "each", "every"], [4]],
        "every <n> <timeunit>": [["every"], [], [4]],
        "as <needed, directed>": [["as"], ["needed", "directed"]],
        "at <time of day>": [["at"], [4]],
        "at <hour>": [["at"], []],
        "at <n> <AM-PM>": [["at"], [], [5]],
        "q <n> <timeunit>": [["q"], [], [4]],
        "q <timeunit>": [["q"], [4]],
        "every other <timeunit>": [["every"], ["other"], [4]]

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
                    if (key == ""):
                        print("SUCCESS!", s.getText())
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
def hasSingular(refToks):
    for item in refToks:
        if item.isQInterval() or item.isAcronym():
            return True

    texts = [re.sub("[" + string.punctuation + "]", "", item.getText().lower().strip()) for item in refToks]

    text_norm = "".join(texts).strip()

    singulars = ["daily", "nightly", "tuthsa", "mowefr", "qmowefr", "qtuthsa", "bedtime",
                 "qmonth", "qday", "once", "ongoing", "noon"]    # find if the texts has any singulars in it
    return text_norm in singulars or re.search("\d+xweek", text_norm)  # check for 4xweek, etc
        ##END OF FUNCTIONS TO BE USED IN PATTERN RECOGNITION##