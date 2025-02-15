#This simple script prepares 2-Track seeds for the initial CNN vertexing
# Part of EDER-VIANN package
#Made by Filips Fedotovs
#Current version 1.0

########################################    Import libraries    #############################################
import csv
import argparse
import pandas as pd #We use Panda for a routine data processing
from pandas import DataFrame as df
import math #We use it for data manipulation
import os, psutil #helps to monitor the memory
import gc  #Helps to clear memory
import numpy as np

#Setting the parser - this script is usually not run directly, but is used by a Master version Counterpart that passes the required arguments
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--PlateZ',help="The Z coordinate of the starting plate", default='-36820.0')
parser.add_argument('--Set',help="Set number", default='1')
parser.add_argument('--Subset',help="Subset number", default='1')
parser.add_argument('--SI_7',help="Separation Interval Point", default='4000')
parser.add_argument('--EOS',help="EOS directory location", default='.')
parser.add_argument('--AFS',help="AFS directory location", default='.')
parser.add_argument('--MaxTracks',help="A maximum number of track combinations that will be used in a particular HTCondor job for this script", default='20000')
######################################## Set variables  #############################################################
args = parser.parse_args()
PlateZ=float(args.PlateZ)   #The coordinate of the st plate in the current scope
Set=args.Set    #This is just used to name the output file
Subset=int(args.Subset)  #The subset helps to determine what portion of the track list is used to create the Seeds
SI_7=float(args.SI_7)
########################################     Preset framework parameters    #########################################
MaxRecords=10000000 #A set parameter that helps to manage memory load of this script (Please do not exceed 10000000)
MaxTracks=int(args.MaxTracks)

#Loading Directory locations
EOS_DIR=args.EOS
AFS_DIR=args.AFS

#import sys
#sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF #This is where we keep routine utility functions

#Specifying the full path to input/output files
input_file_location=EOS_DIR+'/EDER-VIANN/Data/REC_SET/R1_TRACKS.csv'
output_file_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/E5_E5_RawSeeds_'+Set+'_'+str(Subset)+'.csv'
output_result_location=EOS_DIR+'/EDER-VIANN/Data/TEST_SET/E5_E5_RawSeeds_'+Set+'_'+str(Subset)+'_RES.csv'
print(UF.TimeStamp(), "Modules Have been imported successfully...")
print(UF.TimeStamp(),'Loading pre-selected data from ',input_file_location)
data=pd.read_csv(input_file_location)



print(UF.TimeStamp(),'Creating seeds... ')
data_header = data.groupby('Track_ID')['z'].min()  #Keeping only starting hits for the each track record (we do not require the full information about track in this script)
data_header=data_header.reset_index()
#Doing a plate region cut for the Main Data
data_header.drop(data_header.index[data_header['z'] > (PlateZ+SI_7)], inplace = True)
data_header.drop(data_header.index[data_header['z'] < PlateZ], inplace = True)
Records=len(data_header.axes[0])
print(UF.TimeStamp(),'There are total of ', Records, 'tracks in the data set')

Cut=math.ceil(MaxRecords/Records) #Even if use only a max of 20000 track on the right join we cannot perform the full outer join due to the memory limitations, we do it in a small 'cuts'
Steps=math.ceil(MaxTracks/Cut)  #Calculating number of cuts
data=pd.merge(data, data_header, how="inner", on=["Track_ID","z"]) #Shrinking the Track data so just a star hit for each track is present.

#What section of data will we cut?
StartDataCut=(Subset-1)*MaxTracks
EndDataCut=Subset*MaxTracks

#Specifying the right join
r_data=data.rename(columns={"x": "r_x"})
r_data.drop(r_data.index[r_data['z'] != PlateZ], inplace = True)
Records=len(r_data.axes[0])
print(UF.TimeStamp(),'There are  ', Records, 'tracks in the starting plate')
r_data=r_data.iloc[StartDataCut:min(EndDataCut,Records)]
Records=len(r_data.axes[0])
print(UF.TimeStamp(),'However we will only attempt  ', Records, 'tracks in the starting plate')
r_data=r_data.rename(columns={"y": "r_y"})
r_data=r_data.rename(columns={"z": "r_z"})
r_data=r_data.rename(columns={"Track_ID": "Track_2"})
data=data.rename(columns={"Track_ID": "Track_1"})
data['join_key'] = 'join_key'
r_data['join_key'] = 'join_key'

result_list=[]  #We will keep the result in list rather then Panda Dataframe to save memory

#Downcasting Panda Data frame data types in order to save memory
data["x"] = pd.to_numeric(data["x"],downcast='float')
data["y"] = pd.to_numeric(data["y"],downcast='float')
data["z"] = pd.to_numeric(data["z"],downcast='float')
r_data["r_x"] = pd.to_numeric(r_data["r_x"],downcast='float')
r_data["r_y"] = pd.to_numeric(r_data["r_y"],downcast='float')
r_data["r_z"] = pd.to_numeric(r_data["r_z"],downcast='float')

#Cleaning memory
del data_header
gc.collect()

#Creating csv file for the results
UF.LogOperations(output_file_location,'StartLog',result_list)

#This is where we start
for i in range(0,Steps):
  r_temp_data=r_data.iloc[0:min(Cut,len(r_data.axes[0]))] #Taking a small slice of the data
  r_data.drop(r_data.index[0:min(Cut,len(r_data.axes[0]))],inplace=True) #Shrinking the right join dataframe
  merged_data=pd.merge(data, r_temp_data, how="inner", on=['join_key']) #Merging Tracks to check whether they could form a seed
  merged_data['separation']=np.sqrt(((merged_data['x']-merged_data['r_x'])**2)+((merged_data['y']-merged_data['r_y'])**2)+((merged_data['z']-merged_data['r_z'])**2)) #Calculating the Euclidean distance between Track start hits
  merged_data.drop(['y','z','x','r_x','r_y','r_z','join_key'],axis=1,inplace=True) #Removing the information that we don't need anymore
  merged_data.drop(merged_data.index[merged_data['separation'] > SI_7], inplace = True) #Dropping the Seeds that are too far apart
  merged_data.drop(['separation'],axis=1,inplace=True) #We don't need thius field anymore
  merged_data.drop(merged_data.index[merged_data['Track_1'] == merged_data['Track_2']], inplace = True) #Removing the cases where Seed tracks are the same
  merged_list = merged_data.values.tolist() #Convirting the result to List data type
  result_list+=merged_list #Adding the result to the list
  if len(result_list)>=2000000: #Once the list gets too big we dump the results into csv to save memory
      progress=round((float(i)/float(Steps))*100,2)
      print(UF.TimeStamp(),"progress is ",progress,' %') #Progress display
      UF.LogOperations(output_file_location,'UpdateLog',result_list) #Write to the csv
      #Clearing the memory
      del result_list
      result_list=[]
      gc.collect()
      print(UF.TimeStamp(),'Memory usage is',psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

UF.LogOperations(output_file_location,'UpdateLog',result_list) #Writing the remaining data into the csv
UF.LogOperations(output_result_location,'StartLog',[])
print(UF.TimeStamp(), "Fake seed generation is finished...")
#End of the script



