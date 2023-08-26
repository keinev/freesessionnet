import pandas as pd

download_path = "RIS2_PDF/"
json_file = "#dessau_base.json"
path_to_file = download_path + json_file

def check_votes_persons(pd_json):
    vote_errors = 0
    for session_number, session_content in pd_json["sessions"].items():
        persons_registered = len(session_content.get("persons", []))
        
        for sub_session in session_content["sub_sessions"]:
            vote_sum = sum(int(vote_count) for vote_count in sub_session["votes"].values() if vote_count.isdigit())
            if vote_sum > persons_registered:
                vote_errors += 1
    return vote_errors


def check_missing_meta(pd_json):
    meta_errors = {}

    for session_number, session_content in pd_json["sessions"].items():
        for descr, meeting_meta in session_content["meeting"].items():
            if meeting_meta is not None:
                if len(meeting_meta) == 0:
                    append(meta_errors, descr)
            else:
                append(meta_errors, descr)

    return meta_errors


def check_persons(pd_json, year):
    all_person = {}

    for session_number, session_content in pd_json["sessions"].items():
        for person in session_content["persons"]:
            if session_content["meeting"]["date"][-4:] == str(year):
                append(all_person, person["name"])
    return sort_dict(all_person)


def check_all_requester(pd_json):
    all_requests = {}

    for session_number, session_content in pd_json["sessions"].items():
        for subfile_meta in session_content["sub_sessions"]:
            append(all_requests, subfile_meta["requester"])

    return sort_dict(all_requests)


def check_requester(pd_json, req_name):
    all_requests = []

    for session_number, session_content in pd_json["sessions"].items():
        for subfile_meta in session_content["sub_sessions"]:
            if subfile_meta["requester"] == req_name:
                all_requests.append(subfile_meta["desc"])
    return list(set(all_requests))


def check_all_places(pd_json):
    all_places = {}
    
    for session_number, session_content in pd_json["sessions"].items():
        #print(session_content["meeting"]["location"])
        append(all_places, session_content["meeting"]["location"])
    return sort_dict(all_places)


def sort_dict(person_dict):
    sorted_dict = dict(sorted(person_dict.items(), key=lambda item: item[1], reverse=True))
    return sorted_dict


def append(dictionary, key):
    if key not in dictionary:
        dictionary[key] = 1
    else:
        dictionary[key] += 1


def main():
    with open(path_to_file, "r") as file:
        pd_json = pd.read_json(file)
    
    print("-------- Errors with Votes:")
    print(check_votes_persons(pd_json))
    print("-------- Missing Meta:")
    print(check_missing_meta(pd_json))
    print("-------- Persons 2023:")
    print(check_persons(pd_json, 2023))
    print("-------- Requester:")
    print(check_all_requester(pd_json))
    print("-------- requests by a requester:")
    for line in (check_requester(pd_json, "FrFr")):
        print("++ " + line)
    print("-------- places:")
    print(check_all_places(pd_json))


if __name__ == "__main__":
    main()
