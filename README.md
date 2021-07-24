# EDER-VIANN
Emulsion Data Event Reconstruction - Vertex Identification by using Artificial Neural Networks

This README just serves as a very short user guide, the documentation will be written much later

------- Installation steps --------

1) pip3 install tensorflow --user
2) pip3 install keras==2.3.1 --user
3) go to your home directory on AFS where you would like to install the package
4) git clone https://github.com/FilipsFedotovs/EDER-VIANN/
5) cd EDER-VIANN/
6) python3 setup.py
7) The installation will require another directory, please enter the location on EOS where you would like to keep data and the models (has to provide up to 10-100 GB of storage depending on whether particular components of the framework is used. An example of the input is /eos/experiment/ship/user/username (but create the directory there first).
8) The installer will copy and analyse existing data and the pre-trained model, it might take 5-10 minutes.
9) if the message 'EDER-VIANN setup is successfully completed' is displayed, it means that the package is ready for work.

-------- Vertex Reconstruction -------
1) Please make sure that you have a file with hits that there were reconstructed as Tracks.
   Following columns are required: 
   - Track ID Quadrant or Event ID (if MC truth track reconstruction data is used)
   - Track ID (FEDRA or MC depending which data is used)
   - x-coordinates of the track hits
   - y-coordinates of the track hits
   - z-coordinates of the track hits
2) Please open $AFS/EDER_VIANN/Code/Utilities/Parameters.py and check that the lines between 6-13 (within the list of naming conventions correspond to headers in  the      file that you intend to use.
3) Check the 'CNN_Model_Name' variable - it has the name of the Model that is used for reconstruction (included in the package). If you wish to use your own, please place it in the $EOS/EDER_VIANN/Models and change the 'CNN_Model_Name' variable accordingly. You might need to change resolution and MaxX, MaxY, MaxZ parameters if the model was trained with images that have had different size because the model will fail if the image format is different.
4) If happy, save and clode the file.
4) cd ..
5) tmux (please note the number of lxplus machine at which tmux session is logged in)
4) kinit your<username>@CERN.CH -l 24h00m
7) python3 R1_PrepareRecData.py --Xmin 50000 --Xmax 120000 --Ymin 50000 --Ymax 120000 --Track FEDRA --f $<your file with reconstructed tracks> (min and max value arguments can be changed or completely removed if all ECC data to be reconstructed. Track type can be changed to MC if Monte-Carlo truth track reconstruction data is used). The script can take 1-5 minutes depending on the size of the input file.
8) The script will ask which samples to use. Please type D and press ENTER.The script will send HTCondor jobs and exit.
9) After a day or so please run: python Model_Training.py --MODE C
10) This process is repeated multiple times until the model is sufficinetly trained

------- Track reconstruction --------
1) Go to EDER_TRAN directory on AFS
2) cd Code 
3) tmux (please note the number of lxplus machine at which tmux session is logged in)
4) kinit username@CERN.CH -l 24h00m
5) python3 Track_Reconstructor.py 
   The process can take many hours, log out of tmux by using ctrl+b

------ Hit utilisation Analysis -------
1) Relogin to the same machine by using ssh -XY username@lxplus#.cern.ch where # is the recorded number.
2) tmux a -t 0
3) if the green message "The reconstruction has completed # tracks have been recognised' is displayed, it means that the reconstruction is finished.
4) kinit username@CERN.CH
5) cd Utilisation
6) python Analyse_Hit_Utilisation.py --metric TRANN
