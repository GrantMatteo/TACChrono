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



## Class definitions to represent a whitespace-parsed token in the raw text file.


import string

## Class to define a whitespace-parsed token from raw text.
# @author Amy Olex
# @param id Unique numerical ID
# @param text The text of the token
# @param start_span The location of the first character
# @param end_span The location of the last character
# @param pos The part of speech assigned to this token
# @param doseunit A boolean indicating if the token is a dose unit
# @param numeric A boolean indicating if the token is a numeric value
# @para
# @param temporal A boolean indicating if this token contains any temporal components
# @param numericRange A boolean indicating if this token is a numeric range (0-12)
# @param sent_boundary A boolean indicating if this token is at the end of a sentence or line
class refToken:
    ## The constructor
    def __init__(self, id, text, temporalType=-1, acronym=None,start_span=None, end_span=None,
                 pos=None, temporal=None , t6list=None, numeric=None,
                 conjunction=None, sent_boundary=None) :
        self.id = id
        self.frequencyTransition=False
        self.text = text
        self.start_span = start_span
        self.end_span = end_span
        self.pos = pos
        self.doseunit = None
        self.numeric = numeric
        self.t6list = t6list
        self.combdose = None
        self.temporal = temporal
        self.qInterval= False
        self.conjunction = conjunction
        self.sent_boundary = sent_boundary
        self.numericRange = False

        self.acronym= acronym
        self.freqModifier=False;
        self.temporalType=temporalType
    ## Defines how to convert a refToken to string
    def __str__(self) :
        #return str(self.id) + " " + self.text
        span_str = "" if self.start_span is None else (" <" + str(self.start_span) + "," + str(self.end_span) + "> ")
        pos_str = "" if self.pos is None else ("pos: " + self.pos)
        temp_str = "" if self.temporal is None else (" isTemp: " + str(self.temporal))
        num_str = "" if self.numeric is None else (" isNumeric: " + str(self.numeric))
        sentb_str = "" if self.sent_boundary is None else (" isEndSent: " + str(self.sent_boundary))
        #return str(self.id) + " " + self.text
        return str(self.id) + " " + self.text + span_str + pos_str  + temp_str + num_str + sentb_str

    #### Methods to SET properties ###
    
    ## Sets the entity's ID
    #  @param id The ID to set it to
    def setID(self, id) :
        self.id = id
    ## Sets whether the entity is a qInterval
    #  @param boole the boolean value (true if it is, false if it isn't)
    def setQInterval(self, boole):
        self.qInterval=boole
    ## Sets whether the entity is a frequencymodifier
    #  @param boole the boolean value (true if it is, false if it isn't)
    def setFreqModifier(self, boole):
        self.freqModifier=boole
    ## Sets whether or not the current refTok represents a numeric range (8-10), etc for Frequency checking
    #  @param b The boolean value to set NumericRange to
    def setNumericRange(self, b) :
        self.numericRange=b

    ## Sets whether or not the current refTok represents an acronym, etc for Frequency checking
    #  @param b The boolean value to set acronym to
    def setAcronym(self, b):
        self.acronym=b

    ## Sets the temporal type of this phrase
    #  @param n The int value to set temporalType to
    def setTemporalType(self, n):
        self.temporalType= n

    ## Sets whether this phrase is a Frequency Transition (to, each, every, etc)
    #  @param boole boolean for whether it is (true) or isnt (false)
    def setFreqTransition(self, boole):
        self.frequencyTransition=boole
    ## Sets the entity's text
    #  @param text The text to set it to
    def setText(self, text) :
        self.text = text
        
    ## Sets the entity's span
    #  @param start The start index
    #  @param end The ending index
    def setSpan(self, start, end) :
        self.start_span = start
        self.end_span = end
        
    ## Sets the entity's POS
    #  @param pos The part of speech assigned to the token
    def setPos(self, pos) :
        self.pos = pos

    def setConjunction(self, conjunction):
        self.conjunction = conjunction
        
    ## Sets the entity's temporal flag
    #  @param temp A boolean, 1 if it is a temporal token, 0 otherwise
    def setDoseUnit(self, doseunit) :
        self.doseunit = doseunit

    def setCombdose(self, combdose):
        self.combdose = combdose
    
    ## Sets the entity's numeric flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setNumeric(self, num) :
        self.numeric = num
    def setTemporal(self, temp):
        self.temporal = temp

    ## Adds to the entities list of T6 entities
    #  @param t6id an integer of the t6 entities ID
    def t6Append(self, t6id) :
        if self.t6list is None :
            self.t6list = []
            self.t6list.append(t6id)
        else :
            self.t6list.append(t6id)


    ## Sets the entity's sentence boundary flag
    #  @param temp A boolean, 1 if it is a numeric token, 0 otherwise
    def setSentBoundary(self, num) :
        self.sent_boundary = num
    #### Methods to GET properties ####
    def isFreqComp(self):
        if self.doseunit or self.combdose: #don't want to capture doseunits which may precede frequencies
            return False
        return self.temporal or\
               self.acronym or self.numericRange or self.numeric or self.freqModifier or self.qInterval
    ## Returns a string for Frequency debugging
    def getFreqDebug(self):
        return self.text + " " +str(self.frequencyTransition) + " " + str(self.temporal) +" "+ str(self.temporalType)+ " "+str(self.acronym) + " " +\
               str(self.numericRange) + " " + str(self.numeric) + " " + str(self.freqModifier) + " " + str(self.qInterval)+ " "+ "BAD: "+str(self.doseunit or self.combdose)+" " + str(self.pos) + " "+str(self.isNumericOnly())
    ## Useful for stripping away extraneous numeric words
    def isNumericOnly(self):
        return (self.numeric or self.numericRange) and not (self.temporal or \
               self.acronym or self.freqModifier or self.qInterval)
    def isFreqModifier(self):
        return self.freqModifier
    def isFreqTransition(self):
        return self.frequencyTransition
    def isQInterval(self):
        return self.qInterval
    def isAcronym(self):
        return self.acronym
    def getTemporalType(self):
        return self.temporalType
    def getID(self) :
        return(self.id)
    def isNumericRange(self):
        return self.numericRange
    ## Gets the entity's text
    def getText(self) :
        return(self.text)
        
    ## Gets the entity's span
    def getSpan(self) :
        return(self.start_span, self.end_span)
        
    ## Gets the entity's POS
    def getPos(self) :
        return(self.pos)
        
    ## Gets the entity's temporal flag
    def isTemporal(self) :
        return(self.temporal)

    def isDoseunit(self):
        return(self.doseunit)
        
    ## Gets the entity's numeric flag
    def isNumeric(self) :
        return(self.numeric)

    def isCombdose(self):
        return self.combdose

    def isConjunction(self):
        return self.conjunction

    ## Gets the entity's t6list
    def getSentBoundary(self) :
        return(self.sent_boundary)
        
    ## Function to determine if the input span overlaps this objects span
    # @author Amy Olex
    # @param start
    # @param end
    # @output True or False
    def spanOverlap(self, start, end) :
        if self.start_span<=start and self.end_span >=start:
            return True
        elif self.end_span >=end and self.start_span <= end:
            return True
        else:
            return False

## Function to convert a list of tokens into a list of refToken objects
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @param id_counter The number the ID counter should start at. Default is 0.
# @param span A list of spans for each token in the tok_list. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param pos A list of part-of-speech tags for each token in the tok_list. list. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param temporal A boolean list of 0's and 1' indicating which token contains temporal information. Must be the same length as tok_list. Assumes it is a one-to-one relationship in the same order as tok_list.
# @param remove_stopwords A boolean that, if true, removes tokens in the stopword list.  Defaults to False.
# @return A list of refToken objects in the same order as the input tok_list.
def convertToRefTokens(tok_list, id_counter=0, span=None, pos=None, temporal=None, sent_boundaries=None) :
    ref_list = list()
    tok_len = len(tok_list)
    ## figure out which lists were sent in
    include = [1, 0, 0, 0, 0]
    if span is not None:
        if len(span)==tok_len:
            include[1]=1
        else:
            raise ValueError('span list is not same length as token list.')
              
    if pos is not None:
        if len(pos)==tok_len:
            include[2]=1
        else:
            raise ValueError('pos list is not same length as token list.')
        
    if temporal is not None:
        if len(temporal)==tok_len:
            include[3]=1
        else:
            raise ValueError('temporal list is not same length as token list.')
    
    if sent_boundaries is not None:
        if len(sent_boundaries)==tok_len:
            include[4]=1
        else:
            raise ValueError('sentence boundary flag array is not same length as token list.')
    
    for idx in range(0,tok_len):
        ref_list.append(refToken(id=id_counter, text=tok_list[idx], start_span=span[idx][0] if include[1] else None, end_span=span[idx][1] if include[1] else None, pos=pos[idx][1] if include[2] else None, temporal=temporal[idx] if include[3] else None, sent_boundary=sent_boundaries[idx] if include[4] else None))
        id_counter = id_counter +1
        

        
    return ref_list

## Function to remove stopwords from a list of refToken objects
# @author Luke Maffey
# @param tok_list The list of tokens (required)
# @param stopwords_path The file with stopwords, defaults to "./stopwords_short"
# @return A list of refTokens in the same order as the input tok_list with stopwords removed

def removeStopWords(tok_list, stopwords_path="./stopwords_short") :
    with open(stopwords_path) as raw:
        stopwords = raw.read().splitlines()


    filtered_tokens = []
    for tok in tok_list :
        if tok.getText().lower() not in stopwords :
            filtered_tokens.append(tok)
    return filtered_tokens
    

## Function to remove all punctuation from a list of refToken objects
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list with punctuation removed

def replacePunctuation(tok_list) :
    
    for t in range(0,len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().translate(str.maketrans("", "", string.punctuation))) 
            
    return tok_list

## Function to convert all refToken objects to lowercase
# @author Amy Olex
# @param tok_list The list of tokens (required)
# @return A list of refTokens in the same order as the input tok_list converted to lowercase

def lowercase(tok_list) :
    
    for t in range(0,len(tok_list)):
        tok_list[t].setText(tok_list[t].getText().lower()) 
            
    return tok_list  
