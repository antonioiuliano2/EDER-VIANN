#This simple script prepares data for CNN
########################################    Import libraries    #############################################
#import csv
import Utility_Functions as UF
import argparse
import pandas as pd #We use Panda for a routine data processing
#import math
#import copy
#import numpy as np
#import random
import tensorflow as tf
from tensorflow import keras

import os, psutil #helps to monitor the memory
import gc  #Helps to clear memory

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--SubSet',help="SubSet Number", default='1')
parser.add_argument('--Fraction',help="Fraction", default='1')
parser.add_argument('--EOS',help="EOS location", default='')
parser.add_argument('--AFS',help="AFS location", default='')
########################################     Main body functions    #########################################
args = parser.parse_args()
SubSet=args.SubSet
fraction=args.Fraction


AFS_DIR=args.AFS
EOS_DIR=args.EOS

input_track_file_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/E7_KALMAN_REC_VERTICES.csv'
input_seed_file_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/E8_E9_RawSeeds_'+SubSet+'_'+fraction+'.csv'
output_seed_file_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/E9_E9_DecoratedSeeds_'+SubSet+'_'+fraction+'.csv'
print(UF.TimeStamp(),'Loading the data')
seeds=pd.read_csv(input_seed_file_location)
seeds_1=seeds.drop(['Track_2'],axis=1)
seeds_1=seeds_1.rename(columns={"Track_1": "Track_ID"})
seeds_2=seeds.drop(['Track_1'],axis=1)
seeds_2=seeds_2.rename(columns={"Track_2": "Track_ID"})
seed_list=result = pd.concat([seeds_1,seeds_2])
seed_list=seed_list.sort_values(['Track_ID'])
seed_list.drop_duplicates(subset="Track_ID",keep='first',inplace=True)
tracks=pd.read_csv(input_track_file_location)
print(UF.TimeStamp(),'Analysing the data')
tracks=pd.merge(tracks, seed_list, how="inner", on=["Track_ID"]) #Shrinking the Track data so just a star hit for each track is present.
tracks["x"] = pd.to_numeric(tracks["x"],downcast='float')
tracks["y"] = pd.to_numeric(tracks["y"],downcast='float')
tracks["z"] = pd.to_numeric(tracks["z"],downcast='float')
tracks = tracks.values.tolist() #Convirting the result to List data type
seeds = seeds.values.tolist() #Convirting the result to List data type
del seeds_1
del seeds_2
del seed_list
gc.collect()
limit=len(seeds)
seed_counter=0
print(UF.TimeStamp(),bcolors.OKGREEN+'Data has been successfully loaded and prepared..'+bcolors.ENDC)
#create seeds
GoodSeeds=[]
print(UF.TimeStamp(),'Beginning the decorating part...')
for s in range(0,limit):
    seed=seeds.pop(0)
    seed=UF.DecorateSeedTracks(seed,tracks)
    seed=UF.SortImage(seed)
    VO=UF.GiveExpressSeedInfo(seed)[0].tolist()
    seed=UF.PreShiftImage(seed)
    seed_counter+=1
    if seed_counter>=1000:
              progress=int( round( (float(s)/float(limit)*100),0)  )
              print(UF.TimeStamp(),"Performing seed decoration",s,", progress is ",progress,' % of seeds are decorated')
              print(UF.TimeStamp(),'Memory usage is',psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
              seed_counter=0

    seed=UF.LonRotateImage(seed,'x')
    seed=UF.LonRotateImage(seed,'y')
    seed=UF.SortImage(seed)
    seed=UF.PhiRotateImage(seed)
    SEI=UF.GiveFullSeedInfo(seed)
    new_seed=[seed[0][0],seed[0][1],VO[0],VO[1],VO[2],SEI[1],SEI[2],SEI[3],SEI[4],SEI[5]]
    GoodSeeds.append(new_seed)
print(UF.TimeStamp(),bcolors.OKGREEN+'The evaluation seed decoration has been completed..'+bcolors.ENDC)
del tracks
del seeds
gc.collect()
print(UF.TimeStamp(),'Saving the results..')
UF.LogOperations(output_seed_file_location,'StartLog',GoodSeeds)
exit()
