import requests
import threading
import os

path_to_save = "RIS2 PDF/"
start_nbr = 250  # first is
end_nbr = 310000
batch_size = 10000
num_threads = (end_nbr - start_nbr) // batch_size

# for check_new
distance_new = 1000

lock = threading.Lock()


def download_files(start, end):
    for i in range(start, end):
        address = "https://sessionnet.dessau.de/bi/getfile.asp?id=" + str(i) + "&type=do"
        print(address)
        response = requests.get(address)
        if response.status_code == 200:
            filename = response.headers.get('content-disposition')
            filename = str(i) + filename[filename.find('"') + 1:-11]
            with lock:
                open(path_to_save + filename, 'w').write(response.content)
        else:
            print(response.status_code)


def main():
    # is empty
    if len(os.listdir(path_to_save)) == 0:
        threads = []
        for i in range(num_threads):
            start = start_nbr + (i * batch_size)
            end = start + batch_size
            thread = threading.Thread(target=download_files, args=(start, end))
            print("thread ", start, end)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        print("All threads have finished downloading.")
    else:
        # single thread because we have time?
        lst_folder_items = os.listdir(path_to_save)
        highest_number = 0
        for item in lst_folder_items:
            act_number = item[:item.find("-")]
            if int(act_number) > int(highest_number):
                highest_number = int(act_number)
        download_files(highest_number, (highest_number + distance_new))


if __name__ == "__main__":
    main()
