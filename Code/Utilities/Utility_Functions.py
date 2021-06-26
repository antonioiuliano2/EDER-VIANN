###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
#import math
import os, shutil
import subprocess
#import time as t
import datetime
#import ast
#import numpy as np
#import scipy
#import copy
#from scipy.stats import chisquare
#import tensorflow as tf
#from tensorflow import keras
#This utility provides Timestamps for print messages
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"

def CleanFolder(folder,key):
    if key=='':
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    else:
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path) and (key in the_file):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
#This function automates csv read/write operations
def LogOperations(flocation,mode, message):
    if mode=='UpdateLog':
        csv_writer_log=open(flocation,"a")
        log_writer = csv.writer(csv_writer_log)
        for m in message:
         log_writer.writerow(m)
        csv_writer_log.close()
    if mode=='StartLog':
        csv_writer_log=open(flocation,"w")
        log_writer = csv.writer(csv_writer_log)
        for m in message:
         log_writer.writerow(m)
        csv_writer_log.close()
    if mode=='ReadLog':
        csv_reader_log=open(flocation,"r")
        log_reader = csv.reader(csv_reader_log)
        return list(log_reader)

def SubmitCreateSeedsJobsCondor(job):
            SHName=job[11]+'/HTCondor/SH/SH_CS_'+str(job[0])+'_'+str(job[1])+'.sh'
            SUBName=job[11]+'/HTCondor/SUB/SUB_CS_'+str(job[0])+'_'+str(job[1])+'.sub'
            MSGName='MSG_CS_'
            OptionLine=(' --Set '+str(job[0]))
            OptionLine+=(" --Subset "+str(job[1]))
            OptionLine+=(" --EOS "+str(job[12]))
            OptionLine+=(" --AFS "+str(job[11]))
            OptionLine+=(" --PlateZ "+str(job[2]))
            OptionLine+=(" --MaxTracks "+str(job[10]))
            OptionLine+=(" --SI_1 "+str(job[3]))
            OptionLine+=(" --SI_2 "+str(job[4]))
            OptionLine+=(" --SI_3 "+str(job[5]))
            OptionLine+=(" --SI_4 "+str(job[6]))
            OptionLine+=(" --SI_5 "+str(job[7]))
            OptionLine+=(" --SI_6 "+str(job[8]))
            OptionLine+=(" --SI_7 "+str(job[9]))
            MSGName+=str(job[0])
            MSGName+='_'
            MSGName+=str(job[1])
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+job[11]+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+job[11]+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+job[11]+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('+SoftUsed = "EDER-VIANN-CS"')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+job[11]+'/Code/Utilities/R2_GenerateSeeds_Sub.py '+OptionLine
            f = open(SHName, "w")
            f.write("#!/bin/bash")
            f.write("\n")
            f.write("set -ux")
            f.write("\n")
            f.write(TotalLine)
            f.write("\n")
            f.close()
            subprocess.call(['condor_submit',SUBName])
            print(TotalLine," has been successfully submitted")

def CreateSeedsCleanUp(AFS_DIR, EOS_DIR):
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-CS\""])
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/REC_SET'
      folder =  EOSsubModelDIR
      CleanFolder(folder,'SEED_SET_')
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_CS_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_CS_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_CS_')
