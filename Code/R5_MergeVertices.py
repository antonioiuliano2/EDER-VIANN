#This simple merges 2-Track vettices to produce the final result
# Part of EDER-VIANN package
#Made by Filips Fedotovs


########################################    Import libraries    #############################################
import csv
import argparse
import pandas as pd #We use Panda for a routine data processing
import math #We use it for data manipulation
import gc  #Helps to clear memory
import numpy as np
import os


class bcolors:   #We use it for the interface
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Setting the parser - this script is usually not run directly, but is used by a Master version Counterpart that passes the required arguments
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--Acceptance',help="Minimum acceptance for the track", default='0.5')
parser.add_argument('--DataCut',help="In how many chunks would you like to split data?", default='30')
######################################## Set variables  #############################################################
args = parser.parse_args()
Acceptance=float(args.Acceptance)




#Loading Directory locations
csv_reader=open('../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF #This is where we keep routine utility functions
import Parameters as PM #This is where we keep framework global parameters
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"######################     Initialising EDER-VIANN Vertex  module             ########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)

FileCounter=0
FileCounterContinue=True
VertexPool=[]
VertexPool.append(['Track_List','VX_X','VX_Y','VX_Z','VX_FIT','VX_ID'])
for i in range(0,int(args.DataCut)):
              FileCounter+=1
              input_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R4_REC_SEEDS.csv'
              print(UF.TimeStamp(), "Analysing set",i+1)
              csv_read_file=open(input_file_location,"r")
              csv_read = csv.reader(csv_read_file, delimiter=',')
              data=list(csv_read)
              csv_reader.close()
              TrackPosition=[]
              Vx_Fit_Pos=0
              for c in range(len(data[0])):
                  if ('VX_FIT' in data[0][c]):
                      Vx_Fit_Pos=c
              for c in range(len(data[0])):
                  if ('Track_' in data[0][c]):
                      TrackPosition.append(c)

              print(UF.TimeStamp(), "Stripping off the seeds with low acceptance...")
              new_data=[]
              for seed in data[1:]:
                  if float(seed[Vx_Fit_Pos])>=Acceptance:
                      new_data.append(seed)
              del data
              data=new_data
              del new_data
              gc.collect()
              length=len(data[1:])
              segment=int(round(math.ceil(length/int(args.DataCut)),0))
              data=data[1:]
              data=data[(i*segment):((i+1)*segment)]
              print(UF.TimeStamp(), "Restructuring the data...")
              for seed in data:

                  seed_container=[]
                  index_offset=0
                  for track in TrackPosition:
                      seed_container.append(seed.pop(track-index_offset))
                      index_offset+=1
                  seed.insert(0,seed_container)
                  seed[1]=float(seed[1])
                  seed[2]=float(seed[2])
                  seed[3]=float(seed[3])
                  seed[4]=float(seed[4])
                  seed.append(1)
              print(UF.TimeStamp(), "Initiating the seed merging...")
              InitialDataLength=len(data)-1
              SeedCounter=1
              SeedCounterContinue=True
              while SeedCounterContinue:
                  if SeedCounter>=len(data)-1:
                      SeedCounterContinue=False
                      break
                  progress=round((float(SeedCounter)/float(len(data)))*100,0)
                  print(UF.TimeStamp(),'progress is ',progress,' %', end="\r", flush=True) #Progress display
                  SubjectSeed=data[SeedCounter]
                  SubjectHit=False
                  iter=0
                  for ObjectSeed in data[SeedCounter+1:]:
                      if UF.CheckSeedsOverlap(SubjectSeed,ObjectSeed):
                            ObjectSeed[0]+=SubjectSeed[0]
                            ObjectSeed[0]=list(dict.fromkeys(ObjectSeed[0]))
                            ObjectSeed[1]+=SubjectSeed[1]
                            ObjectSeed[2]+=SubjectSeed[2]
                            ObjectSeed[3]+=SubjectSeed[3]
                            ObjectSeed[4]+=SubjectSeed[4]
                            ObjectSeed[5]+=SubjectSeed[5]
                            data.pop(SeedCounter)
                            SubjectHit=True
                  if SubjectHit==False:
                      SeedCounter+=1
              print(str(InitialDataLength), "2-track vertices were merged into", str(len(data)-1), 'vertices with higher multiplicity...')
              VertexPool+=data
print(UF.TimeStamp(), "Initiating the global vertex merging...")
del data
gc.collect()
InitialDataLength=len(VertexPool)-1
SeedCounter=0
SeedCounterContinue=True
while SeedCounterContinue:
    if SeedCounter==len(VertexPool)-1:
                      SeedCounterContinue=False
                      break
    progress=round((float(SeedCounter)/float(len(VertexPool)))*100,0)
    print(UF.TimeStamp(),'progress is ',progress,' %', end="\r", flush=True) #Progress display
    SubjectSeed=VertexPool[SeedCounter]
    SubjectHit=False
    for ObjectSeed in VertexPool[SeedCounter+1:]:
                if UF.CheckSeedsOverlap(SubjectSeed,ObjectSeed):
                            ObjectSeed[0]+=SubjectSeed[0]
                            ObjectSeed[0]=list(dict.fromkeys(ObjectSeed[0]))
                            ObjectSeed[1]+=SubjectSeed[1]
                            ObjectSeed[2]+=SubjectSeed[2]
                            ObjectSeed[3]+=SubjectSeed[3]
                            ObjectSeed[4]+=SubjectSeed[4]
                            ObjectSeed[5]+=SubjectSeed[5]
                            VertexPool.pop(SeedCounter)
                            SubjectHit=True
    if SubjectHit==False:
                      SeedCounter+=1
print(str(InitialDataLength), "vertices from different files were merged into", str(len(VertexPool)-1), 'vertices with higher multiplicity...')
for v in range(1,len(VertexPool)):
    VertexPool[v][1]/=VertexPool[v][5]
    VertexPool[v][2]/=VertexPool[v][5]
    VertexPool[v][3]/=VertexPool[v][5]
    VertexPool[v][4]/=VertexPool[v][5]
    VertexPool[v][5]=v
output_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R5_REC_VERTICES.csv'

print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), "Saving the results into the file",bcolors.OKBLUE+output_file_location+bcolors.ENDC)
UF.LogOperations(output_file_location,'StartLog',VertexPool)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(),bcolors.OKGREEN+'The vertex merging has been completed..'+bcolors.ENDC)
print(bcolors.HEADER+"############################################# End of the program ################################################"+bcolors.ENDC)
