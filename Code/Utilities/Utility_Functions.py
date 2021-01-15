###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
import math
import os, shutil
import subprocess
import time as t
import datetime
import ast
import numpy as np
#This utility provides Timestamps for print messages
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"

#This utility loads an image data
#It requires the location of the file where images are stored
def LoadImages(location,StartSeed,BatchSize):
    csv_read_file=open(location,"r")
    csv_read = csv.reader(csv_read_file, delimiter=',')
    Images=list(csv_read)
    csv_read_file.close()
    Refined_Images=[]
    for Im in Images:
       Im[4]=ast.literal_eval(Im[4])
       if int(Im[0])>=StartSeed and int(Im[0])<(StartSeed+BatchSize):
           Refined_Images.append(Im)
    return Refined_Images

def GetNImages(location):
    csv_read_file=open(location,"r")
    csv_read = csv.reader(csv_read_file, delimiter=',')
    Images=list(csv_read)
    csv_read_file.close()
    for Im in Images:
       Im[4]=ast.literal_eval(Im[4])
    return len(Images)

def LoadImage(location,SeedNo):
    csv_read_file=open(location,"r")
    csv_read = csv.reader(csv_read_file, delimiter=',')
    Images=list(csv_read)
    csv_read_file.close()
    for Im in Images:
       Im[4]=ast.literal_eval(Im[4])
       if int(Im[0])==SeedNo:
           return Im
    return []
#This utility allows to fill gaps between track hit points in order to make track lines solid
#Resolution requires an integer number which is microns per pixel, Images are the Image data
def EnrichImage(resolution, Image):
     New_image=[[],[],[],[],[]]
     for Tracks in Image[4]:
      New_Track=[]
      for h in range(0,len(Tracks)-1):
        deltaX=float(Tracks[h+1][0])-float(Tracks[h][0])
        deltaZ=float(Tracks[h+1][2])-float(Tracks[h][2])
        deltaY=float(Tracks[h+1][1])-float(Tracks[h][1])
        try:
         ThetaAngle=math.atan(deltaX/deltaZ)
        except:
         ThetaAngle=0.0
        try:
         PhiAngle=math.atan(deltaY/deltaZ)
        except:
         PhiAngle=0.0
        TotalDistance=math.sqrt((deltaX**2)+(deltaY**2)+(deltaZ**2))
        Distance=(TotalDistance/float(resolution*2))
        if Distance>=0 and Distance<1:
            Distance=1.0
        if Distance<0 and Distance>-1:
            Distance=-1.0
        Iterations=int(round(TotalDistance/Distance,0))
        for i in range(1,Iterations):
            New_Hit=[]
            New_Hit.append(float(Tracks[h][0])+float(i)*Distance*math.sin(ThetaAngle))
            New_Hit.append(float(Tracks[h][1])+float(i)*Distance*math.sin(PhiAngle))
            New_Hit.append(float(Tracks[h][2])+float(i)*Distance*math.cos(ThetaAngle))
            New_Track.append(New_Hit)
      New_image[4].append(New_Track)
     return New_image

#This utility changes the resolution of the Images to the required on for CNN
#Resolution requires an integer number which is microns per pixel, Images are the Image data
def ChangeImageResoluion(resolution,Image):
    #sort Mothers:
    for Tracks in Image[4]:
      for Hits in Tracks:
        Hits[0]=int(round(float(Hits[0])/resolution,0))
        Hits[1]=int(round(float(Hits[1])/resolution,0))
        Hits[2]=int(round(float(Hits[2])/resolution,0))
    return Image

def TruncateImage(Image):
    #sort Mothers:
    for Tracks in Image[4]:
      for Hits in Tracks:
        Hits[0]=int(float(Hits[0]))
        Hits[1]=int(float(Hits[1]))
        Hits[2]=int(float(Hits[2]))
    return Image

#This utility checks whether the seed track is already in the image
def CheckSeedOverlap(Image,Seed):
    for Tracks in Image[1]:
        if Tracks==Seed[0]:
            return False
    return True
def CheckTrackOverlap(Track,Tracks):
    for t in Tracks:
        if Track[0]==t[0]:
            return True
    return False
#This utility sorts hits in the Image tracks by z-location
def SortImage(seed):
   for Track in seed[4]:
         Track=sorted(Track,key=lambda x: float(x[2]),reverse=False)
   return seed

#This utility shifts hit coordinates so they all start at z,x,y=0
def ShiftImage(seed):
     minZ=666666.0
     Track_Pos=0
     for Track_No in range(0,len(seed[4])):
         if minZ>float(seed[4][Track_No][0][2]):
             minZ=float(seed[4][Track_No][0][2])
             Track_Pos=Track_No
     FinZ=float(seed[4][Track_Pos][0][2])
     LongestDistance=0.0
     for Track in seed[4]:
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                FinX=float(Track[0][0])
                FinY=float(Track[0][1])
     for Tracks in seed[4]:
      for Hits in Tracks:
        Hits[0]=float(Hits[0])-FinX
        Hits[1]=float(Hits[1])-FinY
        Hits[2]=float(Hits[2])-FinZ
     return seed

#This utility rotates the seed in such a way that its longest track is pointing along the z-direction
def LonRotateImage(seed):
    #Locate the longest track (assumption that it has the highest Pt)
        LongestDistance=0.0
        for Track in seed[4]:
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                MainXdiff=Xdiff
                MainYdiff=Ydiff
                MainZdiff=Zdiff
                StartX=float(Track[0][0])
                StartY=float(Track[0][1])
                StartZ=float(Track[0][2])
                if MainZdiff!=0:
                 ThetaAngle=math.atan(MainYdiff/MainZdiff)
                 PhiAngle=math.atan(MainXdiff/MainZdiff)
                else:
                 ThetaAngle=0.0
                 PhiAngle=0.0
        for Tracks in seed[4]:
            for hits in Tracks:
               YDistance=math.sqrt(((float(hits[1])-StartY)**2)+((float(hits[2])-StartZ)**2))
               Yoffset=YDistance*math.sin(ThetaAngle)
               Zoffset=Yoffset*math.sin(ThetaAngle)
               hits[1]=float(hits[1])-Yoffset
               hits[2]=float(hits[2])+Zoffset
               XDistance=math.sqrt(((float(hits[0])-StartX)**2)+((float(hits[2])-StartZ)**2))
               Xoffset=XDistance*math.sin(PhiAngle)
               ZPhiOffset=Xoffset*math.sin(PhiAngle)
               hits[0]=float(hits[0])-Xoffset
               hits[2]=float(hits[2])+ZPhiOffset
        return seed

#This utility checks the quality of the seed based on the bounds on the starting position of the track
#seed is the image, boundX/Y/Z are the bounds on the position (Might be changed to the absolute distance)
def SeedQualityCheck(seed,MaxOffset):
    for Track in seed[4]:
            EuclidianOffset=math.sqrt(float(Track[0][0])**2+float(Track[0][1])**2+float(Track[0][2])**2)
            if EuclidianOffset>MaxOffset:
                return False
    return True

def Pre2TrackSeedCheck(Track1,Track2,MaxOffset):
    EuclidianOffset=math.sqrt((float(Track1[2])-float(Track2[2]))**2+(float(Track1[3])-float(Track2[3]))**2+(float(Track1[4])-float(Track2[4]))**2)
    if EuclidianOffset>MaxOffset:
       return False
    return True

#This utility rotates the seed in such a way that its second longest track is pointing in the Z-direction and has zero x
def PhiRotateImage(seed):
    #Locate the longest track (assumption that it has the highest Pt)
        PhiAngle=0.0
        LongestDistance=0.0
        for Track in seed[4]:
#            print Track
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                AvoidIndex=seed[4].index(Track)
        LongestDistance=0.0
        for Track in seed[4]:
          if seed[4].index(Track)!=AvoidIndex:
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                X=float(Track[len(Track)-1][0])
                Y=float(Track[len(Track)-1][1])
                Distance=math.sqrt((X**2)+(Y**2))
                vector_1 = [0, Distance]
                vector_2 = [X, Y]
                unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
                unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
                dot_product = np.dot(unit_vector_1, unit_vector_2)
                PhiAngle = np.arccos(dot_product)
                if np.isnan(PhiAngle)==True:
                    PhiAngle=0.0
        for Tracks in seed[4]:
            for hits in Tracks:
               Distance=math.sqrt((float(hits[0])**2)+(float(hits[1])**2))
               vector_1 = [0, Distance]
               vector_2 = [float(hits[0]), float(hits[1])]
               unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
               unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
               dot_product = np.dot(unit_vector_1, unit_vector_2)
               NewPhiAngle = PhiAngle-np.arccos(dot_product)+(math.pi/4)
               if np.isnan(NewPhiAngle)==False:
                hits[0]=Distance*math.cos(NewPhiAngle)
                hits[1]=Distance*math.sin(NewPhiAngle)
        return seed


#Given seed, this function assigns the track hit positions for the seed
def DecorateSeedTracks(seed,data):
    if len(seed)==4:
     seed.append([])
     for track in range(0,len(seed[1])):
          seed[4].append([])
          for d in data:
           if seed[1][track]==d[0]:
            Track_Hit=[]
            for di in range(2,5):
              Track_Hit.append(d[di])
            seed[4][track].append(Track_Hit)
    else:
     for track in range(len(seed[4]+1),len(seed[1])):
          for d in data:
           if seed[1][track]==d[0]:
            Track_Hit=[]
            for di in range(2,5):
              Track_Hit.append(d[di])
            seed[4][track].append(Track_Hit)
    return seed

#Given seed, this function assigns the track hit positions for the seed
def EvaluateTracks(Tracks,data):
        for s in range(0,len(Tracks)):
          progress=int(round((float(s)/float(len(Tracks)))*100,0))
          print("Evaluating the quality of the tracks, progress is ",progress,' %', end="\r", flush=True)
          TrackCount=0
          for d in data:
           if Tracks[s][0]==d[0]:
               TrackCount+=1
           if TrackCount>1:
               Tracks[s].append('GT')
               break
          if TrackCount<2:
              Tracks[s].append('BT')
        return Tracks

def RemoveBadTracks(Tracks,data):
        NewData=[]
        NewData.append(data[0])
        for s in range(0,len(Tracks)):
          progress=int(round((float(s)/float(len(Tracks)))*100,0))
          print("Removing bad tracks from the data, progress is ",progress,' %', end="\r", flush=True)
          for d in data:
           if Tracks[s][0]==d[0]:
              NewData.append(d)
        return NewData

def EvolutionCleanUp(AFS_DIR, EOS_DIR,mode):
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-EVO\""])
      if mode=='Full':
       EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
       EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
       EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
       folder =  EOSsubEvoDIR
       for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

       folder =  EOSsubEvoModelDIR
       for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

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
def SubmitEvoJobsCondor(AFS_DIR,EOS_DIR,population):
    for p in population:
            SHName=AFS_DIR+'/HTCondor/SH/SH_'+str(p)+'.sh'
            SUBName=AFS_DIR+'/HTCondor/SUB/SUB_'+str(p)+'.sub'
            MSGName='MSG_'
            OptionLine=' --Mode Evolution'
            OptionLine+=(' --DNA "'+str(p[3])+'"')
            OptionLine+=(' --afs '+AFS_DIR)
            OptionLine+=(' --eos '+EOS_DIR)
            MSGName+=str(p)
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
#            f.write("output ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".out")
#            f.write("\n")
#            f.write("error ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".err")
#            f.write("\n")
#            f.write("log ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".log")
#            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('request_gpus = 1')
            f.write("\n")
            f.write('+SoftUsed = "EDER-VIANN-EVO"')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+AFS_DIR+'/Code/Create_Model.py '+OptionLine
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

def TrainCleanUp(AFS_DIR, EOS_DIR,mode):
    if mode=='Full':
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-TRAIN\""])
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Models'
      folder =  EOSsubModelDIR
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    else:
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Models'
      folder =  EOSsubModelDIR
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path) and 'error' in file_path:
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

def SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,job_list,mode):
    for job in job_list:
            SHName=AFS_DIR+'/HTCondor/SH/SH_'+str(job[0])+'.sh'
            SUBName=AFS_DIR+'/HTCondor/SUB/SUB_'+str(job[0])+'.sub'
            MSGName='MSG_'
            if mode=='New':
                OptionLine=' --Mode Production'
            else:
                OptionLine=' --Mode Train'
            if job[2]!='-':
               OptionLine+=(' --DNA "'+str(job[2])+'"')
            OptionLine+=(" --ImageSet "+str(job[0]))
            OptionLine+=(" --eos "+EOS_DIR)
            OptionLine+=(" --afs "+AFS_DIR)
            MSGName+=(str(job[0]))
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('request_gpus = 1')
            f.write("\n")
            f.write('+SoftUsed = "EDER-VIANN-TRAIN"')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+AFS_DIR+'/Code/Create_Model.py '+OptionLine
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
