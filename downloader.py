import requests
import threading

path = "RIS2 PDF/"
start_nbr = 250 # first is
end_nbr = 310000
batch_size = 10000
num_threads = (end_nbr - start_nbr) // batch_size

lock = threading.Lock()

def download_files(start, end):
    for i in range(start, end):
        address = "https://sessionnet.dessau.de/bi/getfile.asp?id=" + str(i) + "&type=do"
        print(address)
        response = requests.get(address)
        if response.status_code == 200:
            filename = response.headers.get('content-disposition')
            filename = str(i) + filename[filename.find('"') + 1:-1]
            with lock:
                open(path + filename, 'wb').write(response.content)
        else:
            print(response.status_code)

def main():
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

if __name__ == "__main__":
    main()
