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
parser.add_argument('--Mode',help="Please enter the mode: Production/Test/Evolution/Train", default='Test')
parser.add_argument('--ImageSet',help="Please enter the image set", default='1')
parser.add_argument('--DNA',help="Please enter the model dna", default='[[2, 4, 1, 1, 2, 2, 6], [4, 4, 1, 1, 2, 2, 6], [], [], [], [4, 4], [4, 4],[],[],[], [7,2,1]]')
parser.add_argument('--afs',help="Please enter the user afs directory", default='.')
parser.add_argument('--eos',help="Please enter the user eos directory", default='.')
########################################     Main body functions    #########################################
args = parser.parse_args()
ImageSet=args.ImageSet
resolution=float(args.Res)
Mode=args.Mode
DNA=ast.literal_eval(args.DNA)
HiddenLayerDNA=[]
FullyConnectedDNA=[]
OutputDNA=[]
ValidModel=True
for gene in DNA:
    if len(gene)==7:
        HiddenLayerDNA.append(gene)
    if len(gene)==2:
        FullyConnectedDNA.append(gene)
    if len(gene)==3:
        OutputDNA.append(gene)
act_fun_list=['N/A','linear','exponential','elu','relu', 'selu','sigmoid','softmax','softplus','softsign','tanh']
def GiveBias(Code):
    if Code==1:
        return 'False'
    if Code==2:
        return 'True'
MaxX=20000.0
MaxY=20000.0
MaxZ=50000.0
boundsX=int(round(MaxX/resolution,0))
boundsY=int(round(MaxY/resolution,0))
boundsZ=int(round(MaxZ/resolution,0))
H=boundsX*2
W=boundsY*2
L=boundsZ

#Loading Directory locations
AFS_DIR=args.afs
EOS_DIR=args.eos
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
#Load data configuration
EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
flocation=EOS_DIR+'/EDER-VIANN/Data/TRAIN_SET/'+'CNN_TRAIN_IMAGES_'+ImageSet+'.csv'
vlocation=EOS_DIR+'/EDER-VIANN/Data/VALIDATION_SET/'+'CNN_VALIDATION_IMAGES_1.csv'

print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################  Initialising EDER-VIANN image model creation module #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################              Written by Filips Fedotovs              #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################                 PhD Student at UCL                   #########################"+bcolors.ENDC)
print(bcolors.HEADER+"########################################################################################################"+bcolors.ENDC)
print(UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading data from ',bcolors.OKBLUE+flocation+bcolors.ENDC)
TrainImages=UF.LoadImages(flocation)
print(UF.TimeStamp(), bcolors.OKGREEN+"Train data has been loaded successfully..."+bcolors.ENDC)
print(UF.TimeStamp(),'Loading data from ',bcolors.OKBLUE+vlocation+bcolors.ENDC)
ValidationImages=UF.LoadImages(vlocation)
print(UF.TimeStamp(), bcolors.OKGREEN+"Validation data has been loaded successfully..."+bcolors.ENDC)


##########################################################   Data enrichment (Filling gaps between tracklets)   ##############################
print(UF.TimeStamp(),'Enriching training data...')
additional_train_data=[]
for TI in TrainImages:
  additional_train_data.append(UF.EnrichImage(resolution, TI))
print(UF.TimeStamp(), bcolors.OKGREEN+"Train data has been enriched successfully..."+bcolors.ENDC)

print(UF.TimeStamp(),'Enriching validation data...')
additional_val_data=[]
for VI in ValidationImages:
  additional_val_data.append(UF.EnrichImage(resolution, VI))
print(UF.TimeStamp(), bcolors.OKGREEN+"Validation data has been enriched successfully..."+bcolors.ENDC)


########################################################  Image preparation for rendering   ########################################
print(UF.TimeStamp(),'Rendering train images...')
TrainImagesY=np.empty([len(TrainImages),1])
TrainImagesX=np.empty([len(TrainImages),H,W,L])
for TI in range(0,len(TrainImages)):
    TrainImages[TI]=UF.ChangeImageResoluion(resolution, TrainImages[TI])
    additional_train_data[TI]=UF.ChangeImageResoluion(resolution, additional_train_data[TI])
    progress=int(round((float(TI)/float(len(TrainImages)))*100,0))
    print("Progress is ",progress,' %', end="\r", flush=True)
    TrainImagesY[TI]=int(2*float(TrainImages[TI][3]))
    BlankRenderedTrainImage=[]
    for x in range(-boundsX,boundsX):
          for y in range(-boundsY,boundsY):
            for z in range(0,boundsZ):
             BlankRenderedTrainImage.append(0.1)
    RenderedTrainImage = np.array(BlankRenderedTrainImage)
    RenderedTrainImage = np.reshape(RenderedTrainImage,(H,W,L))
    for Tracks in TrainImages[TI][4]:
     for Hits in Tracks:
         if abs(Hits[0])<boundsX and abs(Hits[1])<boundsX and abs(Hits[2])<boundsZ:
             RenderedTrainImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=0.99
    for Tracks in additional_train_data[TI][4]:
     for Hits in Tracks:
       if abs(Hits[0])<boundsX and abs(Hits[1])<boundsX and abs(Hits[2])<boundsZ:
         RenderedTrainImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=0.99
    TrainImagesX[TI]=RenderedTrainImage
TrainImagesX= TrainImagesX[..., np.newaxis]
TrainImagesY=tf.keras.utils.to_categorical(TrainImagesY)
print(UF.TimeStamp(), bcolors.OKGREEN+"Train images have been rendered successfully..."+bcolors.ENDC)

print(UF.TimeStamp(),'Loading the model...')
##### This but has to be converted to a part that interprets DNA code  ###################################
if Mode!='Train':
 try:
  model = Sequential()
  for HL in HiddenLayerDNA:
    Nodes=HL[0]*16
    KS=(HL[2]*2)+1
    PS=HL[3]+1
    DR=float(HL[6]-1)/10.0
    if HiddenLayerDNA.index(HL)==0:
      model.add(Conv3D(Nodes, activation=act_fun_list[HL[1]],kernel_size=(KS,KS,KS),kernel_initializer='he_uniform', input_shape=(H,W,L,1)))
    else:
      model.add(Conv3D(Nodes, activation=act_fun_list[HL[1]],kernel_size=(KS,KS,KS),kernel_initializer='he_uniform'))
    model.add(MaxPooling3D(pool_size=(PS, PS, PS)))
    model.add(BatchNormalization(center=GiveBias(HL[4]), scale=GiveBias(HL[5])))
    model.add(Dropout(DR))
  model.add(Flatten())
  for FC in FullyConnectedDNA:
    Nodes=4**FC[0]
    model.add(Dense(Nodes, activation=act_fun_list[FC[1]], kernel_initializer='he_uniform'))
  model.add(Dense(TrainImagesY.shape[1], activation=act_fun_list[OutputDNA[0][0]]))
 # Compile the model
  model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
  model.summary()
 except:
    print(UF.TimeStamp(), bcolors.FAIL+"Invalid model..."+bcolors.ENDC)
    ValidModel=False
######################### Model Creation section ########################################################################################
if Mode=='Train':
   model_name=EOSsubModelDIR+'/'+'model'
   model=tf.keras.models.load_model(model_name)
   model.summary()
###################################################################################################
Accuracy=-1.0
if ValidModel==True:
 print(UF.TimeStamp(),'Training the model...')
 # Fit data to model
 history = model.fit(TrainImagesX, TrainImagesY,batch_size=(OutputDNA[0][1]*16),epochs=(OutputDNA[0][2]*20),verbose=1)

########################################################  Image preparation for rendering   ########################################
 print(UF.TimeStamp(),'Rendering validation images...')
 ValImagesY=[]
 ValImagesX=np.empty([len(ValidationImages),H,W,L])
 for VI in range(0,len(ValidationImages)):
    ValidationImages[VI]=UF.ChangeImageResoluion(resolution, ValidationImages[VI])
    additional_val_data[VI]=UF.ChangeImageResoluion(resolution, additional_val_data[VI])
    progress=int(round((float(VI)/float(len(ValidationImages)))*100,0))
    print("Progress is ",progress,' %', end="\r", flush=True)
    ValImagesY.append(int(2*float(ValidationImages[VI][3])))
    BlankRenderedValImage=[]
    for x in range(-boundsX,boundsX):
          for y in range(-boundsY,boundsY):
            for z in range(0,boundsZ):
             BlankRenderedValImage.append(0.1)
    RenderedValImage = np.array(BlankRenderedValImage)
    RenderedValImage = np.reshape(RenderedValImage,(H,W,L))
    for Tracks in ValidationImages[VI][4]:
     for Hits in Tracks:
         if abs(Hits[0])<boundsX and abs(Hits[1])<boundsX and abs(Hits[2])<boundsZ:
             RenderedValImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=0.99
    for Tracks in additional_val_data[VI][4]:
     for Hits in Tracks:
       if abs(Hits[0])<boundsX and abs(Hits[1])<boundsX and abs(Hits[2])<boundsZ:
         RenderedValImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=0.99
    ValImagesX[VI]=RenderedValImage
 ValImagesX= ValImagesX[..., np.newaxis]
 print(UF.TimeStamp(), bcolors.OKGREEN+"Validation images have been rendered successfully..."+bcolors.ENDC)

 print(UF.TimeStamp(),'Validating the model...')
 pred = model.predict(ValImagesX)
 pred = np.argmax(pred, axis=1)
 match=0
 for p in range(0,len(pred)):
      if int(ValImagesY[p])==pred[p]:
            match+=1
 Accuracy=round((float(match)/float(len(pred)))*100,3)

if Mode=='Production' or Mode=='Train':
   if ValidModel==True:
    model_name=EOSsubModelDIR+'/'+'model'
    model.save(model_name)
    print('The model has been saved here:', model_name)
   record=[]
   record.append(ImageSet)
   record.append(len(TrainImagesY))
   record.append(Accuracy)
   csv_writer_err=open(EOSsubModelDIR+'/'+'model_log_'+ImageSet+'.csv',"w")
   err_writer = csv.writer(csv_writer_err)
   err_writer.writerow(record)
   csv_writer_err.close()
   exit()

if Mode=='Evolution':
   record=[]
   csv_writer_err=open(EOSsubEvoModelDIR+'/'+'model_fitness_'+args.DNA+'.csv',"w")
   err_writer = csv.writer(csv_writer_err)
   if Accuracy!=Accuracy:
       Accuracy=0.0
   record.append(Accuracy)
   err_writer.writerow(record)
   csv_writer_err.close()
   print('The model fitness file has been saved as ',EOSsubEvoModelDIR+'/'+'model_fitness_'+args.DNA+'.csv')
   exit()
if Mode=='Test' and ValidModel==True:
 print('Overall accuracy of the model is',Accuracy,'%')
 VertexLengths=[]
 for VR in ValImagesY:
    if (VR in VertexLengths)==False:
          VertexLengths.append(VR)
 for VC in VertexLengths:
   overall_match=0
   hit_match=0
   for VI in range(0,len(ValImagesY)):
     if  int(ValImagesY[VI])==int(VC):
         overall_match+=1
         if int(ValImagesY[VI])==int(pred[VI]):
            hit_match+=1
   Accuracy=round((float(hit_match)/float(overall_match))*100,3)
   print('------------------------------------------------------------------')
   print('The accuracy of the model for',str(float(round((VC/2.0),1))),'-track vertices is',Accuracy,'%')
   exit()
print(UF.TimeStamp(), bcolors.FAIL+"Something went wrong with the model..."+bcolors.ENDC)
exit()


