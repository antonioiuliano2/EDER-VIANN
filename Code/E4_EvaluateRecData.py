#This simple script prepares 2-Track seeds for the initial CNN vertexing
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
parser.add_argument('--Acceptance',help="What is the mininimum acceptance", default='0.5')

######################################## Set variables  #############################################################
args = parser.parse_args()
acceptance=float(args.Acceptance)




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
########################################     Preset framework parameters    #########################################
 #The Separation bound is the maximum Euclidean distance that is allowed between hits in the beggining of Seed tracks.
MaxTracksPerJob = PM.MaxTracksPerJob
#Specifying the full path to input/output files
input_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/REC_SET.csv'
input_eval_file_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/VX_EVAL_DEC_SET.csv'
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"######################     Initialising EDER-VIANN Evaluation module             ########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading preselected data from ',bcolors.OKBLUE+input_file_location+bcolors.ENDC)
data=pd.read_csv(input_file_location,header=0,usecols=['Track_ID','z'])
print(UF.TimeStamp(),'Analysing data... ',bcolors.ENDC)
data = data.groupby('Track_ID')['z'].min()  #Keeping only starting hits for the each track record (we do not require the full information about track in this script)
data=data.reset_index()
data = data.groupby('z')['Track_ID'].count()  #Keeping only starting hits for the each track record (we do not require the full information about track in this script)
data=data.reset_index()
data=data.sort_values(['z'],ascending=True)
data['Sub_Sets']=np.ceil(data['Track_ID']/MaxTracksPerJob)
data['Sub_Sets'] = data['Sub_Sets'].astype(int)
data = data.values.tolist() #Convirting the result to List data type
print(UF.TimeStamp(),'Analysing evaluation data... ',bcolors.ENDC)
if os.path.isfile(input_eval_file_location)!=True:
                 print(UF.TimeStamp(), bcolors.FAIL+"Critical fail: file",input_eval_file_location,'is missing, please restart the evaluation sequence scripts'+bcolors.ENDC)
eval_data=pd.read_csv(input_eval_file_location,header=0,usecols=['Track_1','Track_2'])
eval_data["Seed_ID"]= ['-'.join(sorted(tup)) for tup in zip(eval_data['Track_1'], eval_data['Track_2'])]
eval_data.drop_duplicates(subset="Seed_ID",keep='first',inplace=True)
eval_data.drop(eval_data.index[eval_data['Track_1'] == eval_data['Track_2']], inplace = True)
eval_data.drop(["Track_1"],axis=1,inplace=True)
eval_data.drop(["Track_2"],axis=1,inplace=True)
TotalMCVertices=len(eval_data.axes[0])
TotalRecVertices=0
MatchedVertices=0
FakeVertices=0
for j in range(0,len(data)):
             print(UF.TimeStamp(),'Evaluating reconstructed set ',str(j+1),bcolors.ENDC)
             test_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/VX_REC_SET_'+str(j+1)+'.csv'
             if os.path.isfile(test_file_location)!=True:
                 print(UF.TimeStamp(), bcolors.FAIL+"Critical fail: file",test_file_location,'is missing, please restart the reconstruction sequence scripts'+bcolors.ENDC)
             test_data=pd.read_csv(test_file_location,header=0,usecols=['Track_1','Track_2','VX_FIT'])
             test_data["Seed_ID"]= ['-'.join(sorted(tup)) for tup in zip(test_data['Track_1'], test_data['Track_2'])]
             test_data.drop_duplicates(subset="Seed_ID",keep='first',inplace=True)
             test_data.drop(test_data.index[test_data['Track_1'] == test_data['Track_2']], inplace = True)
             test_data.drop(["Track_1"],axis=1,inplace=True)
             test_data.drop(["Track_2"],axis=1,inplace=True)
             test_data.drop(test_data.index[test_data['VX_FIT']<acceptance], inplace = True)
             test_data.drop(["VX_FIT"],axis=1,inplace=True)
             CurrentRecVertices=len(test_data.axes[0])
             TotalRecVertices+=CurrentRecVertices
             test_data=pd.merge(test_data, eval_data, how="inner", on=["Seed_ID"])
             RemainingRecVertices=len(test_data.axes[0])
             MatchedVertices+=RemainingRecVertices
             FakeVertices+=(CurrentRecVertices-RemainingRecVertices)
Recall=round((float(MatchedVertices)/float(TotalMCVertices))*100,2)
Precision=round((float(MatchedVertices)/float(TotalRecVertices))*100,2)
print(UF.TimeStamp(), bcolors.OKGREEN+'Evaluation has been finished'+bcolors.ENDC)

print(bcolors.HEADER+"#########################################  Results  #########################################"+bcolors.ENDC)
print('Total 2-track combinations are expected according to Monte Carlo:',TotalMCVertices)
print('Total 2-track combinations were reconstructed by EDER-VIANN:',TotalRecVertices)
print('EDER-VIANN correct combinations were reconstructed:',MatchedVertices)
print('Therefore the recall of the current model is',bcolors.BOLD+str(Recall), '%'+bcolors.ENDC)
print('And the precision of the current model is',bcolors.BOLD+str(Precision), '%'+bcolors.ENDC)

#End of the script



