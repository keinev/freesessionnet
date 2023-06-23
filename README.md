# English: freeSessionNet ✊
A data explorer for the session net portal of Dessau-Roßlau.

All official documents from the city of Dessau-Roßlau are published on https://sessionnet.dessau.de/ which is basically unnavigatable. It is just a dump of various binary formats that are not searchable or readably accessible for the wider public. 

The aim of this project is to create a comprehensive searchable, analysable database of all public data.

The project consits out of 3 main components:
- Downloader: Repsonsible for downloading all the files from sessionnet and saving them
- Parser: Responsible for consuming the downloaded files, parsing them and saving them into a database
- Frontend: A user interface to the database that is accessible through a webbrowser.


# German: freeSessionNet ✊

Ein Datenexplorer für das Sessionnet-Portal von Dessau-Roßlau.

Alle offiziellen Dokumente der Stadt Dessau-Roßlau werden auf https://sessionnet.dessau.de/ veröffentlicht, das im Grunde genommen unübersichtlich ist. Es handelt sich einfach um eine Ansammlung von verschiedenen binären Formaten, die für die breite Öffentlichkeit nicht durchsuchbar oder lesbar zugänglich sind.

Ziel dieses Projekts ist es, eine umfassende durchsuchbare, analysierbare Datenbank aller öffentlichen Daten zu erstellen.


## downloader - How i think it should work
- instead of just try all document number, we should itterate over all main and sublinks, save meta and links in a JSON. This JSON acts like a database.
- then download all files by theese links, create a MD5 hash of the content so you are able to check later is the document content changed and download it again to compare whats changed.
- implent some checks for missing data

parts for the downloader will be
- the initial JSON builder
- the downloader
-- update names, hash and last_download_time
-- ofc download and name the files like FILEID-FILENAME_VERION.FILETYPE
- the update_checker
-- update the JSON file with new content

--- by SodaYodB
