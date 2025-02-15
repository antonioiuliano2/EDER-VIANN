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
parser.add_argument('--Set',help="Set Number", default='1')
parser.add_argument('--Fraction',help="Fraction", default='1')
parser.add_argument('--EOS',help="EOS location", default='')
parser.add_argument('--AFS',help="AFS location", default='')
parser.add_argument('--resolution',help="Resolution in microns per pixel", default='100')
parser.add_argument('--acceptance',help="Vertex fit minimum acceptance", default='0.5')
parser.add_argument('--MaxX',help="Image size in microns along the x-axis", default='3500.0')
parser.add_argument('--MaxY',help="Image size in microns along the y-axis", default='1000.0')
parser.add_argument('--MaxZ',help="Image size in microns along the z-axis", default='20000.0')
parser.add_argument('--ModelName',help="Name of the CNN model", default='2T_100_MC_1_model')
########################################     Main body functions    #########################################
args = parser.parse_args()
Set=args.Set
fraction=args.Fraction
resolution=float(args.resolution)
acceptance=float(args.acceptance)
#Maximum bounds on the image size in microns
MaxX=float(args.MaxX)
MaxY=float(args.MaxY)
MaxZ=float(args.MaxZ)
#Converting image size bounds in line with resolution settings
boundsX=int(round(MaxX/resolution,0))
boundsY=int(round(MaxY/resolution,0))
boundsZ=int(round(MaxZ/resolution,0))
H=boundsX*2
W=boundsY*2
L=boundsZ
AFS_DIR=args.AFS
EOS_DIR=args.EOS
input_track_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R1_TRACKS.csv'
input_seed_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R3_R4_FilteredSeeds_'+Set+'_'+fraction+'.csv'
output_seed_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R4_R4_RecSeeds_'+Set+'_'+fraction+'.csv'
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
print(UF.TimeStamp(),'Loading the model...')
#Load the model
model_name=EOS_DIR+'/EDER-VIANN/Models/'+args.ModelName
model=tf.keras.models.load_model(model_name)
#create seeds
GoodSeeds=[]
print(UF.TimeStamp(),'Beginning the vertexing part...')
for s in range(0,limit):
    seed=seeds.pop(0)
    decorated_seed=seed[:2]
    decorated_seed=UF.DecorateSeedTracks(decorated_seed,tracks)
    decorated_seed=UF.SortImage(decorated_seed)
    decorated_seed=UF.PreShiftImage(decorated_seed)
    seed_counter+=1
    if seed_counter>=1000:
              progress=int( round( (float(s)/float(limit)*100),0)  )
              print(UF.TimeStamp(),"Performing vertex fit on the seed",s,", progress is ",progress,' % of seeds analysed')
              print(UF.TimeStamp(),'Memory usage is',psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 'MB')
              seed_counter=0
    decorated_seed=UF.LonRotateImage(decorated_seed,'x')
    decorated_seed=UF.LonRotateImage(decorated_seed,'y')
    decorated_seed=UF.SortImage(decorated_seed)
    decorated_seed=UF.PhiRotateImage(decorated_seed)
    decorated_seed=UF.AfterShiftImage(decorated_seed,resolution)
    decorated_seed=UF.RescaleImage(decorated_seed,MaxX,MaxY,MaxZ,resolution)
    try:
       SeedImage=UF.LoadRenderImages([decorated_seed],resolution,MaxX,MaxY,MaxZ,1,1,False)[0]
    except:
       print(decorated_seed)
       exit()
    pred = model.predict(SeedImage)
    if pred[0][1]>=acceptance:
              seed.append(pred[0][1])
              GoodSeeds.append(seed)
    else:
              continue
print(UF.TimeStamp(),bcolors.OKGREEN+'The vertexing has been completed..'+bcolors.ENDC)
del tracks
del seeds
gc.collect()
print(UF.TimeStamp(),'Saving the results..')
UF.LogOperations(output_seed_file_location,'StartLog',GoodSeeds)
exit()
