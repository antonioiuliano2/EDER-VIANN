#import libraries
import numpy as np
from numpy.random import randint
import argparse
import ast
import csv
import os
import random as rnd
from random import random
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Set the parsing module
parser = argparse.ArgumentParser(description='Enter training job parameters')
parser.add_argument('--MODE',help="Please enter the running mode: 'R' for reset, 'C' for continuing the training", default='C')
parser.add_argument('--IPO',help="Please enter a size of initial population for each sequence length", default='100')
parser.add_argument('--SEL',help="Please selection fraction", default='0.25')
parser.add_argument('--CXPB',help="Please selection crossing probability", default='0.25')
parser.add_argument('--MUTPB',help="Please selection mutation probability", default='0.5')
parser.add_argument('--SIGMA',help="Please selection mutation sigma", default='1.0')
args = parser.parse_args()


#setting main learning parameters
mode=args.MODE
population_size=int(args.IPO)
selection_fraction=float(args.SEL)
selected=int(round(population_size*selection_fraction,0))
CXPB=float(args.CXPB)
MUTPB=float(args.MUTPB)
SIGMA=float(args.SIGMA)
dna_bound=[[10,10,4,4,2,10],[10,10,4,4,2,10],[10,10,4,4,2,10],[10,10,4,4,2,10],[10,10,4,4,2,10],[10,10],[10,10],[10,10],[10,10],[10,10],[10,10,10]] #Sets the maximium bound for the model dna code
#in case if mutation violates it
_=0


#Loading Directory locations
csv_reader=open('../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()
#Loading Data configurations
EOSsubDIR=EOS_DIR+'/'+'EDER-VIANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import Utility_Functions as UF
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print bcolors.HEADER+"#########################  Initialising EDER-VIANN model evolution module  #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print UF.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC
#Functions for the initial model DNA initialisation
def RawDNAInit():
    NumberOfHiddenLayers=randint(5)+1
    NumberOfFullyConnectedLayers=randint(5)+1
    gene=[]
    for HL in range(0,5):
        gene.append([])
    for FC in range(0,5):
        gene.append([])
    gene.append([])
    for i in range(0,NumberOfHiddenLayers):
    #Number of nodes
     gene[i].append(randint(10)+1)
    #Activation function
     gene[i].append(randint(10)+1)
     if i==0:
     #Kernel size
      gene[i].append(randint(5)+1)
     #Pool size
      gene[i].append(randint(5)+1)
     if i>0:
     #Kernel size
      gene[i].append(randint(gene[i-1][2])+1)
     #Pool size
      gene[i].append(randint(gene[i-1][3])+1)
    #Batch normalization
     gene[i].append(randint(2)+1)
    #Scale
     gene[i].append(randint(2)+1)
    #Dropout
     gene[i].append(randint(10)+1)
    for i in range(5,NumberOfFullyConnectedLayers+5):
    #Number of nodes
     gene[i].append(randint(10)+1)
    #Activation function
     gene[i].append(randint(10)+1)
    ####Output layer
    #Activation function
    gene[10].append(randint(10)+1)
    #Batch size
    gene[10].append(randint(10)+1)
    #Epocs
    gene[10].append(randint(10)+1)
    return gene

def InitialisePopulation(Size):
  InitialPopulation=[]
  for s in range(0,Size):
    Individual=[]
    #Specify the generation
    Individual.append(0)
    #Specify whether the individual has been submitted (and how many times)
    Individual.append(0)
    #Specify whether the individual has been evaluated
    Individual.append(0)
    Individual.append(RawDNAInit())
    Individual.append(-0.5)
    InitialPopulation.append(Individual)
  return InitialPopulation
#This code fragment covers the Algorithm logic on the first run
if mode=='R':
 print UF.TimeStamp(),'Starting evolution from the scratch'
 print UF.TimeStamp(),'Cleaning up folders...'
 UF.EvolutionCleanUp(AFS_DIR, EOS_DIR,'Full')
 Population=InitialisePopulation(population_size)
 UF.LogOperations(EOSsubEvoDIR+'/Population.csv','StartLog',Population)
 UF.SubmitEvoJobsCondor(AFS_DIR,EOS_DIR,Population)
 print UF.TimeStamp(), bcolors.OKGREEN+"All jobs for generation 0 have been submitted"+bcolors.ENDC
 print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
if mode=='C':
   Generation=0
   print UF.TimeStamp(),'Continuing the evolution that has been started before'
   csv_reader=open(EOSsubEvoDIR+'/Population.csv',"r")
   PreviousPopulation = list(csv.reader(csv_reader))
   csv_reader.close()
   ###Working out the latest generation
   for i in PreviousPopulation:
       if int(i[0])>Generation:
           Generation=int(i[0])
   ###Working out the remaining jobs
   RemainingJobs=[]
   for i in PreviousPopulation:
       if int(i[0])==Generation:
           if int(i[2])==0:
               file_name=EOSsubEvoModelDIR+'/model_fitness_'+str(i[3])+'.csv'
               try:
                csv_reader=open(file_name,"r")
                result = list(csv.reader(csv_reader))
                i[4]=float(result[0][0])
                i[2]=1
                os.remove(file_name)
               except:
                i[1]=int(i[1])+1
                RemainingJobs.append(i)
   UserAnswer=''
   if len(RemainingJobs)>0:
     print UF.TimeStamp(),bcolors.WARNING+'Warning, there are still', len(RemainingJobs), 'HTCondor jobs remaining'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to wait and try again later please enter W'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to resubmit please enter R'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to continue with existing evaluated options please enter C'+bcolors.ENDC
     UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
     if UserAnswer=='W':
         UF.LogOperations(EOSsubEvoDIR+'/Population.csv','StartLog',PreviousPopulation)
         print UF.TimeStamp(),'OK, exiting now then'
         exit()
     if UserAnswer=='R':
        UF.LogOperations(EOSsubEvoDIR+'/Population.csv','StartLog',PreviousPopulation)
        UF.SubmitEvoJobsCondor(AFS_DIR,EOS_DIR,RemainingJobs)
        print UF.TimeStamp(), bcolors.OKGREEN+"All jobs for generation ",Generation,"have been resubmitted"+bcolors.ENDC
        print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
        exit()

   if len(RemainingJobs)==0 or UserAnswer=='C':
      UF.LogOperations(EOSsubEvoDIR+'/Population.csv','StartLog',PreviousPopulation)
      UF.EvolutionCleanUp(AFS_DIR, EOS_DIR,'_')
      print bcolors.BOLD+'Batch',Generation,' is completed'+bcolors.ENDC
      print bcolors.BOLD+'Would you like to continue training?'+bcolors.ENDC
      UserAnswer=raw_input(bcolors.BOLD+"Please, enter Y/N\n"+bcolors.ENDC)
      if UserAnswer=='N':
          print UF.TimeStamp(),bcolors.OKGREEN+'Evolution is finished then, thank you and good bye'+bcolors.ENDC

          exit()
      print UF.TimeStamp(),'Creating next generaion',Generation+1
      PreSelectedPopulation=[]
      for record in PreviousPopulation:
               PreSelectedPopulation.append(record)
      selected_parents_1=sorted(PreSelectedPopulation,key=lambda x: float(x[4]),reverse=True)[:selected]
      selected_parents_2=sorted(PreSelectedPopulation,key=lambda x: float(x[4]),reverse=True)[:selected]
      selected_parents_2.append(selected_parents_1[0])
      children_1=[]
      children_2=[]
      for p in range(0,len(selected_parents_1)):
        children_1.append([])
        children_2.append([])
      for p in range(0,len(selected_parents_1)):
                 children_1[p].append(Generation+1)
                 children_1[p].append(0)
                 children_1[p].append(0)
                 children_2[p].append(Generation+1)
                 children_2[p].append(0)
                 children_2[p].append(0)
                 parent_dna_1=ast.literal_eval(selected_parents_1[p][3])
                 parent_dna_2=ast.literal_eval(selected_parents_2[p+1][3])
                 child_dna_1=[]
                 child_dna_2=[]
                 for codon in range(0,len(parent_dna_1)):
                     if len(parent_dna_1[codon])>1 and len(parent_dna_2[codon])>1:
                         child_codon_1=[]
                         child_codon_2=[]
                         for base in range(0,len(parent_dna_1[codon])):
                             if random()<=CXPB:
                                child_codon_2.append(parent_dna_1[codon][base])
                                child_codon_1.append(parent_dna_2[codon][base])
                             else:
                                child_codon_2.append(parent_dna_2[codon][base])
                                child_codon_1.append(parent_dna_1[codon][base])
                         child_dna_1.append(child_codon_1)
                         child_dna_2.append(child_codon_2)
                     else:
                         if random()<=CXPB:
                            child_dna_1.append(parent_dna_2[codon])
                            child_dna_2.append(parent_dna_1[codon])
                         else:
                            child_dna_1.append(parent_dna_1[codon])
                            child_dna_2.append(parent_dna_2[codon])
                 children_1[p].append(child_dna_1)
                 children_2[p].append(child_dna_2)
                 children_1[p].append(-0.5)
                 children_2[p].append(-0.5)
                 children=children_1+children_2
                 selected_children=(children)[:selected]
      print UF.TimeStamp(),bcolors.OKGREEN+'Population crossing is completed...'+bcolors.ENDC
      for c in range(0,len(selected_children)):
           for codon in range(0,len(selected_children[c][3])):
              if len(selected_children[c][3][codon])>=1:
                for base in range(0,len(selected_children[c][3][codon])):
                  if rnd.random() <= MUTPB:
                    sign=rnd.choice((-1,1))
                    mutation_step=int(sign*(round((rnd.gauss(0, SIGMA)),0)))
                    selected_children[c][3][codon][base]+=mutation_step
                    if selected_children[c][3][codon][base]>dna_bound[codon][base]:
                       selected_children[c][3][codon][base]=dna_bound[codon][base]
                    if selected_children[c][3][codon][base]<1:
                       selected_children[c][3][codon][base]=1
      print UF.TimeStamp(),bcolors.OKGREEN+'Mutation operation is completed...'+bcolors.ENDC
      print UF.TimeStamp(),'The next generation will consist of ',len(selected_children), 'individuals'
      Population=PreviousPopulation+selected_children
      UF.LogOperations(EOSsubEvoDIR+'/Population.csv','UpdateLog',selected_children)
      UF.SubmitEvoJobsCondor(AFS_DIR,EOS_DIR,selected_children)
      print UF.TimeStamp(),bcolors.OKGREEN+'The next generation',Generation+1,' consisting of ',len(selected_children), 'individuals has been submitted for evaluation'+bcolors.ENDC
      print UF.TimeStamp(),bcolors.OKGREEN+'All jobs have been submitted'+bcolors.ENDC
      print bcolors.BOLD,'Please run the script in few hours with --MODE C setting'+bcolors.ENDC
exit()


