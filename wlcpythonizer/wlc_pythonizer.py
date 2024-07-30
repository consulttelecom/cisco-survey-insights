import itertools
import time
import pickle
from datetime import date
import logging
from collections import Counter
from pathlib import Path
import sys
import base64
home = str(Path.home())
sys.path.append(home)

from aireos_dicts_classes import Wlc_Config, test_parsing_dicts_aireos, grep, show, Nearby_Ap, NamedList

from ewlc_dicts_classes import Wlc_Ios_Xe_Config, test_parsing_dicts_ewlc

from parsing_utils import parse_file, read_folder

from rogue_aps_utils import print_rogues_per_ap, rogue_ap_rssi_histogram, rogue_ap_summary, rogue_ap_summary_site, rogue_ap_time, number_of_rogue_aps

def main():
    home = str(Path.home())
    logging.basicConfig(filename=home + '/wlc-pythonizer.log', filemode='w', level=logging.DEBUG)
    test_parsing_dicts_aireos()  # this function checks parsing dicts for correct attributes
    test_parsing_dicts_ewlc()  # this function checks parsing dicts for correct attributes
    print('                                          ``.........``                                             \n' \
          '                                     `.-::::::::::::::::::-.`                                       \n' \
          '                                 `.:::::::::::::::::::::::::::-.                                    \n' \
          '                               .:/:::::::::::::::::::::::::::::::-.                                 \n' \
          '                             -::::::::::-..`          `..-::::::::::.                               \n' \
          '                            -::::::::.`                    `.::::::::.                              \n' \
          '                            .:::::-`      ``.---::---.`       `-:::::`                              \n' \
          '                             ``.`      `-::::::::::::::::.`      `.``                               \n' \
          '                                     .:::::::::::::::::::::-`                                       \n' \
          '                                    .:::::::::--..--:::::::::`                                      \n' \
          '                                    `:::::.`          `-:::::                                       \n' \
          '                                      .-.               `.-.                                        \n' \
          '                                                ```                                                 \n' \
          '                                             .:/::::.                                               \n' \
          '                                            -::::::::.                                              \n' \
          '                                            .::::::::`                                              \n' \
          '                                             `-::::-`                                               \n' \
          '                                        `-ssssssssssss-.                                            \n' \
          '                                      `/ssoosssssssssssso-                                          \n' \
          '                                      :ss-  /sssssssssssys-                                         \n' \
          '                                      :sss:/ssssssssssyyyy:                                         \n' \
          '                                      -ssssssssssssyyyyyy:                                          \n' \
          '                               `-ssssssssssssssssyyyyyyyy:`.....`                                   \n' \
          '                             `+sssssssssssssssssyyyyyyyyyy:.-------`                                \n' \
          '                            `sssssssssssssssssyyyyyyyyyyyy-.--------`                               \n' \
          '                            +sssssssssssssssyyyyyyyyyyyyys`---------.                               \n' \
          '                            sssssssssssssssssyyyyyyyyyys:`.---------.                               \n' \
          '                            sssssssssss/.................-----------.                               \n' \
          '                            osssssssss``..--------------------------.                               \n' \
          '                            /ssssssss:`-----------------------------.                               \n' \
          '                            `ossssyyy-.-----------------------------                                \n' \
          '                             `/ssyyyy-.---------------------------.                                 \n' \
          '                                .----`.-------------------``````                                    \n' \
          '                                      .-------------------.                                         \n' \
          '                                      .-------------.``.--.                                         \n' \
          '                                      `--------------``---.                                         \n' \
          '                                       `.----------------`                                          \n' \
          '                                           ```.```.````                                             \n' \
          '                                                                                                    \n' \
          '  Welcome to WLC Pythonizer                                                                         \n')

    return None

if __name__ == "__main__":
    main()