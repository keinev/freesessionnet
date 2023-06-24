import requests
import re
import json
import os
import hashlib


down_base_addr = "https://sessionnet.dessau.de/bi/"
download_path = "RIS2_PDF/"
json_file = "#dessau_base.json"

down_number_pattern = r'id=(\d+)'

with open(path_to_file, "r") as file:
    existing_data = json.load(file)

testfiles = []
    
for main_file in existing_data["sessions"]["308"]["main_files"]:
    testfiles.append(main_file["link"])
    
for sub_session in existing_data ["sessions"]["308"]["sub_sessions"]:
    testfiles.append(sub_session["sub_files"][0]["link"])
    
print(testfiles)
test_version = 1
    
for testfile in testfiles:
    match_id = re.search(down_number_pattern, testfile)
    file_number = match_id.group(1)
    
    address = "https://sessionnet.dessau.de/bi/" + testfile
    print(address)
    response = requests.get(address)
    if response.status_code == 200:
        filename = response.headers.get('content-disposition')
        filename = file_number + "-" + str(test_version) + "-" + filename[filename.find('"') + 1:-1]
    print(filename)
    h = hashlib.new('md5')
    h.update(response.content)
    print(h.hexdigest())
    print("")
    
    #open(path + filename, 'w').write(response.content)
