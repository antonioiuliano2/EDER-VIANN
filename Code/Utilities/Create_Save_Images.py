#This simple script prepares data for CNN
########################################    Import libraries    #############################################
import csv
import argparse
import math
import copy
import numpy as np
import random
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
parser.add_argument('--VXM',help="Please enter the maximum vertex multiplicity number", default='10')
parser.add_argument('--Type',help="What samples type:train/val", default='train')
parser.add_argument('--Samples',help="How many samples per set?", default='10')
parser.add_argument('--Sets',help="How many training sets?", default='10')
parser.add_argument('--InitialSamples',help="How many initial samples?", default='10')
parser.add_argument('--Quota',help="What is the True vertex/Fake vertex quota?", default='0.5')
parser.add_argument('--Oversampling',help="Enter oversampling probability (0.0-1.0)?", default='0.0')
########################################     Main body functions    #########################################
args = parser.parse_args()
VxMult=int(args.VXM)
samples=float(args.InitialSamples)
sets=int(args.Sets)
quota=float(args.Quota)
Oversampling=float(args.Oversampling)
Bound=4000
if args.Type=='train':
   flocation='/eos/experiment/ship/data/EDER-VIANN/TRAIN_SET/CNN_TRAIN_SET.csv'
   totalsamples=int(args.Samples)*sets
if args.Type=='val':
   flocation='/eos/experiment/ship/data/EDER-VIANN/VALIDATION_SET/CNN_VALIDATION_SET.csv'
   totalsamples=int(args.Samples)
fakesamples=sets*totalsamples
Tsamples=int(round(samples*quota))
Fsamples=int(round(float(totalsamples)*(1.0-quota),0))
#Loading Directory locations
csv_reader=open('../../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################    Initialising EDER-VIANN image preparation module  #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading data from ',bcolors.OKBLUE+flocation+bcolors.ENDC)
csv_read_file=open(flocation,"r")
csv_read = csv.reader(csv_read_file, delimiter=',')
Seeds=[]
data=list(csv_read)
csv_read_file.close()
#Identify potential seeds
for d in range(1,len(data)):
        progress=int(round((float(d)/float(len(data)))*100,0))
        print("Loading data, progress is ",progress,' %', end="\r", flush=True)
        Track=[]
        Track.append(data[d][0])
        Track.append(data[d][1])
        if (Track in Seeds)==False:
            Seeds.append(Track)

InitialSeeds=len(Seeds)
print(UF.TimeStamp(),'Cleaning up seeds... ')
Seeds=UF.EvaluateSeeds(Seeds,data)
Seeds[:] = [x for x in Seeds if not x[2]=='BT']
print(UF.TimeStamp(), bcolors.OKGREEN+str(InitialSeeds-len(Seeds)), "bad seeds that represent 1-point tracks have been removed..."+bcolors.ENDC)
InitialData=len(data)
data=UF.RemoveBadTracks(Seeds,data)
print(UF.TimeStamp(), bcolors.OKGREEN+str(InitialData-len(data)), "bad track hit records have been removed..."+bcolors.ENDC)
for s in range(len(Seeds)):
    Seeds[s]=(Seeds[s])[:2]
print(UF.TimeStamp(),bcolors.OKGREEN+'Data has been successfully loaded and prepared..'+bcolors.ENDC)
print(UF.TimeStamp(),bcolors.BOLD+str(len(Seeds))+bcolors.ENDC, 'tracks have been identified...')
print(UF.TimeStamp(),'Creating 2-track seeds...')
#create seeds
Mothers=[]
Seed1Pos=0
Seed2Pos=0
def Ingest2TrackSeeds(Seeds,Fsamples,Tsamples,MaxOffset):
 SampleCount=0
 Images=[]
 InitialTsampleC=Tsamples
 InitialFsampleC=Fsamples
 for SdItr1 in range(0,len(Seeds)):
     for SdItr2 in range(0,len(Seeds)):
        if Seeds[SdItr1][0]!=Seeds[SdItr2][0]:
         if ((Seeds[SdItr1][1]!=Seeds[SdItr2][1]) or (Seeds[SdItr1][1]=='P') or (Seeds[SdItr2][1]=='P')) and Fsamples>0:
             progress=int(round((float(InitialFsampleC-Fsamples)/float(InitialFsampleC))*100,0))
             print("Created",InitialFsampleC-Fsamples," fake 2-track seeds, progress is ",progress,' %', end="\r", flush=True)
             SampleCount+=1
             seed=[]
             seed.append(SampleCount)
             seed.append([])
             seed.append([])
             seed[1].append(Seeds[SdItr1][0])
             seed[1].append(Seeds[SdItr2][0])
             seed[2].append(Seeds[SdItr1][1])
             seed[2].append(Seeds[SdItr2][1])
             seed.append('0')
             UF.DecorateSeedTracks(seed,data)
             UF.SortImage(seed)
             UF.LonRotateImage(seed)
             UF.SortImage(seed)
             UF.ShiftImage(seed)
             if UF.SeedQualityCheck(seed,MaxOffset):
              UF.PhiRotateImage(seed)
              Fsamples-=1
              Images.append(seed)
             else:
              SampleCount-=1
         if (Seeds[SdItr1][1]==Seeds[SdItr2][1]) and (Seeds[SdItr1][1]!='P') and (Tsamples>0) and (Seeds[SdItr1][1] in Mothers)==False:
             progress=int(round((float(InitialTsampleC-Tsamples)/float(InitialTsampleC))*100,0))
             print("Created",InitialTsampleC-Tsamples,"  genuine 2-track seeds, progress is ",progress,' %', end="\r", flush=True)
             SampleCount+=1
             seed=[]
             seed.append(SampleCount)
             seed.append([])
             seed.append([])
             seed[1].append(Seeds[SdItr1][0])
             seed[1].append(Seeds[SdItr2][0])
             seed[2].append(Seeds[SdItr1][1])
             seed[2].append(Seeds[SdItr2][1])
             if random.random()>Oversampling:
                Mothers.append(Seeds[SdItr1][1])
             seed.append('2')
             UF.DecorateSeedTracks(seed,data)
             UF.SortImage(seed)
             UF.LonRotateImage(seed)
             UF.SortImage(seed)
             UF.ShiftImage(seed)
             UF.PhiRotateImage(seed)
             Tsamples-=1
             Images.append(seed)
         if Tsamples==0 and Fsamples==0:
            return Images
 return Images
def IngestNTrackSeeds(Seeds,Images,Multiplicity,Fsamples,Tsamples,MaxOffset):
   SampleCount=0
   NewImages=[]
   InitialTsampleC=Tsamples
   InitialFsampleC=Fsamples
   for Sd in Seeds:
     for Im in Images:
             if Im[3]!='0' and ('.' in Im[3])==False:
                 if int(Im[3])==Multiplicity-1:
                     if UF.CheckSeedOverlap(Im,Sd)==True:
                         if ((Im[2][0]!=Sd[1]) or (Sd[1]=='P')) and Fsamples>0:
                            progress=int(round((float(InitialFsampleC-Fsamples)/float(InitialFsampleC))*100,0))
                            print("Created",InitialFsampleC-Fsamples,"  fake",Multiplicity,"-track seeds, progress is ",progress,' %', end="\r", flush=True)
                            SampleCount+=1
                            seed=[]
                            seed.append(SampleCount)
                            seed.append([])
                            seed.append([])
                            for tr in Im[1]:
                               seed[1].append(tr)
                            seed[1].append(Sd[0])
                            seed[2].append(Im[2][0])
                            seed[2].append(Sd[1])
                            seed.append(str(VM-1)+'.5')
                            UF.DecorateSeedTracks(seed,data)
                            UF.SortImage(seed)
                            UF.LonRotateImage(seed)
                            UF.SortImage(seed)
                            UF.ShiftImage(seed)
                            if UF.SeedQualityCheck(seed,MaxOffset):
                             UF.PhiRotateImage(seed)
                             Fsamples-=1
                             NewImages.append(seed)
                            else:
                               SampleCount-=1
                         if (Im[2][0]==Sd[1]) and (Sd[1]!='P') and (Tsamples>0) and (Sd[1] in Mothers)==False:
                             progress=int(round((float(InitialTsampleC-Tsamples)/float(InitialTsampleC))*100,0))
                             print("Created",InitialTsampleC-Tsamples,"  genuine",Multiplicity,"-track seeds, progress is ",progress,' %', end="\r", flush=True)
                             SampleCount+=1
                             seed=[]
                             seed.append(SampleCount)
                             seed.append([])
                             seed.append([])
                             for tr in Im[1]:
                                seed[1].append(tr)
                             seed[1].append(Sd[0])
                             seed[2].append(Im[2][0])
                             seed[2].append(Sd[1])
                             if random.random()>Oversampling:
                                Mothers.append(Sd[1])
                             seed.append(str(VM))
                             UF.DecorateSeedTracks(seed,data)
                             UF.SortImage(seed)
                             UF.LonRotateImage(seed)
                             UF.SortImage(seed)
                             UF.ShiftImage(seed)
                             UF.PhiRotateImage(seed)
                             Tsamples-=1
                             NewImages.append(seed)
             if Tsamples==0 and Fsamples==0:
                return NewImages
   return NewImages
GenuineImages=[]
FakeImages=[]
GenuineImages.append(Ingest2TrackSeeds(Seeds,0,Tsamples,Bound))
print(UF.TimeStamp(),bcolors.OKGREEN+str(len(GenuineImages[0])),'Two track genuine images have been created..'+bcolors.ENDC)
if len(GenuineImages[0])<Tsamples:
    print(UF.TimeStamp(),bcolors.WARNING+'Warning, data contains',str(len(GenuineImages[0])),'Two-track genuine seeds, which is less than the required',str(Tsamples),'seeds...'+bcolors.ENDC)
    samples=int(round(len(GenuineImages[0])/quota))
    Tsamples=len(GenuineImages[0])
    Fsamples=min(samples-Tsamples,Fsamples)
FakeImages.append(Ingest2TrackSeeds(Seeds,Fsamples,0,Bound))
print(UF.TimeStamp(),bcolors.OKGREEN+str(len(FakeImages[0])),'Two track fake images have been created..'+bcolors.ENDC)
#Creating seeds with higher track multiplicity
if VxMult>=3:
 for VM in range(3,VxMult+1):
    Mothers=[]
    GenuineImages.append(IngestNTrackSeeds(Seeds,GenuineImages[VM-3],VM,0,Tsamples,Bound))
    samples=int(round(len(GenuineImages[VM-2])/quota))
    Tsamples=len(GenuineImages[VM-2])
    Fsamples=min(samples-Tsamples,Fsamples)
    FakeImages.append(IngestNTrackSeeds(Seeds,GenuineImages[VM-3],VM,Fsamples,0,Bound))
    if len(GenuineImages[VM-2])==0:
       print(UF.TimeStamp(),bcolors.FAIL+'Ingestion of Genuine', VM,'-track vertices has been starved'+bcolors.ENDC)
       print(UF.TimeStamp(),bcolors.FAIL+'Please consider a higher number of initial seeds'+bcolors.ENDC)
       break
    if len(GenuineImages[VM-2])<Tsamples:
#       CurrentTsamples=len(GenuineImages[VM-2])
#       NewSamples=int(round(CurrentTsamples/quota))
#       NewFakeSamples=NewSamples-CurrentTsamples
#       FakeImages[VM-2]=(FakeImages[VM-2])[:NewFakeSamples]
       print(UF.TimeStamp(),bcolors.WARNING+'----------------------------------------------------------------------------'+bcolors.ENDC)
       print(UF.TimeStamp(),bcolors.WARNING+str(len(GenuineImages[VM-2])),' ',VM,'-track genuine vertices have been added'+bcolors.ENDC)
       print(UF.TimeStamp(),bcolors.WARNING+str(len(FakeImages[VM-2])),' ',VM,'-track fake vertices have been added'+bcolors.ENDC)
    if len(GenuineImages[VM-2])==Tsamples:
       print(UF.TimeStamp(),bcolors.OKGREEN+'------------------------------------------------------------------------------'+bcolors.ENDC)
       print(UF.TimeStamp(),bcolors.OKGREEN+str(len(GenuineImages[VM-2])),' ',VM,'-track genuine vertices have been added'+bcolors.ENDC)
       print(UF.TimeStamp(),bcolors.OKGREEN+str(len(FakeImages[VM-2])),' ',VM,'-track fake vertices have been added'+bcolors.ENDC)
SuperImages=[]
for FI in range(0,len(GenuineImages)):
    SuperImages.append(GenuineImages[FI]+FakeImages[FI])
for Batch in SuperImages:
  random.shuffle(Batch)
  if len(Batch)>totalsamples:
     Batch=Batch[:totalsamples]
Count=0
if args.Type=='train':
   final_count=sets+1
if args.Type=='val':
   final_count=2
for set in range(1,final_count):
  if args.Type=='train':
     olocation='/eos/experiment/ship/data/EDER-VIANN/TRAIN_SET/CNN_TRAIN_IMAGES'+'_'+str(set)+'.csv'
  if args.Type=='val':
    olocation='/eos/experiment/ship/data/EDER-VIANN/VALIDATION_SET/CNN_VALIDATION_IMAGES_1.csv'
  csv_write=open(olocation,"w")
  writer = csv.writer(csv_write)
  for Batch in SuperImages:
     if ((set-1)*round((float(totalsamples)/float(sets)))>len(Batch)):
         continue
     for Sd in range(int((set-1)*(float(totalsamples)/float(sets))),min(len(Batch),int(set*(float(totalsamples)/float(sets))))):
         Count+=1
         Batch[Sd][0]=Count
         writer.writerow(Batch[Sd])
csv_write.close()
print(UF.TimeStamp(),bcolors.OKGREEN+'Training and validation images have been saved in the csv'+bcolors.ENDC)
exit()



