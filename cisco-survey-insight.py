from wlcpythonizer import wlc_pythonizer as wlcp
import pathlib
import json
import zipfile
import shutil
import sys
import uuid
import logging

#Set logging parameters globally
home = pathlib.Path.cwd()
log_filepath = home / 'sensei.log'
logger = logging.getLogger(__name__)
if not log_filepath.is_file():
    log_filepath.touch()
logger = logging.getLogger('sensei')
logger.setLevel(logging.DEBUG)
fh1 = logging.FileHandler(str(log_filepath))  # create a file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh1.setFormatter(formatter)  # set formatter
logger.addHandler(fh1)
logger.debug('Logging started')

def unique_id():
    return str(uuid.uuid4())

def get_ap_name_by_bssid(bssid, wlc_config):
    if wlc_config.platform == 'AireOS':
        ap_list = [ap.name for ap in wlc_config.ap_configs if ap.slot_0_bssid == bssid]
    else:
        ap_list = [ap.ap_name for ap in wlc_config.ap_rf_5 if ap.mac_address == bssid]
    if len(ap_list) == 0: ap_list.append('AP_' + bssid)
    return ap_list[0]

def get_ap_notes(wlc_config):
    # This function returns notes text for every AP in config in dictionary of following format {'AP name':'note text'}
    # parameters_dict is also added to be used in coloration and tagging functions later
    notes_dict = {}
    parameters_per_ap_dict = {}
    if wlc_config.platform == 'AireOS':
        for ap in wlc_config.ap_rf:
            if 'slot1' in ap.name:
                text = ''
                parameters_dict = {}
                if len([nearbyap for nearbyap in ap.nearby_aps if
                        ap.channel_assignment_information_recommended_best_channel == nearbyap.channel]) > 3:
                    text = '!!!!' + '\n'
                text = text + 'Recommended channel (5GHz): ' + ap.channel_assignment_information_recommended_best_channel + '\n'
                text = text + 'Channel change count: ' + ap.channel_assignment_information_channel_change_count + '\n'
                parameters_dict['chan_changes'] = int(ap.channel_assignment_information_channel_change_count)
                text = text + 'Channel utilization (5GHz): ' + ap.load_profile_channel_utilization + '\n'
                parameters_dict['chan_util_5G'] = int(ap.load_profile_channel_utilization.split(' ')[0])
                text = text + 'Number of clients: ' + ap.load_profile_attached_clients + '\n'
                parameters_dict['clients'] = int(ap.load_profile_attached_clients.split(' ')[0])
                rogue_aps = wlcp.number_of_rogue_aps(wlc_config, ap.name.split('_')[0])
                text = text + 'Number of rogue APs: ' + str(rogue_aps) + '\n'
                parameters_dict['rogue_aps'] = rogue_aps
                text = text + 'Number of nearby APs: ' + str(len(ap.nearby_aps)) + '\n'
                parameters_dict['nearby_aps'] = len(ap.nearby_aps)
                nearby_aps_same_chan = len([nearbyap for nearbyap in ap.nearby_aps if
                                                                               ap.channel_assignment_information_recommended_best_channel == nearbyap.channel])
                text = text + 'Number of SAME channel nearby APs: ' + str(nearby_aps_same_chan) + '\n'
                parameters_dict['nearby_aps_same_chan'] = nearby_aps_same_chan
                for nearby_ap in ap.nearby_aps:
                    if ap.channel_assignment_information_recommended_best_channel == nearby_ap.channel:
                        text = text + '!!!' + get_ap_name_by_bssid(nearby_ap.mac_address[:-1] + '0',
                                                                   wlc_config) + ' ' + nearby_ap.channel + ' ' + nearby_ap.rssi + ' \n'
                    else:
                        text = text + get_ap_name_by_bssid(nearby_ap.mac_address[:-1] + '0',
                                                           wlc_config) + ' ' + nearby_ap.channel + ' ' + nearby_ap.rssi + ' \n'

                notes_dict[ap.name[:-6]] = text #Removing _slot1 from name
                parameters_per_ap_dict[ap.name[:-6]] = parameters_dict
    else:
        for ap in wlc_config.ap_rf_5:
            if 'slot1' in ap.name:
                text = ''
                parameters_dict = {}
                if len([nearbyap for nearbyap in ap.nearby_aps if
                        ap.channel_assignment_information_recommended_best_channel == nearbyap.channel]) > 3:
                    text = '!!!!' + '\n'
                try:
                    text = text + 'Recommended channel (5GHz): ' + ap.channel_assignment_information_recommended_best_channel + '\n'
                    text = text + 'Channel change count: ' + ap.channel_assignment_information_channel_change_count + '\n'
                    parameters_dict['chan_changes'] = int(ap.channel_assignment_information_channel_change_count)
                    text = text + 'Channel utilization (5GHz): ' + ap.load_information_channel_utilization + '\n'
                    parameters_dict['chan_util_5G'] = int(ap.load_information_channel_utilization.split('%')[0])
                    text = text + 'Number of clients: ' + ap.load_information_attached_clients + '\n'
                    parameters_dict['clients'] = int(ap.load_information_attached_clients.split(' ')[0])
                    rogue_aps = wlcp.number_of_rogue_aps(wlc_config, ap.name.split('_')[0])
                    text = text + 'Number of rogue APs: ' + str(rogue_aps) + '\n'
                    parameters_dict['rogue_aps'] = rogue_aps
                    text = text + 'Number of nearby APs: ' + str(len(ap.nearby_aps)) + '\n'
                    parameters_dict['nearby_aps'] = len(ap.nearby_aps)
                    nearby_aps_same_chan = len([nearbyap for nearbyap in ap.nearby_aps if
                                                                                   ap.channel_assignment_information_recommended_best_channel == nearbyap.channel])
                    text = text + 'Number of SAME channel nearby APs: ' + str(nearby_aps_same_chan) + '\n'
                    parameters_dict['nearby_aps_same_chan'] = nearby_aps_same_chan
                except:
                    logger.debug(str(ap.name) + ' data not fully parsed')
                for nearby_ap in ap.nearby_aps:
                    if ap.channel_assignment_information_recommended_best_channel == nearby_ap.channel:
                        text = text + '!!!' + get_ap_name_by_bssid(nearby_ap.mac_address[:-1] + '0',
                                                                   wlc_config) + ' ' + nearby_ap.channel + ' ' + nearby_ap.rssi + ' \n'
                    else:
                        text = text + get_ap_name_by_bssid(nearby_ap.mac_address[:-1] + '0',
                                                           wlc_config) + ' ' + nearby_ap.channel + ' ' + nearby_ap.rssi + ' \n'

                notes_dict[ap.name[:-6]] = text #Removing _slot1 from name
                parameters_per_ap_dict[ap.name[:-6]] = parameters_dict
    return notes_dict, parameters_per_ap_dict

def coloration(ap_parameters, parameter):
    #Returns color of AP based on defined criteria
    color_code = {'RED': '#FF0000', 'YELLOW': '#FFE600', 'GREEN': '#00FF00', 'EMPTY': None}
    #This dictionary defines colouring rules, change values for customization
    #If the value is higher than defined, then this color is chosen
    colouring_scheme = {
        'chan_util_5G': {'RED': 40, 'YELLOW': 20, 'GREEN': 0},
        'chan_changes': {'RED': 20, 'YELLOW': 10, 'GREEN': 0},
        'clients': {'RED': 40, 'YELLOW': 20, 'GREEN': 0},
        'rogue_aps': {'RED': 10, 'YELLOW': 5, 'GREEN': 0},
        'nearby_aps': {'RED': 15, 'YELLOW': 10, 'GREEN': 0},
        'nearby_aps_same_chan': {'RED': 3, 'YELLOW': 2, 'GREEN': 0},
    }
    if ap_parameters[parameter] > colouring_scheme[parameter]['RED']:
        color = 'RED'
    elif ap_parameters[parameter] > colouring_scheme[parameter]['YELLOW']:
        color = 'YELLOW'
    elif ap_parameters[parameter] > colouring_scheme[parameter]['GREEN']:
        color = 'GREEN'
    else:
        color = 'EMPTY'
    logger.debug('Parameter of choice is: ' + parameter + ', value is: '+str(ap_parameters[parameter]) + ', chosen color is: ' + color)
    return color_code[color]

def tagging(ap_parameters):
    #Returns a list of tags and its values for AP based on the values of parameters
    tags_list = []
    predefined_values = {
        'rogue_aps': {'high': 10,
                      'medium': 5,
                      'low': 0},
        'chan_util_5G':
            {'high': 40,
             'medium': 20,
             'low': 0},
        'clients':
            {'high': 40,
             'medium': 20,
             'low': 0},
        'chan_changes':
            {'high': 20,
             'medium': 10,
             'low': 0},
        'nearby_aps':
            {'high': 15,
             'medium': 10,
             'low': 0},
        'nearby_aps_same_chan':
            {'high': 3,
             'medium': 2,
             'low': 0},}

    predefined_tags = {
        'rogue_aps': {'high': 'b38ee9a7-edfb-4375-bafc-a851ad341e62', #'rogue_aps_10+'
                      'medium': 'f77ab560-44af-4edb-a7e5-952216e680ac', #'rogue_aps_5-10'
                      'low': 'ad4c0430-e0f3-471a-b050-b3f8e7cb09b0'},#'rogue_aps_0-5'
        'chan_util_5G':
                    {'high': 'fee4aea7-0ef5-4016-a323-158f5ad4d78f',#'chan_util_5G_40+'
                     'medium': 'c85acc30-213f-4a72-aa9b-02e14f20bbb6',#'chan_util_5G_20-40'
                     'low': 'ebd9290d-0926-4568-8fcc-afa6addaa379'},#'chan_util_5G_0-20'
        'clients':
                    {'high': '1af88617-95b4-4aaf-9670-9b7fb26d2f9a',#'clients_40+'
                     'medium': 'db58ec81-defa-4e91-a4f7-c764463574e9',#'clients_20-40'
                     'low': 'ef043d58-9c42-4707-862c-49a872a5dc02'},#'clients_0-20'
        'chan_changes':
                    {'high': '8e8fa88b-bbbc-45d7-8fb2-00782f51d4a0',#'chan_changes_20+'
                     'medium': '766287b3-7a88-4a92-b7ce-1b1fa5659e70',#'chan_changes_10-20'
                     'low': 'c60a6091-46d7-4fb1-91dc-9ceba7334120'},#'chan_changes_0-10'
        'nearby_aps':
                    {'high': '4d04e5f5-3853-48cd-9267-a86a544ae69b',#'nearby_aps_15+'
                     'medium': '3a791adc-5487-4d9d-a5f7-375b597dac5a',#'nearby_aps_10-15'
                     'low': '5a6b3153-1a0f-42ca-9db9-d8f96f46ddbd'},#'nearby_aps_0-10'
        'nearby_aps_same_chan':
                    {'high': '9e8e4862-2ecf-46ca-a58f-4e218fc45cf7',#'nearby_aps_same_chan_3+'
                     'medium': 'de988216-ea2b-49e2-bb73-aea373382098',#'nearby_aps_same_chan_2-3'
                     'low': '16d0e42b-0c50-41e9-ba64-3f3b951bf73b'}}#'nearby_aps_same_chan_0-2'
    logging_tags = ''
    for parameter, value in ap_parameters.items():
        if value > predefined_values[parameter]['high']:
            tags_list.append({"tagKeyId": predefined_tags[parameter]['high'], "value": value})
            logging_tags = logging_tags + parameter + ': high , value: ' + str(value)
        elif value > predefined_values[parameter]['medium']:
            tags_list.append({"tagKeyId": predefined_tags[parameter]['medium'], "value": value})
            logging_tags = logging_tags + parameter + ': medium , value: ' + str(value)
        elif value >= predefined_values[parameter]['low']:
            tags_list.append({"tagKeyId": predefined_tags[parameter]['low'], "value": value})
            logging_tags = logging_tags + parameter + ': low , value: ' + str(value)

    logger.debug('Tag list is defined ' + logging_tags)
    return tags_list

def add_ap_notes(project_filename, notes_dict, ap_parameters, parameter_of_choice):
    color_codes = {'RED': '#FF0000', 'YELLOW': '#FFE600', 'GREEN': '#00FF00'}
    p = pathlib.Path('Ekahau/')
    p.mkdir(parents=True, exist_ok=True)
    working_directory = pathlib.Path.cwd()
    temp_folder_filepath = working_directory / 'Ekahau'
    # Load & Unzip the Ekahau Project File
    with zipfile.ZipFile(project_filename, 'r') as myzip:
        myzip.extractall(temp_folder_filepath)

        # Load the accessPoints.json file into the accessPoints dictionary
        with myzip.open('accessPoints.json') as json_file:
            accessPoints = json.load(json_file)

        # Load the notes.json file into the notes dictionary in case the file exists
        notes_file_path = temp_folder_filepath / 'notes.json'

        if not notes_file_path.is_file():
            notes_file_path.touch()
            content = '''{
  "notes": [
    {
      "text": "Test_note",
      "history": {
        "createdAt": "2023-12-07T17:20:03.062Z",
        "createdBy": "Roman P"
      },
      "imageIds": [],
      "id": "9599c5a7-fc5f-4731-9aaf-d36e1015f847",
      "status": "CREATED"
    }
  ]
}
            '''
            notes_file_path.write_text(content)
            with open(notes_file_path, 'r') as json_file:
                notes = json.load(json_file)
        else:
            with myzip.open('notes.json') as json_file:
                notes = json.load(json_file)

        # Load the tagKeys.json file into the tags dictionary in case the file exists, if not - fulfill it with pre-defined tags
        tag_keys_file_path = temp_folder_filepath / 'tagKeys.json'

        if not tag_keys_file_path.is_file():
            tag_keys_file_path.touch()
            tags_content = '''{
  "tagKeys": [
    {
      "key": "rogue_aps_5-10",
      "id": "f77ab560-44af-4edb-a7e5-952216e680ac",
      "status": "CREATED"
    },
    {
      "key": "rogue_aps_0-5",
      "id": "ad4c0430-e0f3-471a-b050-b3f8e7cb09b0",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_0-10",
      "id": "5a6b3153-1a0f-42ca-9db9-d8f96f46ddbd",
      "status": "CREATED"
    },
    {
      "key": "chan_util_5G_20-40",
      "id": "c85acc30-213f-4a72-aa9b-02e14f20bbb6",
      "status": "CREATED"
    },
    {
      "key": "clients_40+",
      "id": "1af88617-95b4-4aaf-9670-9b7fb26d2f9a",
      "status": "CREATED"
    },
    {
      "key": "chan_changes_10-20",
      "id": "766287b3-7a88-4a92-b7ce-1b1fa5659e70",
      "status": "CREATED"
    },
    {
      "key": "chan_util_5G_0-20",
      "id": "ebd9290d-0926-4568-8fcc-afa6addaa379",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_15+",
      "id": "4d04e5f5-3853-48cd-9267-a86a544ae69b",
      "status": "CREATED"
    },
    {
      "key": "chan_changes_20+",
      "id": "8e8fa88b-bbbc-45d7-8fb2-00782f51d4a0",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_10-15",
      "id": "3a791adc-5487-4d9d-a5f7-375b597dac5a",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_same_chan_3+",
      "id": "9e8e4862-2ecf-46ca-a58f-4e218fc45cf7",
      "status": "CREATED"
    },
    {
      "key": "chan_util_5G_40+",
      "id": "fee4aea7-0ef5-4016-a323-158f5ad4d78f",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_same_chan_2-3",
      "id": "de988216-ea2b-49e2-bb73-aea373382098",
      "status": "CREATED"
    },
    {
      "key": "chan_changes_0-10",
      "id": "c60a6091-46d7-4fb1-91dc-9ceba7334120",
      "status": "CREATED"
    },
    {
      "key": "clients_0-20",
      "id": "ef043d58-9c42-4707-862c-49a872a5dc02",
      "status": "CREATED"
    },
    {
      "key": "rogue_aps_10+",
      "id": "b38ee9a7-edfb-4375-bafc-a851ad341e62",
      "status": "CREATED"
    },
    {
      "key": "clients_20-40",
      "id": "db58ec81-defa-4e91-a4f7-c764463574e9",
      "status": "CREATED"
    },
    {
      "key": "nearby_aps_same_chan_0-2",
      "id": "16d0e42b-0c50-41e9-ba64-3f3b951bf73b",
      "status": "CREATED"
    }
  ]
}
                    '''
            tag_keys_file_path.write_text(tags_content)
            with open(tag_keys_file_path, 'r') as tag_json_file:
                tags = json.load(tag_json_file)
        else:
            with myzip.open('tagKeys.json') as tag_json_file:
                tags = json.load(tag_json_file)
                #Add predefined tags to existing tags
                predefined_tags = {'tagKeys':[{'key': 'rogue_aps_5-10', 'id': 'f77ab560-44af-4edb-a7e5-952216e680ac', 'status': 'CREATED'}, {'key': 'rogue_aps_0-5', 'id': 'ad4c0430-e0f3-471a-b050-b3f8e7cb09b0', 'status': 'CREATED'}, {'key': 'nearby_aps_0-10', 'id': '5a6b3153-1a0f-42ca-9db9-d8f96f46ddbd', 'status': 'CREATED'}, {'key': 'chan_util_5G_20-40', 'id': 'c85acc30-213f-4a72-aa9b-02e14f20bbb6', 'status': 'CREATED'}, {'key': 'clients_40+', 'id': '1af88617-95b4-4aaf-9670-9b7fb26d2f9a', 'status': 'CREATED'}, {'key': 'chan_changes_10-20', 'id': '766287b3-7a88-4a92-b7ce-1b1fa5659e70', 'status': 'CREATED'}, {'key': 'chan_util_5G_0-20', 'id': 'ebd9290d-0926-4568-8fcc-afa6addaa379', 'status': 'CREATED'}, {'key': 'nearby_aps_15+', 'id': '4d04e5f5-3853-48cd-9267-a86a544ae69b', 'status': 'CREATED'}, {'key': 'chan_changes_20+', 'id': '8e8fa88b-bbbc-45d7-8fb2-00782f51d4a0', 'status': 'CREATED'}, {'key': 'nearby_aps_10-15', 'id': '3a791adc-5487-4d9d-a5f7-375b597dac5a', 'status': 'CREATED'}, {'key': 'nearby_aps_same_chan_3+', 'id': '9e8e4862-2ecf-46ca-a58f-4e218fc45cf7', 'status': 'CREATED'}, {'key': 'chan_util_5G_40+', 'id': 'fee4aea7-0ef5-4016-a323-158f5ad4d78f', 'status': 'CREATED'}, {'key': 'nearby_aps_same_chan_2-3', 'id': 'de988216-ea2b-49e2-bb73-aea373382098', 'status': 'CREATED'}, {'key': 'chan_changes_0-10', 'id': 'c60a6091-46d7-4fb1-91dc-9ceba7334120', 'status': 'CREATED'}, {'key': 'clients_0-20', 'id': 'ef043d58-9c42-4707-862c-49a872a5dc02', 'status': 'CREATED'}, {'key': 'rogue_aps_10+', 'id': 'b38ee9a7-edfb-4375-bafc-a851ad341e62', 'status': 'CREATED'}, {'key': 'clients_20-40', 'id': 'db58ec81-defa-4e91-a4f7-c764463574e9', 'status': 'CREATED'}, {'key': 'nearby_aps_same_chan_0-2', 'id': '16d0e42b-0c50-41e9-ba64-3f3b951bf73b', 'status': 'CREATED'}]}
                tags.update(predefined_tags)

    for ap_name in notes_dict.keys():
            logger.debug('Checking if AP exists in survey project file for: ' + ap_name)

            for ap in accessPoints['accessPoints']:
                if ap_name == ap['name']:
                    logger.debug('AP found: ' + ap_name)
                    #Add notes to AP dictionary
                    note_id = unique_id()
                    notes['notes'].append({
                        "text": notes_dict[ap_name],
                        "history": {
                            "createdAt": "2020-12-30T00:00:12.345Z",
                            "createdBy": wlcp.base64.b64decode('Um9tYW4gQ1dORSM5Mg==').decode()
                        },
                        "imageIds": [],
                        "id": note_id,
                        "status": "CREATED"
                    })
                    if 'note_Ids' in ap:
                        ap['noteIds'].append(note_id)
                    else:
                        ap['noteIds'] = []
                        ap['noteIds'].append(note_id)
                    logger.debug('Added noteId ' + str(note_id) + ' to AP ' + ap_name)
                    #Add tags here
                    logger.debug('Adding tags for AP with name: ' + ap_name)
                    tags_list = tagging(ap_parameters[ap_name])
                    if 'tags' in ap:
                        for tag in tags_list:
                            if not tag["tagKeyId"] in ap['tags']:
                                ap['tags'].append(tag)
                    else:
                        ap['tags'] = []
                        for tag in tags_list:
                            if not tag["tagKeyId"] in ap['tags']:
                                ap['tags'].append(tag)
                    #Add color to AP dictionary based on coloration rules
                    logger.debug('Choosing color for AP with name: ' + ap_name)
                    color_code = coloration(ap_parameters[ap_name],parameter_of_choice)
                    ap['color'] = color_code

    # Write the changes into the accessPoints.json File
    filepath = temp_folder_filepath / 'accessPoints.json'
    with filepath.open(mode="w", encoding="utf-8") as file:
        json.dump(accessPoints, file, indent=4)
    logger.debug('New accessPoints.json file is written')
    # Write the changes into the notes.json File
    filepath = temp_folder_filepath / 'notes.json'
    with filepath.open(mode="w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4)
    logger.debug('New notes.json file is written')
    # Write the changes into the tagKeys.json File
    filepath = temp_folder_filepath / 'tagKeys.json'
    with filepath.open(mode="w", encoding="utf-8") as file:
        json.dump(tags, file, indent=4)
    logger.debug('New tagKeys.json file is written')

    # Create a new version of the Ekahau Project
    new_filename = pathlib.Path(str(project_filename) +'_modified')
    shutil.make_archive(new_filename, 'zip', temp_folder_filepath)
    my_file = pathlib.Path(str(new_filename)+'.zip')
    my_file.rename(my_file.with_suffix('.esx'))
    logger.debug('New project file is ready to use, filename is ' + str(my_file.with_suffix('.esx')))

    # Cleaning Up
    shutil.rmtree(temp_folder_filepath)
    logger.debug('Working folder is cleaned')

    return str(my_file.with_suffix('.esx'))

def main():
    if len(sys.argv) == 4 and int(sys.argv[3]) >0 and int(sys.argv[3]) < 7:
        logger.debug('Correct number of arguments supplied')
        wlc_config_filepath = home / sys.argv[1]
        project_filepath = home / sys.argv[2]
        parameter_of_choice = int(sys.argv[3])
        parameters_scheme = {
            2: 'chan_util_5G',
            3: 'chan_changes',
            1: 'clients',
            4: 'rogue_aps',
            5: 'nearby_aps',
            6: 'nearby_aps_same_chan'
        }
        wlc = wlcp.parse_file(wlc_config_filepath)
        wlc_config = next(iter(wlc.values()))
        ap_notes, ap_parameters_dict = get_ap_notes(wlc_config)
        if len(ap_notes) > 0:
            add_ap_notes(project_filepath, ap_notes, ap_parameters_dict, parameters_scheme[parameter_of_choice])
        else:
            print('No AP notes were parsed from the supplied WLC config file')
            logger.debug('No AP notes were parsed from the supplied WLC config file')
    else:
        print('Incorrect number of arguments supplied, please check README for instructions')
        logger.debug('!!! INCorrect number of arguments supplied: ' + str(len(sys.argv)))

if __name__ == "__main__":
    main()

