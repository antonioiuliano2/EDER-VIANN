#This simple script prepares the reconstruction data for vertexing procedure

########################################    Import libraries    #############################################
import csv
import argparse
import pandas as pd
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
parser.add_argument('--f',help="Please enter the full path to the file with track reconstruction", default='/eos/user/a/aiuliano/public/sims_fedra/CH1_pot_03_02_20/b000001/b000001_withtracks.csv')
parser.add_argument('--Track',help="Which tracks to use FEDRA/MC (For actual vertexing the track designations used by FEDRA should be used", default='FEDRA')

########################################     Main body functions    #########################################
args = parser.parse_args()
flocation=args.f
Track=args.Track

#Loading Directory locations
csv_reader=open('../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()
out_file=EOS_DIR+'/EDER-VIANN/Data/REC_SET/REC_SET.csv'
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"####################  Initialising EDER-VIANN reconstruction data preparation module ###################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
#fetching_test_data
print(UF.TimeStamp(),'Loading raw data...')
if Track=='FEDRA':
 data=pd.read_csv(flocation,
            header=0,
            usecols=['FEDRATrackID','quarter','x','y','z'])
 total_rows=len(data.axes[0])
 print(UF.TimeStamp(),'The raw data has ',total_rows,' hits')
 print(UF.TimeStamp(),'Removing unreconstructed hits...')
 data=data.dropna()
 final_rows=len(data.axes[0])
 print(UF.TimeStamp(),'The cleaned data has ',final_rows,' hits')
 data['FEDRATrackID'] = data['FEDRATrackID'].astype(int)
 data['FEDRATrackID'] = data['FEDRATrackID'].astype(str)
 data['quarter'] = data['quarter'].astype(int)
 data['quarter'] = data['quarter'].astype(str)
 data['Track_ID'] = data['quarter'] + '-' + data['FEDRATrackID']
 data=data.drop(['FEDRATrackID'],axis=1)
 data=data.drop(['quarter'],axis=1)

else:
 data=pd.read_csv(flocation,
            header=0,
            usecols=['MCEvent','MCTrack','x', 'y','z'])
 total_rows=len(data.axes[0])
 print(UF.TimeStamp(),'The raw data has ',total_rows,' hits')
 print(UF.TimeStamp(),'Removing unreconstructed hits...')
 data=data.dropna()
 final_rows=len(data.axes[0])
 print(UF.TimeStamp(),'The cleaned data has ',final_rows,' hits')
 data['MCTrack'] = data['MCTrack'].astype(int)
 data['MCTrack'] = data['MCTrack'].astype(str)
 data['MCEvent'] = data['MCEvent'].astype(int)
 data['MCEvent'] = data['MCEvent'].astype(str)
 data['Track_ID'] = data['MCEvent'] + '-' + data['MCTrack']
 data=data.drop(['MCTrack'],axis=1)
 data=data.drop(['MCEvent'],axis=1)
print(UF.TimeStamp(),'Removing 1 hit tracks...')
track_no_data=data.groupby(['Track_ID'],as_index=False).count()
track_no_data=track_no_data.drop(['y','z'],axis=1)
track_no_data=track_no_data.rename(columns={"x": "Track_No"})
new_combined_data=pd.merge(data, track_no_data, how="left", on=["Track_ID"])
new_combined_data = new_combined_data[new_combined_data.Track_No >= 2]
new_combined_data = new_combined_data.drop(['Track_No'],axis=1)
new_combined_data=new_combined_data.sort_values(['Track_ID','z'],ascending=[1,1])
grand_final_rows=len(new_combined_data.axes[0])
print(UF.TimeStamp(),'The cleaned data has ',grand_final_rows,' hits')
new_combined_data.to_csv(out_file,index=False)
print(UF.TimeStamp(), bcolors.OKGREEN+"Test data has been created successfully..."+bcolors.ENDC)
exit()
