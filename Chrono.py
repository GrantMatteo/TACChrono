# Copyright (c) 2018 
# Amy L. Olex, Virginia Commonwealth University
# alolex at vcu.edu
# ONE 1 II
# ONE 1 II
# ONE 1 II


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

## This is the main driver program that runs Chrono.  

import argparse
import os
import pickle
import spacy
import re
from chronoML import FrequencyRNN as rnn
from chronoML import DecisionTree as DTree
from chronoML import RF_classifier as RandomForest
from chronoML import NB_nltk_classifier as NBclass, ChronoKeras
from chronoML import SVM_classifier as SVMclass
from Chrono import DosePhrase_to_Chrono
from Chrono import BuildEntities
# from Chrono import TimePhrase_to_Chrono
from Chrono import referenceToken
from Chrono import utils
import keras
from keras.models import load_model


debug=False
## This is the driver method to run all of Chrono.
# @param INDIR The location of the directory with all the files in it.
# @param OUTDIR The location of the directory where you want all the output written.
# @param REFDIR The location of the gold standard XML files for evaluation.
# @return Anafora formatted XML files, one directory per file with one XML file in each directory.
# @return The precision and recall from comparing output results to the gold standard.
if __name__ == "__main__":
    
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Parse a directory of files to identify and normalize temporal information.')
    parser.add_argument('-i', metavar='inputdir', type=str, help='path to the input directory.', required=True)
    parser.add_argument('-x', metavar='fileExt', type=str, help='input file extension if exists. Default is and empty string', required=False, default="")
    parser.add_argument('-o', metavar='outputdir', type=str, help='path to the output directory.', required=True)
    parser.add_argument('-m', metavar='useML', type=str, help='Whether to use ML classification (1) or not (0) (default 0)', required=False, default='0')
    parser.add_argument('-w', metavar='windowSize', type=str, help='An integer representing the window size for context feature extraction. Default is 3.', required=False, default=3)
    parser.add_argument('-d', metavar='MLTrainData', type=str, help='A string representing the file name that contains the CSV file with the training data matrix.', required=False, default=False)
    parser.add_argument('-c', metavar='MLTrainClass', type=str, help='A string representing the file name that contains the known classes for the training data matrix.', required=False, default=False)
    parser.add_argument('-M', metavar='MLmodel', type=str, help='The path and file name of a pre-build ML model for loading.', required=False, default=None)
    parser.add_argument('-T', metavar='TrainingPath', type=str, help='1 if we are training a new model, 0 otherwise', required=False, default='0')
    parser.add_argument('-X', metavar='XMLOUT', type=str, help='1 if you want xml out, 0 otherwise (deafault 0)', required=False, default='0')
    args = parser.parse_args()
    ## Now we can access each argument as args.i, args.o, args.r
    print(args.i)

    ## Get list of folder names in the input directory
    indirs = []
    infiles = []
    xml_outfiles = []
    ann_outfiles = []
    outdirs = []

    for root, dirs, files in os.walk(args.i, topdown = True):
       for name in files:
           if (args.x in name):
               name=re.sub("\\"+ args.x, "", name)
               indirs.append(os.path.join(root, name))
               infiles.append(os.path.join(root,name))
               ann_outfiles.append(os.path.join(args.o, "anns", name))
               xml_outfiles.append(os.path.join(args.o, name, name))
               outdirs.append(os.path.join(args.o,name))
               if args.X=="1" and not os.path.exists(os.path.join(args.o,name)):
                   os.makedirs(os.path.join(args.o,name))
               if not os.path.exists(os.path.join(args.o, "anns")):
                   os.makedirs(os.path.join(args.o, "anns"))
    ## Get training data for ML methods by importing pre-made boolean matrix
    ## Train ML methods on training data


    classifier=keras.models.load_model(args.M)
    xTotal=[]
    yTotal=[]
    totDiff=0
    #TODO delete
    for f in range(0,len(infiles)) :
        print("Parsing "+ infiles[f] +" ...")
        ## Init the ChronoEntity list
        my_chronoentities = []
        chrono_ID_counter=1


        text, tokens, spans, tags, sents = utils.getWhitespaceTokens(infiles[f]+ args.x)




        my_refToks = referenceToken.convertToRefTokens(tok_list=tokens, span=spans, pos=tags, sent_boundaries=sents)

    
        chroList = utils.markNotable(my_refToks)
        try:
            with open("/home/garnt/Documents/ChroDeb.out", "w") as deb:
                for chro in chroList:
                    deb.write(chro.getFreqDebug()+"\n")
        except:
            print("Debug Output to /home/garnt/Documents failed in Chrono.py")
        freqPhrases = utils.getFrequencyPhrases(chroList, text)

        freqPhrases = utils.preProcessPhrases(freqPhrases)
        nnYList, nnXList = BuildEntities.getMLFeats(freqPhrases, infiles[f] + ".ann" if args.T=='1' else None)
        if (args.T=='1'):
            for x, y in zip(nnXList, nnYList):
                xTotal.append(x)
                yTotal.append(y)
        else:
            for x in nnXList:
                xTotal.append(x)
        chrono_master_list=[]
        chro_check_list, useless = BuildEntities.buildChronoList(freqPhrases, 0, chroList)

        if (args.m=='1'):
            if (len(nnXList)>0):
                chrono_master_list, my_freq_ID_counter =BuildEntities.buildChronoListML(TimePhraseList=freqPhrases, chrono_id=chrono_ID_counter, ref_list= chroList, X=nnXList, classifier=classifier)
            else:
                print("skipped")
                chrono_master_list, my_freq_ID_counter = BuildEntities.buildChronoList(freqPhrases,
                                                                                       chrono_ID_counter, chroList)
        else:
            chrono_master_list, my_freq_ID_counter = BuildEntities.buildChronoList(freqPhrases,
                                                                             chrono_ID_counter, chroList)

        print("Number of Chrono Entities: " + str(len(chrono_master_list)))
        if (args.X=='1'):
            utils.write_xml(chrono_list=chrono_master_list, outfile=xml_outfiles[f])
        utils.write_ann(chrono_list=chrono_master_list, outfile=ann_outfiles[f])
    if args.T =='1':
        classifier=rnn.build_model(xTotal, yTotal)
        classifier.save("/home/garnt/Documents/Models/2.pkl")
