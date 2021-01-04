###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
import math
import time as t
import datetime
import ast
import numpy as np
#This utility provides Timestamps for print messages
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"

#This utility loads an image data
#It requires the location of the file where images are stored
def LoadImages(location):
    csv_read_file=open(location,"r")
    csv_read = csv.reader(csv_read_file, delimiter=',')
    Images=list(csv_read)
    csv_read_file.close()
    for Im in Images:
       Im[4]=ast.literal_eval(Im[4])
    return Images

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

#This utility checks whether the seed track is already in the image
def CheckSeedOverlap(Image,Seed):
    for Tracks in Image[1]:
        if Tracks==Seed[0]:
            return False
    return True

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
            EuclidianOffset=math.sqrt(Track[0][0]**2+Track[0][1]**2+Track[0][2]**2)
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
