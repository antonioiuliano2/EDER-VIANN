#This simple script prepares data for CNN

########################################    Import libraries    #############################################
import csv
import argparse
import math
import ast
import numpy as np

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
parser.add_argument('--Res',help="Please enter the scaling resolution in microns", default='1000')
parser.add_argument('--Seed',help="Please select the seed", default='0')
parser.add_argument('--Title',help="Plot title", default='Untitled')
parser.add_argument('--MarkSize',help="Marker size", default='20')
parser.add_argument('--PlotType',help="Enter plot type: XZ/YZ/3D", default='3D')
parser.add_argument('--Fill',help="Fill the plot?", default='1')
parser.add_argument('--f',help="Please enter the input file location", default='/eos/experiment/ship/data/EDER-VIANN/TRAIN_SET/CNN_TRAIN_IMAGES_1.csv')
########################################     Main body functions    #########################################
args = parser.parse_args()
MS=int(args.MarkSize)
flocation=args.f
SeedNo=int(args.Seed)
resolution=float(args.Res)

#MaxX=10000.0
#MaxY=10000.0
#MaxZ=20000.0

MaxX=20000.0
MaxY=20000.0
MaxZ=50000.0

boundsX=int(round(MaxX/resolution,0))
boundsY=int(round(MaxY/resolution,0))
boundsZ=int(round(MaxZ/resolution,0))
H=(boundsX)*2
W=(boundsY)*2
L=boundsZ
FillFactor=args.Fill

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
print(bcolors.HEADER+"#########################  Initialising EDER-VIANN image visualisation module  #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading data from ',bcolors.OKBLUE+flocation+bcolors.ENDC)
#Locate mothers
data=UF.LoadImage(flocation,SeedNo)
if data==[]:
    print(UF.TimeStamp(), bcolors.FAIL+"Invalid Seed number"+bcolors.ENDC)
    exit()
print(UF.TimeStamp(), bcolors.OKGREEN+"Data has been loaded successfully..."+bcolors.ENDC)
if FillFactor=='Y':
  print(UF.TimeStamp(),'Enriching data')

  additional_data=[]
  additional_data=UF.EnrichImage(resolution, data)
#  additional_data=UF.PhiRotateImage(additional_data)
  additional_data=UF.ChangeImageResoluion(resolution,additional_data)
#data=UF.PhiRotateImage(data)
data=UF.ChangeImageResoluion(resolution, data)
if args.PlotType=='3D':
 X=[]
 Y=[]
 Z=[]
 for Tracks in data[4]:
      for Hits in Tracks:
          X.append(Hits[0])
          Y.append(Hits[1])
          Z.append(Hits[2])
 if FillFactor=='Y':
     for Tracks in additional_data[4]:
      for Hits in Tracks:
          X.append(Hits[0])
          Y.append(Hits[1])
          Z.append(Hits[2])
if args.PlotType=='XZ':
 InitialData=[]
 Index=-1
 for x in range(-boundsX,boundsX):
          for z in range(0,boundsZ):
            InitialData.append(0.1)

 Matrix = np.array(InitialData)
 Matrix=np.reshape(Matrix,(H,L))
 for Tracks in data[4]:
           for Hits in Tracks:
                if abs(Hits[0])<boundsX and abs(Hits[2])<boundsZ:
                   Matrix[Hits[0]+boundsX][Hits[2]]=0.99
        #           Matrix[Hits[0]][Hits[2]]=0.99
 if FillFactor=='Y':
     for Tracks in additional_data[4]:
      for Hits in Tracks:
        if abs(Hits[0])<boundsX and abs(Hits[2])<boundsZ:
          Matrix[Hits[0]+boundsX][Hits[2]]=0.99
         #  Matrix[Hits[0]][Hits[2]]=0.99
if args.PlotType=='YZ':
 InitialData=[]
 Index=-1
 for y in range(-boundsY,boundsY):
          for z in range(0,boundsZ):
            InitialData.append(0.1)

 Matrix = np.array(InitialData)
 Matrix=np.reshape(Matrix,(W,L))
 for Tracks in data[4]:
         for Hits in Tracks:
                 if abs(Hits[1])<boundsY and abs(Hits[2])<boundsZ:
                   Matrix[Hits[1]+boundsY][Hits[2]]=0.99
            #    Matrix[Hits[1]][Hits[2]]=0.99
 if FillFactor=='Y':
     for Tracks in additional_data[4]:
      for Hits in Tracks:
         if abs(Hits[1])<boundsY and abs(Hits[2])<boundsZ:
          Matrix[Hits[1]+boundsY][Hits[2]]=0.99
        #  Matrix[Hits[1]][Hits[2]]=0.99
if args.PlotType=='XY':
 InitialData=[]
 Index=-1
 for x in range(-boundsX,boundsX):
          for y in range(-boundsY,boundsY):
            InitialData.append(0.1)


 Matrix = np.array(InitialData)
 Matrix=np.reshape(Matrix,(H,W))
 for Tracks in data[4]:
     for Hits in Tracks:
       if abs(Hits[0])<boundsX and abs(Hits[1])<boundsY:
         Matrix[Hits[0]+boundsX][Hits[1]+boundsY]=0.99
       #  Matrix[Hits[0]][Hits[1]]=0.99
 if FillFactor=='Y':
     for Tracks in additional_data[4]:
      for Hits in Tracks:
         if abs(Hits[0])<boundsX and abs(Hits[1])<boundsY:
          Matrix[Hits[0]+boundsX][Hits[1]+boundsY]=0.99
         #  Matrix[Hits[0]][Hits[1]]=0.99
import matplotlib as plt
if args.PlotType=='3D':
 from mpl_toolkits import mplot3d
 import numpy as np
 from mpl_toolkits.mplot3d import axes3d
 import matplotlib.pyplot as plt
 fig = plt.figure()
 ax = plt.axes(projection="3d")# Data for a three-dimensional line
 ax.set_xlabel('Z [microns /'+str(int(resolution))+']')
 ax.set_ylabel('X [microns /'+str(int(resolution))+']')
 ax.set_zlabel('Y [microns /'+str(int(resolution))+']')
 ax.scatter3D(Z, X, Y,s=MS,zdir='z', c='r',marker='s');
 plt.title(args.Title)
 plt.ylim(-boundsX,boundsX)
 plt.xlim(0,boundsZ)
 ax.set_zlim(-boundsY,boundsY)
 plt.show()
if args.PlotType=='XZ':
 import numpy as np
 from matplotlib import pyplot as plt
 plt.title(args.Title)
 plt.xlabel('Z [microns /'+str(int(resolution))+']')
 plt.ylabel('X [microns /'+str(int(resolution))+']')
 image=plt.imshow(Matrix,cmap='gray_r',extent=[0,boundsZ,-boundsX,boundsX])
 plt.show()
if args.PlotType=='YZ':
 import numpy as np
 from matplotlib import pyplot as plt
 plt.title(args.Title)
 plt.xlabel('Z [microns /'+str(int(resolution))+']')
 plt.ylabel('Y [microns /'+str(int(resolution))+']')
 image=plt.imshow(Matrix,cmap='gray_r',extent=[0,boundsZ,-boundsY,boundsY])
 plt.show()
if args.PlotType=='XY':
 import numpy as np
 from matplotlib import pyplot as plt
 plt.title(args.Title)
 plt.xlabel('X [microns /'+str(int(resolution))+']')
 plt.ylabel('Y [microns /'+str(int(resolution))+']')
 image=plt.imshow(Matrix,cmap='gray_r',extent=[-boundsX,boundsX,-boundsY,boundsY])
 plt.show()
exit()




