###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
import math
import os, shutil
import subprocess
import time as t
import datetime
import ast
import numpy as np
import htcondor
schedd = htcondor.Schedd()
def SubmitDummyJobs(population):
    sub = htcondor.Submit()
    sub['executable']="/afs/cern.ch/user/f/ffedship/private/SND/EDER-VIANN/Code/Utilities/dummy.py"
    sub['output']="dummy.out"
    sub['error']="dummy.err"
    sub['log']="dummy.log"

    with schedd.transaction() as txn:
        for p in population:
            argument='-f '+p
            sub['Arguments']=argument
            sub.queue(txn)
    print("Jobs has been successfully submitted")

