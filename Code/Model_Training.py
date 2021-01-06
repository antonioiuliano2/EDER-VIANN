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
parser.add_argument('--MODE',help="Please enter the running mode: 'R' for reset, 'C' for continuing the training", default='C')
args = parser.parse_args()
#setting main learning parameters
mode=args.MODE
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
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print bcolors.HEADER+"#########################  Initialising EDER-VIANN model training module   #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC
print bcolors.HEADER+"###################### For troubleshooting please contact filips.fedotovs@cern.ch ##################"+bcolors.ENDC
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC

print UF.TimeStamp(),'Checking whether we have available DNA codes derived from evolution'
try:
  csv_reader=open(EOSsubEvoDIR+'/Population.csv',"r")
  evolution_models=list(csv_reader)
  csv_reader.close()
except:
  print UF.TimeStamp(),bcolors.WARNING+'No evolution models have been found '+bcolors.ENDC

#This code fragment covers the Algorithm logic on the first run
if mode=='R':
 job_list=[]
 UF.TrainCleanUp(AFS_DIR, EOS_DIR,'Full')
 print UF.TimeStamp(),bcolors.BOLD+'What model configurations would you like to use for training?'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to use Evolution derived Models please press E'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to use default model setting (aka Vanilla CNN) please enter D'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to specify for a particular configuration, please enter C'+bcolors.ENDC
 UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
 if UserAnswer=='D':
         job=[]
         job.append(1)
         job.append('Unknown')
         job.append('-')
         job.append(-0.5)
         job.append(0)
         print UF.TimeStamp(),bcolors.OKGREEN+'Job list has been created'+bcolors.ENDC
 if UserAnswer=='E':
    refined_evolution_models=[]
    for em in evolution_models:
      try:
          refined_evolution_models.append(ast.literal_eval(em))

      except:
       print bcolors.FAIL+'Error reading one of the records'+bcolors.END
    model_choice=[]
    model_choice=(sorted(refined_evolution_models,key=lambda x: float(x[4]),reverse=True)[:1])[0]
    job=[]
    job.append(1)
    job.append('Unknown')
    job.append(model_choice[3])
    job.append(-0.5)
    job.append(0)
 if UserAnswer=='C':
         print UF.TimeStamp(),bcolors.BOLD+'Please type model DNA'+bcolors.ENDC
         print UF.TimeStamp(),bcolors.BOLD+'The format is as follows [[x0,...,x5],[x0,...,x5],[x0,...,x5],[x0,...,x5],[x0,...,x5],[x0,...,x5],[y0,y1],[y0,y1],[y0,y1],[y0,y1],[y0,y1],[z1,z2,z3]]]'+bcolors.ENDC
         print UF.TimeStamp(),bcolors.BOLD+'Please consult documentation for accepted ranges'+bcolors.ENDC
         UserAnswer=raw_input(bcolors.BOLD+"Please, enter it here:\n"+bcolors.ENDC)
         job=[]
         job.append(1)
         job.append('Unknown')
         job.append(ast.literal_eval(UserAnswer))
         job.append(-0.5)
         job.append(0)
         print UF.TimeStamp(),bcolors.OKGREEN+'Job list has been created'+bcolors.ENDC
 job_list.append(job)
 UF.LogOperations(EOSsubModelDIR+'/TrainLog.csv','StartLog',job_list)
 UF.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,job_list,'New')
 print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
if mode=='C':
   CurrentSet=0
   print UF.TimeStamp(),'Continuing the training that has been started before'
   csv_reader=open(EOSsubModelDIR+'/TrainLog.csv',"r")
   PreviousJobs = list(csv.reader(csv_reader))
   csv_reader.close()
   ###Working out the latest batch
   for j in PreviousJobs:
       if int(j[0])>CurrentSet:
           CurrentSet=int(j[0])
   ###Working out the remaining jobs
   RemainingJobs=[]
   for j in PreviousJobs:
       if int(j[0])==CurrentSet:
           if int(j[4])==1:
               file_name=EOSsubModelDIR+'/model_log_'+j[0]+'.csv'
               try:
                csv_reader=open(file_name,"r")
                result = list(csv.reader(csv_reader))
                j[4]=1
                j[1]=result[0][1]
                j[3]=result[0][2]
                os.remove(file_name)
               except:
                RemainingJobs.append(j)
   UF.LogOperations(EOSsubModelDIR+'/TrainLog.csv','StartLog',PreviousJobs)
   if len(RemainingJobs)>0:
     print UF.TimeStamp(),bcolors.WARNING+'Warning, there are still', len(RemainingJobs), 'HTCondor jobs remaining'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to wait and try again later please enter W'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to resubmit please enter R'+bcolors.ENDC
     UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
     if UserAnswer=='W':
         print UF.TimeStamp(),'OK, exiting now then'
         exit()
     if UserAnswer=='R':
        if CurrentSet==1:
          UF.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,RemainingJobs,'New')
        if CurrentSet>1:
          UF.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,RemainingJobs,'Train')
        print UF.TimeStamp(), bcolors.OKGREEN+"All jobs for batch ",CurrentSet,"have been resubmitted"+bcolors.ENDC
        print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
        exit()
   if len(RemainingJobs)==0:
      NextJobs=[]
      print UF.TimeStamp(),'Creating next batch',CurrentSet+1
      for record in range(0,len(PreviousJobs)):
          if int(PreviousJobs[record][0])==CurrentSet:
                 PreviousJobs[record][0]=int(PreviousJobs[record][0])+1
                 PreviousJobs[record][1]=PreviousJobs[record][1]
                 PreviousJobs[record][2]=PreviousJobs[record][2]
                 PreviousJobs[record][3]=float(PreviousJobs[record][3])
                 PreviousJobs[record][4]=0
                 NextJobs.append(PreviousJobs[record])

      UF.TrainCleanUp(AFS_DIR,EOS_DIR,'Partial')
      print bcolors.BOLD+'Image Set',CurrentSet,' is completed'+bcolors.ENDC
      if os.path.isfile(EOS_DIR+'/EDER-VIANN/Data/TRAIN_SET/'+'CNN_TRAIN_IMAGES_'+str(CurrentSet+1)+'.csv')==False:
          print bcolors.WARNING+'No more training files left, hence exiting now...'+bcolors.ENDC
          exit()
      print bcolors.BOLD+'Would you like to continue training?'+bcolors.ENDC
      UserAnswer=raw_input(bcolors.BOLD+"Please, enter Y/N\n"+bcolors.ENDC)
      if UserAnswer=='Y':
          UF.LogOperations(EOSsubModelDIR+'/TrainLog.csv','UpdateLog',NextJobs)
          UF.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,NextJobs,'Train')
          print UF.TimeStamp(),bcolors.OKGREEN+'The next Image Set',CurrentSet+1,'has been submitted to HTCondor'+bcolors.ENDC
          print bcolors.BOLD,'Please run the script in few hours with --MODE C setting'+bcolors.ENDC

      if UserAnswer=='N':
          print UF.TimeStamp(),bcolors.OKGREEN+'Training is finished then, thank you and good bye'+bcolors.ENDC
exit()


