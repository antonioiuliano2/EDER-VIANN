#This simple script prepares raw data for train/validation image creation

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
parser.add_argument('--f',help="Please enter the full path to the file that you want to use as preparation dna", default='/eos/user/a/aiuliano/public/sims_fedra/CH1_pot_03_02_20/b000001/b000001_withtracks_safety_backup.csv')
parser.add_argument('--XminTest',help="Please enter the minX for test data", default='60000')
parser.add_argument('--XmaxTest',help="Please enter the maxX for test data", default='70000')
parser.add_argument('--YminTest',help="Please enter the minY for test data", default='60000')
parser.add_argument('--YmaxTest',help="Please enter the maxY for test data", default='70000')

parser.add_argument('--do',help="Please enter the full path to the file that you want to use as preparation dna", default='/eos/experiment/ship/data/EDER-VIANN/TEST_SET/CNN_TEST_SET.csv')

parser.add_argument('--XminVal',help="Please enter the minX for validation data", default='70000')
parser.add_argument('--XmaxVal',help="Please enter the maxX for validation data", default='70500')
parser.add_argument('--YminVal',help="Please enter the minY for validation data", default='20000')
parser.add_argument('--YmaxVal',help="Please enter the maxY for validation data", default='20500')

parser.add_argument('--vo',help="Please enter the full path to the file that you want to use as preparation dna", default='/eos/experiment/ship/data/EDER-VIANN/VALIDATION_SET/CNN_VALIDATION_SET.csv')

parser.add_argument('--XminTrain',help="Please enter the minX for train data", default='20000')
parser.add_argument('--XmaxTrain',help="Please enter the maxX for train data", default='21000')
parser.add_argument('--YminTrain',help="Please enter the minY for train data", default='70000')
parser.add_argument('--YmaxTrain',help="Please enter the maxY for train data", default='71000')

parser.add_argument('--to',help="Please enter the full path to the file that you want to use as preparation dna", default='/eos/experiment/ship/data/EDER-VIANN/TRAIN_SET/CNN_TRAIN_SET.csv')

########################################     Main body functions    #########################################
args = parser.parse_args()
flocation=args.f
odlocation=args.do
ovlocation=args.vo
otlocation=args.to
XminTest=float(args.XminTest)
XmaxTest=float(args.XmaxTest)
YminTest=float(args.YminTest)
YmaxTest=float(args.YmaxTest)

XminVal=float(args.XminVal)
XmaxVal=float(args.XmaxVal)
YminVal=float(args.YminVal)
YmaxVal=float(args.YmaxVal)

XminTrain=float(args.XminTrain)
XmaxTrain=float(args.XmaxTrain)
YminTrain=float(args.YminTrain)
YmaxTrain=float(args.YmaxTrain)

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
print bcolors.HEADER+"########################################################################################################"+bcolors.ENDC
print bcolors.HEADER+"#########################  Initialising EDER-VIANN raw data preparation module #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC
print bcolors.HEADER+"########################################################################################################"+bcolors.ENDC
print UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC
#fetching_test_data
used_events=[]
data_events=[]
with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          for row in csv_read:
           if row[0]!='ID':
              if float(row[2])>=XminTest and float(row[2])<XmaxTest:
                  if float(row[3])>=YminTest and float(row[3])<YmaxTest:
                      if (row[7] in used_events)==False:
                          used_events.append(row[7])
                          data_events.append(row[7])
csv_read_file.close()



with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data=[]
          HEADER=[]
          HEADER.append('ID_TRACK')
          HEADER.append('TEST_MOTHER')
          HEADER.append('X')
          HEADER.append('Y')
          HEADER.append('Z')
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
                      data.append(datarow)
                      datarow=[]
csv_read_file.close()

csv_write=open(odlocation,"w")
writer = csv.writer(csv_write)
for d in data:
    writer.writerow(d)
csv_write.close()
print UF.TimeStamp(), bcolors.OKGREEN+"Test data has been created successfully..."+bcolors.ENDC

#fetching_validation_data
val_events=[]
with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          for row in csv_read:
           if row[0]!='ID':
              if float(row[2])>=XminVal and float(row[2])<XmaxVal:
                  if float(row[3])>=YminVal and float(row[3])<YmaxVal:
                      if (row[7] in used_events)==False:
                          used_events.append(row[7])
                          val_events.append(row[7])
csv_read_file.close()

with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data=[]
          HEADER=[]
          HEADER.append('ID_TRACK')
          HEADER.append('TEST_MOTHER')
          HEADER.append('X')
          HEADER.append('Y')
          HEADER.append('Z')
          data.append(HEADER)
          for row in csv_read:
           datarow=[]
           if row[0]!='ID':
             if (row[7] in val_events)==True:
                      datarow.append(row[7]+'-'+row[8])
                      if row[10]=='-1':
                        datarow.append('P')
                      else:
                        datarow.append(row[7]+'-'+row[10])
                      datarow.append(row[2])
                      datarow.append(row[3])
                      datarow.append(row[4])
                      data.append(datarow)
                      datarow=[]
csv_read_file.close()

csv_write=open(ovlocation,"w")
writer = csv.writer(csv_write)
for d in data:
    writer.writerow(d)
csv_write.close()

print UF.TimeStamp(), bcolors.OKGREEN+"Validation data has been created successfully..."+bcolors.ENDC
#fetching_training_data
train_events=[]
with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          for row in csv_read:
           if row[0]!='ID':
              if float(row[2])>=XminTrain and float(row[2])<XmaxTrain:
                  if float(row[3])>=YminTrain and float(row[3])<YmaxTrain:
                      if (row[7] in used_events)==False:
                          used_events.append(row[7])
                          train_events.append(row[7])
csv_read_file.close()

with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data=[]
          HEADER=[]
          HEADER.append('ID_TRACK')
          HEADER.append('TEST_MOTHER')
          HEADER.append('X')
          HEADER.append('Y')
          HEADER.append('Z')
          data.append(HEADER)
          for row in csv_read:
           datarow=[]
           if row[0]!='ID':
             if (row[7] in train_events)==True:
                      datarow.append(row[7]+'-'+row[8])
                      if row[10]=='-1':
                        datarow.append('P')
                      else:
                        datarow.append(row[7]+'-'+row[10])
                      datarow.append(row[2])
                      datarow.append(row[3])
                      datarow.append(row[4])
                      data.append(datarow)
                      datarow=[]
csv_read_file.close()

csv_write=open(otlocation,"w")
writer = csv.writer(csv_write)
for d in data:
    writer.writerow(d)
csv_write.close()
print UF.TimeStamp(), bcolors.OKGREEN+"Train data has been created successfully..."+bcolors.ENDC
print UF.TimeStamp(), bcolors.OKGREEN+"Data preparation has finished successfully..."+bcolors.ENDC
exit()
