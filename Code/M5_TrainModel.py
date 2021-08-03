#import libraries
import numpy as np
from numpy.random import randint
import argparse
import ast
import csv
import os
from os import path
import random as rnd
from random import random
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Set the parsing module
parser = argparse.ArgumentParser(description='Enter training job parameters')
parser.add_argument('--Mode',help="Please enter the running mode: 'R' for reset, 'C' for continuing the training", default='C')
parser.add_argument('--ModelName',help="Which model would you like to use as a base for training (please enter N if you want to train a new model from scratch)", default='Default')
parser.add_argument('--ModelNewName',help="Would you like to save your pretrained model as a separate one", default='Default')
parser.add_argument('--LR',help="Would you like to modify the model Learning Rate, If yes please enter it here eg: 0.01 ", default='Default')
args = parser.parse_args()
#setting main learning parameters
mode=args.Mode
_=0
#Loading Directory locations
csv_reader=open('../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()

#Loading Data configurations
EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
import Parameters as PM
if args.ModelName=='Default':
    ModelName=PM.CNN_Model_Name
else:
    ModelName=args.ModelName

print(bcolors.HEADER+"####################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################  Initialising EDER-VIANN model training module   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC)
print(bcolors.HEADER+"###################### For troubleshooting please contact filips.fedotovs@cern.ch ##################"+bcolors.ENDC)
print(bcolors.HEADER+"####################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
#This code fragment covers the Algorithm logic on the first run
if mode=='R' and args.ModelName=='N':
 UF.TrainCleanUp(AFS_DIR, EOS_DIR, 'M5', ['M5_M5','M5_PERFORMANCE_'], "SoftUsed == \"EDER-VIANN-M5\"")
 job=[]
 job.append(1)
 job.append(1)
 job.append(PM.ModelArchitecture)
 job.append(PM.resolution)
 job.append(PM.MaxX)
 job.append(PM.MaxY)
 job.append(PM.MaxZ)
 job.append(args.LR)
 job.append(ModelName)
 if args.ModelNewName=='Default':
     job.append(ModelName)
 else:
     job.append(args.ModelNewName)
 print(UF.TimeStamp(),bcolors.OKGREEN+'Job description has been created'+bcolors.ENDC)
 PerformanceHeader=[['Epochs','Set','Training Samples','Train Loss','Train Accuracy','Validation Loss','Validation Accuracy']]
 UF.LogOperations(EOSsubModelDIR+'/M5_PERFORMANCE_'+job[9]+'.csv','StartLog',PerformanceHeader)
 UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,job,'New')
 job[8]=job[9]
 UF.LogOperations(EOSsubModelDIR+'/M5_M5_JobTask.csv','StartLog',[job])
 print(bcolors.BOLD+"Please the job completion in few hours by running this script with the option C"+bcolors.ENDC)
elif mode=='R':
 UF.TrainCleanUp(AFS_DIR, EOS_DIR, 'M5', ['M5_M5','M5_PERFORMANCE_'], "SoftUsed == \"EDER-VIANN-M5\"")
 job=[]
 job.append(1)
 job.append(1)
 job.append(PM.ModelArchitecture)
 job.append(PM.resolution)
 job.append(PM.MaxX)
 job.append(PM.MaxY)
 job.append(PM.MaxZ)
 job.append(args.LR)
 job.append(ModelName)
 if args.ModelNewName=='Default':
     job.append(ModelName)
 else:
     job.append(args.ModelNewName)
 print(UF.TimeStamp(),bcolors.OKGREEN+'Job description has been created'+bcolors.ENDC)
 PerformanceHeader=[['Epochs','Set','Training Samples','Train Loss','Train Accuracy','Validation Loss','Validation Accuracy']]
 UF.LogOperations(EOSsubModelDIR+'/M5_PERFORMANCE_'+job[9]+'.csv','StartLog',PerformanceHeader)
 UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,job,'Train')
 job[8]=job[9]
 UF.LogOperations(EOSsubModelDIR+'/M5_M5_JobTask.csv','StartLog',[job])
 print(bcolors.BOLD+"Please the job completion in few hours by running this script with the option C"+bcolors.ENDC)
if mode=='C':
   CurrentSet=0
   print(UF.TimeStamp(),'Continuing the training that has been started before')
   print(UF.TimeStamp(),'Checking the previous job completion...')
   csv_reader=open(EOSsubModelDIR+'/M5_M5_JobTask.csv',"r")
   PreviousJob = list(csv.reader(csv_reader))
   #if os.path.isfile(EOSsubModelDIR+'/'+PreviousJob[0][9])==False:
   #    print(UF.TimeStamp(),bcolors.FAIL+'Model',EOSsubModelDIR+ModelName,'has not been found '+bcolors.ENDC)
   #    print(bcolors.BOLD+"Please restart this script with the option R"+bcolors.ENDC)
   #    exit()
   csv_reader.close()
   CurrentSet=int(PreviousJob[0][0])
   CurrentEpoch=int(PreviousJob[0][1])
   ###Working out the latest batch
   ###Working out the remaining jobs
   required_file_name=EOSsubModelDIR+'/M5_M5_model_train_log_'+PreviousJob[0][0]+'.csv'
   if os.path.isfile(required_file_name)==False:
     print(UF.TimeStamp(),bcolors.WARNING+'Warning, the HTCondor job is still running'+bcolors.ENDC)
     print(bcolors.BOLD+'If you would like to wait and try again later please enter W'+bcolors.ENDC)
     print(bcolors.BOLD+'If you would like to resubmit please enter R'+bcolors.ENDC)
     UserAnswer=input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
     if UserAnswer=='W':
         print(UF.TimeStamp(),'OK, exiting now then')
         exit()
     if UserAnswer=='R':
        if CurrentSet==1:
          UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,PreviousJob[0],'Train')
        if CurrentSet>1:
          UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,PreviousJob[0],'Train')
        print(UF.TimeStamp(), bcolors.OKGREEN+"The Training Job for the CurrentSet",CurrentStep,"have been resubmitted"+bcolors.ENDC)
        print(bcolors.OKGREEN+"Please check it in a few hours"+bcolors.ENDC)
        exit()
   else:
      csv_reader=open(required_file_name,"r")
      PreviousHeader = list(csv.reader(csv_reader))
      UF.LogOperations(EOSsubModelDIR+'/M5_PERFORMANCE_'+PreviousJob[0][9]+'.csv','UpdateLog',PreviousHeader)
      os.unlink(required_file_name)
      print(UF.TimeStamp(),bcolors.OKGREEN+'The training of the model by using image set',CurrentSet,'has been completed'+bcolors.ENDC)
      print(UF.TimeStamp(),'Creating next batch',CurrentSet+1)
      print(bcolors.BOLD+'Image Set',CurrentSet,' is completed'+bcolors.ENDC)
      if os.path.isfile(EOS_DIR+'/EDER-VIANN/Data/TRAIN_SET/'+'M3_TRAIN_SET_'+str(CurrentSet+1)+'.csv')==False:
          print(bcolors.WARNING+'No more training files left, restarting the new epoch...'+bcolors.ENDC)
          CurrentSet=1
          CurrentEpoch+=1
          PreviousJob[0][0]=str(CurrentSet)
          PreviousJob[0][1]=str(CurrentEpoch)
          UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,PreviousJob[0],'Train')
          print(UF.TimeStamp(),bcolors.OKGREEN+'The Image Set',CurrentSet,'has been submitted to HTCondor'+bcolors.ENDC)
          exit()
      print(bcolors.BOLD+'Would you like to continue training?'+bcolors.ENDC)
      UserAnswer=input(bcolors.BOLD+"Please, enter Y/N\n"+bcolors.ENDC)
      if UserAnswer=='Y':
          CurrentSet+=1
          PreviousJob[0][0]=str(CurrentSet)
          UF.LogOperations(EOSsubModelDIR+'/M5_M5_JobTask.csv','StartLog',PreviousJob)
          UF.SubmitTrainJobCondor(AFS_DIR,EOS_DIR,PreviousJob[0],'Train')
          print(UF.TimeStamp(),bcolors.OKGREEN+'The next Image Set',CurrentSet,'has been submitted to HTCondor'+bcolors.ENDC)
          print(bcolors.BOLD,'Please run the script in few hours with --MODE C setting'+bcolors.ENDC)
          print(bcolors.HEADER+"############################################# End of the program ################################################"+bcolors.ENDC)

      if UserAnswer=='N':
          print(UF.TimeStamp(),bcolors.OKGREEN+'Training is finished then, thank you and good bye'+bcolors.ENDC)
          print(bcolors.HEADER+"############################################# End of the program ################################################"+bcolors.ENDC)
exit()


