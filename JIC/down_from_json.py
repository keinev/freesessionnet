import requests
import re
import json
import hashlib
from datetime import datetime

down_number_pattern = r'id=(\d+)'


def hash_file_content(file_content):
    h = hashlib.new('md5')
    h.update(file_content)
    return h.hexdigest()


def load_edit(json_data, down_base_addr="https://sessionnet.dessau.de/bi/", download_path="RIS2_PDF/"):
    got_response = False
    got_version = False

    address = down_base_addr + json_data["link"]
    response = requests.get(address)
    if response.status_code == 200:
        got_response = True
        file_hash = str(hash_file_content(response.content))
        if json_data["hash"] != file_hash:
            got_version = True
            filename = response.headers.get('content-disposition')
            file_number = re.search(down_number_pattern, json_data["link"]).group(1)

            if json_data["version"] is not None and json_data["version"]:
                new_version = int(json_data["version"]) + 1
            else:
                new_version = 1
            fin_filename = file_number + "-" + str(new_version) + "-" + filename[filename.find('"') + 1:-1]
            fin_filename = str(fin_filename)
            file_hash = str(hash_file_content(response.content))
            down_time = str(datetime.now())
            new_version = str(new_version)

            json_data["name"] = fin_filename
            json_data["hash"] = file_hash
            json_data["version"] = new_version
            json_data["downloadtime"] = down_time

            try:
                with open(download_path + fin_filename, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Error: unable to write to file. {e}")
    return got_response, got_version, json_data


# -----------------------------------------------------------------
# just for test
download_path = "RIS2_PDF/"
json_file = "#dessau_base.json"
path_to_file = download_path + json_file
with open(path_to_file, "r") as file:
    existing_data = json.load(file)
testfiles = []
for i, main_file in enumerate(existing_data["sessions"]["308"]["main_files"]):
    got_response, new_version, new_json = load_edit(main_file)
    if not got_response:
        print(f'not able to call{main_file["link"]}')
    if not new_version:
        print(f'no new version for {main_file["name"]}')
    if got_response and new_version:
        existing_data["sessions"]["308"]["main_files"][i] = new_json
        with open(path_to_file, "w") as file:
            json.dump(existing_data, file, indent=4)