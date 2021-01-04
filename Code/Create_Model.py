#This simple script prepares data for CNN

########################################    Import libraries    #############################################
import csv
import argparse
import math
import ast
import numpy as np
import tensorflow as tf
import copy
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv3D, MaxPooling3D, Dropout, BatchNormalization

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
parser.add_argument('--Mode',help="Please enter the mode: Production/Test/Evolution", default='Test')
parser.add_argument('--ImageSet',help="Please enter the image set", default='1')
########################################     Main body functions    #########################################
args = parser.parse_args()
ImageSet=args.ImageSet
resolution=float(args.RES)
MaxX=10000.0
MaxY=10000.0
MaxZ=50000.0
boundsX=int(round(MaxX/resolution,0))
boundsY=int(round(MaxY/resolution,0))
boundsZ=int(round(MaxZ/resolution,0))
Schema=args.ClassSchema
H=boundsX*2
W=boundsY*2
L=boundsZ

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
import Utility_Functions as UF

flocation=EOS_DIR+'/Data/TRAIN_SET/'+'CNN_TRAIN_IMAGES_'+ImageSet+'.csv'
vlocation=EOS_DIR+'/Data/VALIDATION_SET/'+'CNN_VALIDATION_IMAGES_'+ImageSet+'.csv'

print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################  Initialising EDER-VIANN image model creation module #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading data from ',bcolors.OKBLUE+flocation+bcolors.ENDC)

exit()

print('Enriching data')
Images=LoadImages(flocation)
ValImages=LoadData(vlocation)
if FillFactor>0:
 print('Enriching data')
 additional_data=[]
 additional_data=EnrichPlot(resolution, Images)
 vadditional_data=EnrichPlot(resolution, valdata)
 print('Data is enriched')
print('Changing resolution of the data')
data=ChangeResoluion(resolution, data)
valdata=ChangeResoluion(resolution, valdata)
if FillFactor>0:
  additional_data=ChangeResoluion(resolution, additional_data)
print('Resolution has been changed')
print('Creating data 3-d images...')
TrainX=np.empty([len(data),H,W,L])
TrainY=np.empty([len(data),1])



for DataItems in range(0,len(data)):
    progress=int(round((float(DataItems)/float(len(data)))*100,0))
    print("Progress is ",progress,' %', end="\r", flush=True)
    InitialData=[]
    Index=-1
    if Schema=='B':
      if data[DataItems][3]=='0':
        TrainY[DataItems]=0
      else:
        TrainY[DataItems]=1
    if Schema=='VMN':
        TrainY[DataItems]=int(data[DataItems][3])
    if Schema=='BVMN':
        TrainY[DataItems]=int(2*float(data[DataItems][3]))
    for x in range(-boundsX,boundsX):
      for y in range(-boundsY,boundsY):
          for z in range(0,boundsZ):
            Index+=1
            InitialData.append(0.1)
            for Tracks in data[DataItems][4]:
             for Hits in Tracks:
                if (x == Hits[0]) and (y == Hits[1]) and (z == Hits[2]):
                      InitialData[Index]=0.99
            if FillFactor>0:
             for Tracks in additional_data[DataItems][4]:
              for Hits in Tracks:
                if (x == Hits[0]) and (y == Hits[1]) and (z == Hits[2]):
                      InitialData[Index]=0.99
    Matrix = np.array(InitialData)
    Matrix=np.reshape(Matrix,(H,W,L))
    TrainX[DataItems]=Matrix
TrainX= TrainX[..., np.newaxis]
print(TrainY)
TrainY=tf.keras.utils.to_categorical(TrainY)

TestX=np.empty([len(valdata),H,W,L])
TestY=np.empty([len(valdata),1])

for DataItems in range(0,len(valdata)):
    progress=int(round((float(DataItems)/float(len(valdata)))*100,0))
    print("Progress is ",progress,' %', end="\r", flush=True)
    InitialData=[]
    Index=-1
    if Schema=='B':
      if valdata[DataItems][3]=='0':
        TestY[DataItems]=0
      else:
        TestY[DataItems]=1
    if Schema=='VMN':
        TestY[DataItems]=int(valdata[DataItems][3])
    if Schema=='BVMN':
        TestY[DataItems]=int(2*float(valdata[DataItems][3]))
    for x in range(-boundsX,boundsX):
      for y in range(-boundsY,boundsY):
          for z in range(0,boundsZ):
            Index+=1
            InitialData.append(0.1)
            for Tracks in valdata[DataItems][4]:
             for Hits in Tracks:
                if (x == Hits[0]) and (y == Hits[1]) and (z == Hits[2]):
                      InitialData[Index]=0.99
            if FillFactor>0:
             for Tracks in additional_data[DataItems][4]:
              for Hits in Tracks:
                if (x == Hits[0]) and (y == Hits[1]) and (z == Hits[2]):
                      InitialData[Index]=0.99
    Matrix = np.array(InitialData)
    Matrix=np.reshape(Matrix,(H,W,L))
    TestX[DataItems]=Matrix
TestX= TestX[..., np.newaxis]
ValY=copy.deepcopy(TestY)
TestY=tf.keras.utils.to_categorical(TestY)
model = Sequential()
model.add(Conv3D(32, activation='relu',kernel_size=(3,3,3),kernel_initializer='he_uniform', input_shape=(H,W,L,1)))
model.add(MaxPooling3D(pool_size=(2, 2, 2)))
model.add(BatchNormalization(center=True, scale=True))
model.add(Dropout(0.5))
model.add(Conv3D(64, activation='relu',kernel_size=(3,3,3),kernel_initializer='he_uniform'))
model.add(MaxPooling3D(pool_size=(2, 2, 2)))
model.add(BatchNormalization(center=True, scale=True))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(256, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(256, activation='relu', kernel_initializer='he_uniform'))
model.add(Dense(TrainY.shape[1], activation='softmax'))
# Compile the model
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()
# Fit data to model
history = model.fit(TrainX, TrainY,batch_size=32,epochs=20,verbose=1)
pred = model.predict(TestX)
pred = np.argmax(pred, axis=1)
match=0
for p in range(0,len(pred)):
      if int(ValY[p])==pred[p]:
            match+=1
Accuracy=int(round((float(match)/float(len(pred)))*100,0))
print('Accuracy of the model is',Accuracy,'%')
exit()


