#Belogs to: EDER-VIANN
#Purpose: To setup all working directories for the new user

########################################    Import libraries    #############################################
import csv
import os, shutil
import argparse
from shutil import copyfile
import subprocess
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
######################################## Work out whether user wants to uninstall the config ################
parser = argparse.ArgumentParser(description='Setup creation parameters')
parser.add_argument('--REMOVE',help="If you want to uninstall please enter Y", default='N')
args = parser.parse_args()
UserChoice=args.REMOVE
######################################## Create some functions to simplify the code   #######################
def FolderCreate(DIR):
    try:
      os.mkdir(DIR)
      print bcolors.OKBLUE+DIR+bcolors.ENDC, bcolors.OKGREEN+'folder has been created...'+bcolors.ENDC
    except:
      print bcolors.FAIL+'Problem creating '+bcolors.ENDC,bcolors.OKBLUE+DIR+bcolors.ENDC, bcolors.FAIL+'folder, probably it already exists...'+bcolors.ENDC

if UserChoice=='Y':
   csv_reader=open('config',"r")
   dir_reader = csv.reader(csv_reader)
   for row in dir_reader:
     if row[0]=='EOS_DIR':
       DEL_DIR=row[1]
       DEL_DIR+='/'+'EDER-VIANN'
       shutil.rmtree(DEL_DIR)
       break
   shutil.rmtree('HTCondor')
   shutil.rmtree('Code')
   os.remove('config')

   print bcolors.OKGREEN+'Uninstallation complete, you can delete setup.py and its parent directory manually if you wish'+bcolors.ENDC
   exit()


def CheckForData(String):
    if String[:4]!='TEST' and String[:2]!='ID':
        return True
    return False


def RecordExistCheck(Record, Data):
    for d in Data:
        if Record==d:
            return True
    return False

########################################     Work out and registering the current directory    #########################################
CurrDir=os.getcwd()
print 'Current directory is set as:', bcolors.OKBLUE+os.getcwd()+bcolors.ENDC
#Writing this directory into csv file so the software knows where to look data/code
csv_writer=open('config',"w")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('AFS_DIR')
string_to_write.append(CurrDir)
dir_writer.writerow(string_to_write)
print bcolors.OKGREEN+'Created the configuration file'+bcolors.ENDC

########################################     Create directories for HTCondor    #########################################
FolderCreate('HTCondor')
FolderCreate('HTCondor/MSG')
FolderCreate('HTCondor/SUB')
FolderCreate('HTCondor/SH')

#########################################   Workout EOS directory #################################
EOSDir=raw_input(bcolors.BOLD+"Please enter the full path of your directory on EOS:\n"+bcolors.ENDC)
#Writing this directory into csv file so the software knows where to look data/code
csv_writer=open('config',"a")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('EOS_DIR')
string_to_write.append(EOSDir)
dir_writer.writerow(string_to_write)
print bcolors.OKGREEN+'Updated the directory mapping file with EOS location'+bcolors.ENDC

########################################     Create sub-directories on EOS    #########################################

EOSsubDIR=EOSDir+'/'+'EDER-VIANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubTrainDIR=EOSsubDataDIR+'/'+'TRAIN_SET'
EOSsubValDIR=EOSsubDataDIR+'/'+'VALIDATION_SET'
EOSsubTestDIR=EOSsubDataDIR+'/'+'TEST_SET'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'

FolderCreate(EOSsubDIR)
FolderCreate(EOSsubDataDIR)
FolderCreate(EOSsubModelDIR)
FolderCreate(EOSsubEvoDIR)
FolderCreate(EOSsubTrainDIR)
FolderCreate(EOSsubValDIR)
FolderCreate(EOSsubTestDIR)
FolderCreate(EOSsubEvoModelDIR)

#########################################   Workout out training and validation files #################################
print bcolors.BOLD+'We have to make sure that we have training and validation files in relevant folders'+bcolors.ENDC
print bcolors.BOLD+'If you want to use original files that were created beforehand, please type Y/N below'+bcolors.ENDC
UserAnswer1=raw_input(bcolors.BOLD+"Would you like to copy default training and validation files?:\n"+bcolors.ENDC)
#Making action depending on user input
if UserAnswer1=='Y':
  TrainOrigin='/eos/experiment/ship/data/EDER-VIANN/TRAIN_SET/'
  src_files = os.listdir(TrainOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(TrainOrigin, file_name)

    if os.path.isfile(full_file_name) and ('IMAGES' in full_file_name==True):
        print 'Copying file', full_file_name, 'from ',bcolors.OKBLUE+TrainOrigin+bcolors.ENDC,'into', bcolors.OKBLUE+EOSsubTrainDIR+bcolors.ENDC
        shutil.copy(full_file_name, EOSsubTrainDIR)

  ValOrigin='/eos/experiment/ship/data/EDER-VIANN/VALIDATION_SET/'
  src_files = os.listdir(ValOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(ValOrigin, file_name)
    if os.path.isfile(full_file_name) and ('IMAGES' in full_file_name==True):
        print 'Copying file', full_file_name, 'from ',bcolors.OKBLUE+ValOrigin+bcolors.ENDC,'into', bcolors.OKBLUE+EOSsubValDIR+bcolors.ENDC
        shutil.copy(full_file_name, EOSsubValDIR)

  TestOrigin='/eos/experiment/ship/data/EDER-VIANN/TEST_SET/'
  src_files = os.listdir(TestOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(TestOrigin, file_name)
    if os.path.isfile(full_file_name):
        print 'Copying file', full_file_name, 'from ',bcolors.OKBLUE+TestOrigin+bcolors.ENDC,'into', bcolors.OKBLUE+EOSsubTestDIR+bcolors.ENDC
        shutil.copy(full_file_name, EOSsubTestDIR)
else:
   print bcolors.BOLD+'In this case, please make sure that you have put your custom training files in the folder:'+bcolors.ENDC, bcolors.OKBLUE+EOSsubTrainDIR+bcolors.ENDC
   print bcolors.BOLD+'They have to be named in the following format: CNN_TRAIN_IMAGES_#.csv where # is a file number'+bcolors.ENDC
   print bcolors.BOLD+'Also, please make sure that you have put your custom validation file in the folder:'+bcolors.ENDC, bcolors.OKBLUE+EOSsubValDIR+bcolors.ENDC
   print bcolors.BOLD+'They have to be named in the following format: CNN_VALIDATION_IMAGES.csv '+bcolors.ENDC
   print bcolors.BOLD+'Also, please make sure that you have put your custom test file in the folder:'+bcolors.ENDC, bcolors.OKBLUE+EOSsubTestDIR+bcolors.ENDC
   print bcolors.BOLD+'They have to be named in the following format: CNN_TEST_IMAGES.csv '+bcolors.ENDC
   raw_input(bcolors.BOLD+"Please press enter to continue setup once files are in the relevant folders.\n"+bcolors.ENDC)

print bcolors.OKGREEN+'EDER-VIANN setup is successfully completed' +bcolors.ENDC
exit()
