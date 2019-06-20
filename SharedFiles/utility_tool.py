'''
This is the utility function. It takes data from LibraryData.json and returns the results. The result is a list of dictionaries where is dictionary is the data for a single library.
'''

import json

def read_json_file(filenameLib):  
    main_array = []
    with open(filenameLib, 'r') as myfile:
        main_array = json.loads(myfile.read())    
    return main_array