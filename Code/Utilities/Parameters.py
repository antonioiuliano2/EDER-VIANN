#This is the list of parameters that EDER-VIANN uses for reconstruction, model training etc. There have been collated here in one place for the user convenience
# Part of EDER-VIANN package
#Made by Filips Fedotovs
#Current version 1.0

######List of naming conventions
x='x' #x-coordinate of the track hit
y='y' #y-coordinate of the track hit
z='z' #z-coordinate of the track hit
FEDRA_Track_ID='FEDRATrackID'
FEDRA_Track_QUADRANT='quarter'
MC_Track_ID='MCTrack'
MC_Event_ID='MCEvent'
MC_VX_ID='MotherID'
FEDRA_VX_ID='VertexS'
MC_NV_VX_ID='-1'
FEDRA_NV_VX_ID='-1.0'

#List of the package run parameters
MaxTracksPerJob=20000 #This parameter imposes the limit on the number of the tracks form the Start plate when forming the Seeds.
MaxEvalTracksPerJob=20000 #This parameter imposes the limit on the number of the tracks form the Start plate when forming the Seeds.
MaxSeedsPerJob=40000

######List of geometrical constain parameters
SI_1=1200
SI_2=1310
SI_3=1600
SI_4=2620
SI_5=3120
SI_6=3940
SI_7=4000 #This parameter restricts the maximum euclidean distance between the first hits of the 2-track seeds that are subject to the Vertex Fit.
MinHitsTrack=2

MaxTrainSampleSize=50000
MaxValSampleSize=100000

VO_T=3900 #The minimum distance from the reconstructed Vertex Origin to the closest starting hit of any track in the seed
VO_max_Z=0 #Fidu
VO_min_Z=-39500
MaxDoca=200
resolution=100
acceptance=0.5
MaxX=3500.0
MaxY=1000.0
MaxZ=20000.0

