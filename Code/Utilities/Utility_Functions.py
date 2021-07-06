###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
import math
import os, shutil
import subprocess
#import time as t
import datetime
#import ast
import numpy as np
#import scipy
import copy
#from scipy.stats import chisquare
import tensorflow as tf
from tensorflow import keras
#This utility provides Timestamps for print messages
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"

def CleanFolder(folder,key):
    if key=='':
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    else:
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path) and (key in the_file):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
#This function automates csv read/write operations
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
    if mode=='ReadLog':
        csv_reader_log=open(flocation,"r")
        log_reader = csv.reader(csv_reader_log)
        return list(log_reader)

def EnrichImage(resolution, Image):
     New_image=[[],[],[],[],[]]
     for Tracks in Image[1]:
      New_Track=[]
      for h in range(0,len(Tracks)-1):
        deltaX=float(Tracks[h+1][0])-float(Tracks[h][0])
        deltaZ=float(Tracks[h+1][2])-float(Tracks[h][2])
        deltaY=float(Tracks[h+1][1])-float(Tracks[h][1])
        try:
         vector_1 = [deltaZ,0]
         vector_2 = [deltaZ, deltaX]
         ThetaAngle=angle_between(vector_1, vector_2)
        except:
         ThetaAngle=0.0
        try:
         vector_1 = [deltaZ,0]
         vector_2 = [deltaZ, deltaY]
         PhiAngle=angle_between(vector_1, vector_2)
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
      New_image[1].append(New_Track)
     return New_image

def SubmitCreateSeedsJobsCondor(job):
            SHName=job[11]+'/HTCondor/SH/SH_CS_'+str(job[0])+'_'+str(job[1])+'.sh'
            SUBName=job[11]+'/HTCondor/SUB/SUB_CS_'+str(job[0])+'_'+str(job[1])+'.sub'
            MSGName='MSG_CS_'
            OptionLine=(' --Set '+str(job[0]))
            OptionLine+=(" --Subset "+str(job[1]))
            OptionLine+=(" --EOS "+str(job[12]))
            OptionLine+=(" --AFS "+str(job[11]))
            OptionLine+=(" --PlateZ "+str(job[2]))
            OptionLine+=(" --MaxTracks "+str(job[10]))
            OptionLine+=(" --SI_1 "+str(job[3]))
            OptionLine+=(" --SI_2 "+str(job[4]))
            OptionLine+=(" --SI_3 "+str(job[5]))
            OptionLine+=(" --SI_4 "+str(job[6]))
            OptionLine+=(" --SI_5 "+str(job[7]))
            OptionLine+=(" --SI_6 "+str(job[8]))
            OptionLine+=(" --SI_7 "+str(job[9]))
            MSGName+=str(job[0])
            MSGName+='_'
            MSGName+=str(job[1])
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+job[11]+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+job[11]+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+job[11]+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('+SoftUsed = "EDER-VIANN-CS"')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+job[11]+'/Code/Utilities/R2_GenerateSeeds_Sub.py '+OptionLine
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

def SubmitVertexSeedsJobsCondor(job):
            SHName=job[14]+'/HTCondor/SH/SH_VS_'+str(job[0])+'_'+str(job[1])+'_'+str(job[2])+'.sh'
            SUBName=job[14]+'/HTCondor/SUB/SUB_VS_'+str(job[0])+'_'+str(job[1])+'_'+str(job[2])+'.sub'
            MSGName='MSG_VS_'
            OptionLine=(' --Set '+str(job[0]))
            OptionLine+=(" --SubSet "+str(job[1]))
            OptionLine+=(" --Fraction "+str(job[2]))
            OptionLine+=(" --EOS "+str(job[15]))
            OptionLine+=(" --AFS "+str(job[14]))
            OptionLine+=(" --TV_int_1 "+str(job[3]))
            OptionLine+=(" --TV_int_2 "+str(job[4]))
            OptionLine+=(" --TV_int_3 "+str(job[5]))
            OptionLine+=(" --TV_int_4 "+str(job[6]))
            OptionLine+=(" --TV_int_5 "+str(job[7]))
            OptionLine+=(" --MaxDoca "+str(job[8]))
            OptionLine+=(" --resolution "+str(job[9]))
            OptionLine+=(" --acceptance "+str(job[10]))
            OptionLine+=(" --MaxX "+str(job[11]))
            OptionLine+=(" --MaxY "+str(job[12]))
            OptionLine+=(" --MaxZ "+str(job[13]))
            MSGName+=str(job[0])
            MSGName+='_'
            MSGName+=str(job[1])
            MSGName+='_'
            MSGName+=str(job[2])
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+job[14]+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+job[14]+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+job[14]+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('+SoftUsed = "EDER-VIANN-VS"')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+job[14]+'/Code/Utilities/R3_VertexSeeds_Sub.py '+OptionLine
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

def CreateSeedsCleanUp(AFS_DIR, EOS_DIR):
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-CS\""])
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/REC_SET'
      folder =  EOSsubModelDIR
      CleanFolder(folder,'SEED_SET_')
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_CS_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_CS_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_CS_')

def CreateVertexCleanUp(AFS_DIR, EOS_DIR):
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-VS\""])
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/REC_SET'
      folder =  EOSsubModelDIR
      CleanFolder(folder,'VX_CANDIDATE_SET_')
      CleanFolder(folder,'VX_REC_RAW_SET_')
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_VS_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_VS_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_VS_')

def CreateFullVertexCleanUp(AFS_DIR, EOS_DIR):
      subprocess.call(['condor_rm', '-constraint', "SoftUsed == \"EDER-VIANN-VS\""])
      EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/REC_SET'
      folder =  EOSsubModelDIR
      CleanFolder(folder,'VX_CANDIDATE_SET_')
      CleanFolder(folder,'VX_REC_SET_')
      CleanFolder(folder,'VX_REC_RAW_SET_')
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_VS_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_VS_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_VS_')

#Given seed, this function assigns the track hit positions for the seed
def DecorateSeedTracks(seed,tracks):
     new_seed=[]
     new_seed.append(seed)
     new_seed.append([])
     for s in range(len(seed)):
      new_seed[1].append([])
      for t in tracks:
           if seed[s]==t[3]:
              new_seed[1][s].append(t[:3])
     return new_seed

def SortImage(seed):
   for Track in range(0,len(seed[1])):
         seed[1][Track]=sorted(seed[1][Track],key=lambda x: float(x[2]),reverse=False)
   return seed

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    dot = v1_u[0]*v2_u[0] + v1_u[1]*v2_u[1]      # dot product
    det = v1_u[0]*v2_u[1] - v1_u[1]*v2_u[0]      # determinant
    return np.arctan2(det, dot)

#This utility shifts hit coordinates so they all start at z,x,y=0
def PreShiftImage(seed):
     LongestDistance=0.0
     for Track in seed[1]:
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                FinX=float(Track[0][0])
                FinY=float(Track[0][1])
                FinZ=float(Track[0][2])
     for Tracks in seed[1]:
      for Hits in Tracks:
        Hits[0]=float(Hits[0])-FinX
        Hits[1]=float(Hits[1])-FinY
        Hits[2]=float(Hits[2])-FinZ
     return seed

def GetEquationOfTrack(Track):
      Xval=[]
      Yval=[]
      Zval=[]
      for Hits in Track:
        Xval.append(Hits[0])
        Yval.append(Hits[1])
        Zval.append(Hits[2])
      XZ=np.polyfit(Zval,Xval,1)
      YZ=np.polyfit(Zval,Yval,1)
      observed=[]
      expected=[]
      for dp in range(len(Track)):
         observed.append((Xval[dp]-np.polyval(XZ,Zval[dp]))**2)
         observed.append((Yval[dp]-np.polyval(YZ,Zval[dp]))**2)
         expected.append(0)
         expected.append(0)
      return (XZ,YZ, 'N/A',Xval[0],Yval[0],Zval[0])

def closestDistanceBetweenLines(a0,a1,b0,b1,clampAll=False,clampA0=False,clampA1=False,clampB0=False,clampB1=False):

    ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
        Return the closest points on each segment and their distance
    '''
    a0=np.array(a0)
    a1=np.array(a1)
    b0=np.array(b0)
    b1=np.array(b1)
    # If clampAll=True, set all clamps to True
    if clampAll:
        clampA0=True
        clampA1=True
        clampB0=True
        clampB1=True


    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0
    magA = np.linalg.norm(A)
    magB = np.linalg.norm(B)

    _A = A / magA
    _B = B / magB

    cross = np.cross(_A, _B);
    denom = np.linalg.norm(cross)**2


    # If lines are parallel (denom=0) test if lines overlap.
    # If they don't overlap then there is a closest point solution.
    # If they do overlap, there are infinite closest positions, but there is a closest distance
    if not denom:
        d0 = np.dot(_A,(b0-a0))

        # Overlap only possible with clamping
        if clampA0 or clampA1 or clampB0 or clampB1:
            d1 = np.dot(_A,(b1-a0))

            # Is segment B before A?
            if d0 <= 0 >= d1:
                if clampA0 and clampB1:
                    if np.absolute(d0) < np.absolute(d1):
                        return a0,b0,np.linalg.norm(a0-b0)
                    return a0,b1,np.linalg.norm(a0-b1)


            # Is segment B after A?
            elif d0 >= magA <= d1:
                if clampA1 and clampB0:
                    if np.absolute(d0) < np.absolute(d1):
                        return a1,b0,np.linalg.norm(a1-b0)
                    return a1,b1,np.linalg.norm(a1-b1)


        # Segments overlap, return distance between parallel segments
        return None,None,np.linalg.norm(((d0*_A)+a0)-b0)



    # Lines criss-cross: Calculate the projected closest points
    t = (b0 - a0);
    detA = np.linalg.det([t, _B, cross])
    detB = np.linalg.det([t, _A, cross])

    t0 = detA/denom;
    t1 = detB/denom;

    pA = a0 + (_A * t0) # Projected closest point on segment A
    pB = b0 + (_B * t1) # Projected closest point on segment B


    # Clamp projections
    if clampA0 or clampA1 or clampB0 or clampB1:
        if clampA0 and t0 < 0:
            pA = a0
        elif clampA1 and t0 > magA:
            pA = a1

        if clampB0 and t1 < 0:
            pB = b0
        elif clampB1 and t1 > magB:
            pB = b1

        # Clamp projection A
        if (clampA0 and t0 < 0) or (clampA1 and t0 > magA):
            dot = np.dot(_B,(pA-b0))
            if clampB0 and dot < 0:
                dot = 0
            elif clampB1 and dot > magB:
                dot = magB
            pB = b0 + (_B * dot)

        # Clamp projection B
        if (clampB0 and t1 < 0) or (clampB1 and t1 > magB):
            dot = np.dot(_A,(pB-a0))
            if clampA0 and dot < 0:
                dot = 0
            elif clampA1 and dot > magA:
                dot = magA
            pA = a0 + (_A * dot)


    return pA,pB,np.linalg.norm(pA-pB)

def GiveExpressSeedInfo(seed):
               # #Get equation of track motion in ZX plane
                XZ1=GetEquationOfTrack(seed[1][0])[0]
                XZ2=GetEquationOfTrack(seed[1][1])[0]
                YZ1=GetEquationOfTrack(seed[1][0])[1]
                YZ2=GetEquationOfTrack(seed[1][1])[1]
                X1S=GetEquationOfTrack(seed[1][0])[3]
                X2S=GetEquationOfTrack(seed[1][1])[3]
                Y1S=GetEquationOfTrack(seed[1][0])[4]
                Y2S=GetEquationOfTrack(seed[1][1])[4]
                Z1S=GetEquationOfTrack(seed[1][0])[5]
                Z2S=GetEquationOfTrack(seed[1][1])[5]
                vector_1_st = np.array([np.polyval(XZ1,seed[1][0][0][2]),np.polyval(YZ1,seed[1][0][0][2]),seed[1][0][0][2]])
                vector_1_end = np.array([np.polyval(XZ1,seed[1][0][len(seed[1][0])-1][2]),np.polyval(YZ1,seed[1][0][len(seed[1][0])-1][2]),seed[1][0][len(seed[1][0])-1][2]])
                vector_2_st = np.array([np.polyval(XZ2,seed[1][0][0][2]),np.polyval(YZ2,seed[1][0][0][2]),seed[1][0][0][2]])
                vector_2_end = np.array([np.polyval(XZ2,seed[1][0][len(seed[1][0])-1][2]),np.polyval(YZ2,seed[1][0][len(seed[1][0])-1][2]),seed[1][0][len(seed[1][0])-1][2]])
                result=closestDistanceBetweenLines(vector_1_st,vector_1_end,vector_2_st,vector_2_end,clampAll=False,clampA0=False,clampA1=False,clampB0=False,clampB1=False)
                midpoint=(result[0]+result[1])/2
                D1M=math.sqrt(((midpoint[0]-X1S)**2) + ((midpoint[0]-Y1S)**2) + ((midpoint[0]-Z1S)**2))
                D2M=math.sqrt(((midpoint[0]-X2S)**2) + ((midpoint[0]-Y2S)**2) + ((midpoint[0]-Z2S)**2))
                return (midpoint,result[2],D1M, D2M)

def SeedQualityCheck(seed,MaxDoca,TV_int_1, TV_int_2, TV_int_3, TV_int_4, TV_int_5):
  try:
    Answer=GiveExpressSeedInfo(seed)
    Doca=Answer[1]
    TrVx=max(Answer[2],Answer[3])
    if Doca>MaxDoca:
        return False
    if TrVx>TV_int_5:
       return False
    elif TrVx<=TV_int_4 and TrVx>=TV_int_3:
       return False
    elif TrVx<=TV_int_2 and TrVx>=TV_int_1:
       return False
    return True
  except:
    return False

def LonRotateImage(seed,var):
    #Locate the longest track (assumption that it has the highest Pt)
        if var=='x':
            pos=0
        else:
            pos=1
        LongestDistance=0.0
        for Track in seed[1]:
            Vardiff=float(Track[len(Track)-1][pos])
            Xdiff=float(Track[0][0])-float(Track[len(Track)-1][0])
            Ydiff=float(Track[0][1])-float(Track[len(Track)-1][1])
            Zdiff=float(Track[0][2])-float(Track[len(Track)-1][2])
            ControlDistance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            Zdiff=float(Track[len(Track)-1][2])
            if ControlDistance>=LongestDistance:
                LongestDistance=ControlDistance
                vector_1 = [Zdiff, 0]
                vector_2 = [Zdiff, Vardiff]
                Angle=angle_between(vector_1, vector_2)
                if np.isnan(Angle)==True:
                    Angle=0.0
        for Tracks in seed[1]:
           for hits in Tracks:
                Z=float(hits[2])
                Pos=float(hits[pos])
                hits[2]=(Z*math.cos(-Angle)) - (Pos * math.sin(-Angle))
                hits[pos]=(Z*math.sin(-Angle)) + (Pos * math.cos(-Angle))
        return seed

def PhiRotateImage(seed):
    #Locate the longest track (assumption that it has the highest Pt)
        LongestDistance=0.0
        for Track in seed[1]:
                X=float(Track[len(Track)-1][0])
                Y=float(Track[len(Track)-1][1])
                Distance=math.sqrt((X**2)+(Y**2))
                if Distance>=LongestDistance:
                 LongestDistance=Distance
                 vector_1 = [Distance, 0]
                 vector_2 = [X, Y]
                 Angle=-angle_between(vector_1,vector_2)
        if np.isnan(Angle)==True:
                    Angle=0.0
        for Tracks in seed[1]:
            for hits in Tracks:
                X=float(hits[0])
                Y=float(hits[1])
                hits[0]=(X*math.cos(Angle)) - (Y * math.sin(Angle))
                hits[1]=(X*math.sin(Angle)) + (Y * math.cos(Angle))
        return seed
def RescaleImage(seed,max_x,max_y,max_z,res):
    #Locate the longest track (assumption that it has the highest Pt)
        X=[]
        Y=[]
        Z=[]
        for Tracks in seed[1]:
            for hits in Tracks:
                X.append(hits[0])
                Y.append(hits[1])
                Z.append(hits[2])
        dUpX=max_x-max(X)
        dDownX=max_x+min(X)
        dX=(dUpX+dDownX)/2
        xshift=dUpX-dX
        X=[]
        for Tracks in seed[1]:
            for hits in Tracks:
                hits[0]=hits[0]+xshift
                X.append(hits[0])
        ##########Y
        dUpY=max_y-max(Y)
        dDownY=max_y+min(Y)
        dY=(dUpY+dDownY)/2
        yshift=dUpY-dY
        Y=[]
        for Tracks in seed[1]:
            for hits in Tracks:
                hits[1]=hits[1]+yshift
                Y.append(hits[1])
        min_scale=max(max(X)/(max_x-(2*res)),max(Y)/(max_y-(2*res)), max(Z)/(max_z-(2*res)))
        for Tracks in seed[1]:
            for hits in Tracks:
                hits[0]=hits[0]/min_scale
                hits[1]=hits[1]/min_scale
                hits[2]=hits[2]/min_scale
        return seed

#This utility shifts hit coordinates so they all start at z,x,y=0
def AfterShiftImage(seed,res):
     FinZ=666666.0
     for Track_No in range(0,len(seed[1])):
         if FinZ>float(seed[1][Track_No][0][2]):
             FinZ=float(seed[1][Track_No][0][2])-res
     LongestDistance=0.0
     for Track in seed[1]:
            Xdiff=float(Track[len(Track)-1][0])-float(Track[0][0])
            Ydiff=float(Track[len(Track)-1][1])-float(Track[0][1])
            Zdiff=float(Track[len(Track)-1][2])-float(Track[0][2])
            Distance=math.sqrt(Xdiff**2+Ydiff**2+Zdiff**2)
            if Distance>=LongestDistance:
                LongestDistance=Distance
                FinX=float(Track[0][0])
                FinY=float(Track[0][1])
     for Tracks in seed[1]:
      for Hits in Tracks:
        Hits[0]=float(Hits[0])-FinX
        Hits[1]=float(Hits[1])-FinY
        Hits[2]=float(Hits[2])-FinZ
     return seed

def ChangeImageResoluion(resolution,Image):
    #sort Mothers:
    for Tracks in Image[1]:
      for Hits in Tracks:
        Hits[0]=int(round(float(Hits[0])/resolution,0))
        Hits[1]=int(round(float(Hits[1])/resolution,0))
        Hits[2]=int(round(float(Hits[2])/resolution,0))
    return Image

def LoadRenderImages(Images,resolution,MaxX,MaxY,MaxZ,StartSeed,EndSeed,Train):
    boundsX=int(round(MaxX/resolution,0))
    boundsY=int(round(MaxY/resolution,0))
    boundsZ=int(round(MaxZ/resolution,0))
    H=boundsX*2
    W=boundsY*2
    L=boundsZ
    Images_Copy=copy.deepcopy(Images[StartSeed-1:min(EndSeed,len(Images))])
    additional_data=[]
    for im in Images_Copy:
        additional_data.append(EnrichImage(resolution, im))
    ImagesY=np.empty([len(Images_Copy),1])
    ImagesX=np.empty([len(Images_Copy),H,W,L],dtype=np.float16)
    for im in range(0,len(Images_Copy)):
        Images_Copy[im]=ChangeImageResoluion(resolution, Images_Copy[im])
        additional_data[im]=ChangeImageResoluion(resolution, additional_data[im])
        if Train:
           ImagesY[im]=int(float(Images_Copy[im][3])/2)
        else:
           ImagesY[im]=0
        BlankRenderedImage=[]
        for x in range(-boundsX,boundsX):
          for y in range(-boundsY,boundsY):
            for z in range(0,boundsZ):
             BlankRenderedImage.append(0.0)
        RenderedImage = np.array(BlankRenderedImage)
        RenderedImage = np.reshape(RenderedImage,(H,W,L))
        for Tracks in Images_Copy[im][1]:
            for Hits in Tracks:
                if abs(Hits[0])<boundsX and abs(Hits[1])<boundsY and abs(Hits[2])<boundsZ:
                   RenderedImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=1.0
        for Tracks in additional_data[im][1]:
            for Hits in Tracks:
                if abs(Hits[0])<boundsX and abs(Hits[1])<boundsY and abs(Hits[2])<boundsZ:
                   RenderedImage[Hits[0]+boundsX][Hits[1]+boundsY][Hits[2]]=1.0
        ImagesX[im]=RenderedImage
    ImagesX= ImagesX[..., np.newaxis]
    ImagesY=tf.keras.utils.to_categorical(ImagesY,2)
    del Images_Copy
    del additional_data
    return (ImagesX,ImagesY)
