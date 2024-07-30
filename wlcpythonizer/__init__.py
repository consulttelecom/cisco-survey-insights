import itertools
import time
import pickle
from datetime import date
import logging
from collections import Counter
from pathlib import Path
import sys
import os
home = str(Path.home())
sys.path.append(home)
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from aireos_dicts_classes import Wlc_Config, test_parsing_dicts_aireos, grep, show

from ewlc_dicts_classes import Wlc_Ios_Xe_Config, test_parsing_dicts_ewlc

from best_practices import Best_Practice_Description, bp_check

from rogue_aps_utils import print_rogues_per_ap, rogue_ap_rssi_histogram, rogue_ap_summary, rogue_ap_summary_site, rogue_ap_time, number_of_rogue_aps

from parsing_utils import parse_file, read_folder

logging.basicConfig(filename=home+'/wlc-pythonizer.log', filemode='w', level=logging.DEBUG)
test_parsing_dicts_aireos() #this function checks parsing dicts for correct attributes
test_parsing_dicts_ewlc()   #this function checks parsing dicts for correct attributes

__author__ = "Roman Podoynitsyn"

