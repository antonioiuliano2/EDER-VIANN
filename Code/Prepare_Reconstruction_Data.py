#This simple script prepares the reconstruction data for vertexing procedure

########################################    Import libraries    #############################################
import csv
import argparse
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
parser.add_argument('--f',help="Please enter the full path to the file with track reconstruction", default='/eos/user/a/aiuliano/public/sims_fedra/CH1_pot_03_02_20/b000001/b000001_withvertices.csv')
parser.add_argument('--Track',help="Which tracks to use FEDRA/MC (For actual vertexing the track designations used by FEDRA should be used", default='FEDRA')
parser.add_argument('--Xmin',help="Please enter the minX for data", default='0')
parser.add_argument('--Xmax',help="Please enter the maxX for data", default='0')
parser.add_argument('--Ymin',help="Please enter the minY for data", default='0')
parser.add_argument('--Ymax',help="Please enter the maxY for data", default='0')

########################################     Main body functions    #########################################
args = parser.parse_args()
flocation=args.f
DataSetNo=args.DataSet
Track=args.Track
Xmin=float(args.Xmin)
Xmax=float(args.Xmax)
Ymin=float(args.Ymin)
Ymax=float(args.Ymax)

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
print(bcolors.HEADER+"####################  Initialising EDER-VIANN reconstruction data preparation module ###################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
#fetching_test_data
data_header=[]
with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data_header=list(csv_read)[0]
          #for row in csv_read:
        #   if row[0]!='ID':
        #      if float(row[2])>=Xmin and float(row[2])<Xmax:
        #          if float(row[3])>=Ymin and float(row[3])<Ymax:
         #             if (row[7] in used_events)==False:
       #                   used_events.append(row[7])
        #                  data_events.append(row[7])
csv_read_file.close()
print(data_header)
exit()

with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data=[]
          HEADER=[]
          HEADER.append('ID_TRACK')
          HEADER.append('TEST_MOTHER')
          HEADER.append('X')
          HEADER.append('Y')
          HEADER.append('Z')
          HEADER.append('TEST_FEDRA_TRK')
          HEADER.append('TEST_FEDRA_VXS')
          HEADER.append('TEST_FEDRA_VXE')
          HEADER.append('TEST_PROC_ID')
          HEADER.append('TEST_Px')
          HEADER.append('TEST_Py')
          HEADER.append('TEST_Pz')
          data.append(HEADER)
          for row in csv_read:
           datarow=[]
           if row[0]!='ID':
             if (row[7] in data_events)==True:
                      datarow.append(row[7]+'-'+row[8])
                      if row[10]=='-1':
                        datarow.append('P')
                      else:
                        datarow.append(row[7]+'-'+row[10])
                      datarow.append(row[2])
                      datarow.append(row[3])
                      datarow.append(row[4])
                      datarow.append(row[19])
                      datarow.append(row[21])
                      datarow.append(row[22])
                      datarow.append(row[11])
                      datarow.append(row[16])
                      datarow.append(row[17])
                      datarow.append(row[18])
                      data.append(datarow)
                      datarow=[]
csv_read_file.close()
if DataSetNo=='0':
   SavedData='/eos/experiment/ship/data/EDER-VIANN/TEST_SET/CNN_TEST_SET.csv'
   UF.LogOperations(SavedData,'StartLog',data)
else:
   SavedData='/eos/experiment/ship/data/EDER-VIANN/RAW_DATA_SET/CNN_DATA_SET_'+DataSetNo+'.csv'
   UF.LogOperations(SavedData,'StartLog',data)
print(UF.TimeStamp(), bcolors.OKGREEN+"Test data has been created successfully..."+bcolors.ENDC)
exit()
