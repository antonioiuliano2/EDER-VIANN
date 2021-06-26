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
######List of geomtrical parameters
SI_1=1050
SI_2=1310
SI_3=1850
SI_4=2630
SI_5=2900
SI_6=3930
SI_7=4000 #This parameter restricts the maximum euclidean distance between the first hits of the 2-track seeds that are subject to the Vertex Fit.
MaxTracksPerJob=20000 #This parameter imposes the limit on the number of the tracks form the Start plate when forming the Seeds.

