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
4) If happy, save and close the file.
4) cd ..
5) tmux (please note the number of lxplus machine at which tmux session is logged in)
4) kinit your<username>@CERN.CH -l 24h00m
7) python3 R1_PrepareRecData.py --Xmin 50000 --Xmax 120000 --Ymin 50000 --Ymax 120000 --Track FEDRA --f $<your file with reconstructed tracks> (min and max value arguments can be changed or completely removed if all ECC data to be reconstructed. Track type can be changed to MC if Monte-Carlo truth track reconstruction data is used. The script can take 1-5 minutes depending on the size of the input file. Once it finish it will give the message "The track data has been created successfully and written to ....' and exit.)
8) python3 R2_GenerateSeeds.py --Mode R
   (The script will send warning, type Y. The program will send HTCondor jobs and exit. The jobs take about an hour.)
9) (After an hour or so) python3 R2_GenerateSeeds.py --Mode C (it will check whether the HTCondor jobs have been completed, if not it will give a warning).
10) This process is repeated multiple times until the model is sufficinetly trained
