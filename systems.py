import requests
import constants
import io
import os
import math
import zipfile
from zipfile import ZipFile
from tqdm import tqdm
from pathlib import Path
from googleapiclient.http import MediaIoBaseDownload
from time import sleep
from colorama import init
from colorama import Fore, Style
init()  # Colorama init

def prompt_duplicate_file(file_path, mode:str):
    while True:
        if mode == "compress":
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                f": Zip file '{file_path}' already exists.")
            print("// RN = Rename file (Adds a number next to it).")
            print("// RP = Replace file.")
        else:
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                f": Extraction folder '{file_path}' already exists.")
            print("// RN = Rename folder (Adds a number next to it).")
            print("// RP = Replace folder.")
        choice = input("=> ").strip().upper()
        
        if choice == "RN" or choice == "RP":
            break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + ": Choose a valid option!")
            continue
    return choice
    
def compact_directory(file_dir): 
    print("\nFile identified as a directory. Starting compression process...", end="")
    sleep(0.5)
    # FIXME: String vazia na hora de colocar o diretório para compactar irá retornar erro
    target_path = Path(file_dir).with_suffix(".zip")
    local_filename = target_path.name
    folder_size = sum(file.stat().st_size for file in file_dir.rglob('*') if file.is_file())
    print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    
    if target_path.exists():
        choice = prompt_duplicate_file(target_path, "compress")
      
        if choice == "RN":
            counter = 0
            print("\nRenaming file...", end="")
            path = target_path.parent.absolute() 
            while target_path.exists():
                counter += 1
                pure_filename = target_path.stem.strip(f"({counter - 1})")
                target_path = Path(f"{path}/{pure_filename}({counter})").with_suffix(".zip")
            local_filename = target_path.name
            print(Fore.GREEN + "Done!\n" + Style.RESET_ALL)
          
    with ZipFile(target_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
        progress_bar = load_progress_bar(description="Compressing", 
                                         total_file_size=folder_size, 
                                         folder_mode=True)
        for item in file_dir.rglob("*"):       
            current_file_path = str(item.relative_to(file_dir))
            progress_bar.set_postfix({"File": item.name}, refresh=True)
            if item.is_file():
                with open(item, "rb") as input_file, zfile.open(current_file_path, "w") as output_file:
                    while True:
                        chunk = input_file.read(524288)
                        progress_bar.update(len(chunk))
                        if not chunk:
                           break
                        output_file.write(chunk)
            else:
                zfile.write(item, item.relative_to(file_dir))
            
    file_metadata = {"name" : local_filename, 
                     "mimetype" : "application/zip"}
    file_created = True
    return target_path, local_filename, file_metadata, file_created

def extract_file(zipfile_path, extract_folder_path): 
    if extract_folder_path.exists():
        choice = prompt_duplicate_file(extract_folder_path, "extract")
        
        if choice == "RN":
            counter = 0
            print("\nRenaming file...", end="")
            path = extract_folder_path.parent.absolute()
            while extract_folder_path.exists():
                counter += 1
                folder_name = extract_folder_path.name.strip(f"({counter - 1})")
                extract_folder_path = Path(f"{path}/{folder_name}({counter})")
            print(Fore.GREEN + "Done!\n" + Style.RESET_ALL)
    
    
    with ZipFile(zipfile_path, "r", allowZip64=True) as zfile:
        total_size = sum(zinfo.file_size for zinfo in zfile.filelist) 
        progress_bar = load_progress_bar(description="Extracting", total_file_size=total_size, folder_mode=True)
               
        for item in zfile.infolist():
            """ Duct tape fix for a problem I spent days trying to solve, but didn't manage to 
            get a good solution. Here's the problem:
            
            As of Python 3.10, the ZipFile module only accepts two encoding formats when it 
            comes to filenames in a zip file. These are 'cp437' and 'utf-8'. How ZipFile switches 
            between these two encoding types is a mystery to me, but from my testing, if you zip 
            a file using ZipFile, and it has utf-8 characters inside, then it will use utf-8 
            encoding, otherwise, it will use cp437. ZipFile will also use cp437 when extracting 
            zip files not created by ZipFile, even if they have utf-8 chars. So if you want to
            extract a file using ZipFile utf-8 encoding for file names, you'll be only able do 
            that if you zip (using ZipFile) a file that has utf-8 characters, otherwise, you better 
            hope all the characters in your language are in the cp437 char table.
            
            When reading a filename using cp437, depending on the characters present in the 
            filename, you will get wrong encoded chars (mojibake). For me, what was supposed 
            to be 'ã' became '╞' and 'õ' became 'Σ', as this chars are not supported by cp437.
            
            This fix is only useful for my native language (pt-BR), as 'ã'/'õ' is used a lot, 
            and all other characters are covered by cp437. This will be problem if your language 
            has a lot of characters not covered by cp437. Other fixes I tried was using a module 
            named 'ftfy', or using a combination of encode/decode methods, but none of them 
            worked and just returned mojibake.
            
            If you are still reading this and plan to use this code on your own project,
            changes in the code below may be necessary. Let me know if you have a better
            way to fix this (please, as this solution is really ugly!).
            
            If you are reading this after Python 3.11 has been released, ZipFile added a 
            'metadata_encoding' argument in the ZipFile constructor, so maybe that can fix
            the encoding problem. """ 
            item.filename = item.filename.replace("╞","ã").replace("Σ","õ")
            progress_bar.set_postfix({"File": item.filename.rsplit("/", 1)[-1]}, refresh=True)
            zfile.extract(item, extract_folder_path)
            progress_bar.update(item.file_size)
    progress_bar.close()
     
def convert_filesize(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes == 0:
        return "0B"
    size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024))) # i = index of size_unit tuple
    # unit_bytesize = 1 unit of size, in bytes.
    # i.e if the unit is in MB, it will store 1MB, in bytes (1048576 bytes)).
    unit_bytesize = math.pow(1024, i)
    size_converted = round(size_bytes / unit_bytesize, 2)
    return f"{size_converted} {size_unit[i]}"

def create_gdrive_copy(file_metadata, drive, drive_filename, file):
    file_metadata["name"] = f"Copy of {drive_filename}"
    request = drive.files().create(body=file_metadata, media_body=file)
    return request

def upload_file(file_size, request):
    print("\nStarting upload...", end="")
    sleep(1)
    print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    progress_bar = load_progress_bar("Uploading", file_size) 
    response = None
    while response is None:
        status, response = request.next_chunk()
        """ If the file is smaller than the chunksize (100MB), it will be
        completely uploaded in a single chunk, skipping the if below.
        Trying to access status.resumable_progress after the
        file has been completely uploaded will raise AttributeError. """ 
        if status:
            progress_bar.n = status.resumable_progress # Keeps track of the total size transfered.
            progress_bar.refresh()

        # Updates bar when the file is uploaded in a single chunk.
        if status is None:
            progress_bar.n = file_size
            progress_bar.refresh() 
    progress_bar.close()

def remove_localfile(file_dir):
    if file_dir.exists:
        print("\nRemoving created ZIP file from system...", end="")
        sleep(1)
        file_dir.unlink()
        print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    else:
        print(f"\n" + Fore.RED + "ERROR" + Style.RESET_ALL + 
              f": File path '{file_dir}' doesn't exist. Skipping operation...\n")

def list_drive_files(search_results, GOOGLE_WORKSPACE_MIMETYPES):
    terminal_size = os.get_terminal_size().columns - 1
    counter = 1
    print("\nThe following files were found:")
    print("-" * terminal_size)
    print(f"{'Num':^4}  | {'Type':^14} | {'Size':^11}    |   File name")
    print("-" * terminal_size)
    for drive_file in search_results:
        try:
            if drive_file["mimeType"] in constants.NO_SIZE_TYPES:
                print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {'-----':^11} --->   {drive_file['name']}")
    
            elif drive_file["mimeType"] in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
                print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}") 
        # Sometimes even for supported mimetypes like docs or spreadsheet, 
        # the API will not return a "size" key. The except handles this cases.
        except KeyError:
            print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {'-----':^11} --->   {drive_file['name']}")
        
        if drive_file["mimeType"] not in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
            print(f"#{counter:>4} | {'File':^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}")
        counter += 1
    print("-" * terminal_size)
    print(Fore.YELLOW + "WARNING" + Style.RESET_ALL +
          ": Files tagged with '*' are not supported for download.")
    
def list_skipped_files(skipped_files, GOOGLE_WORKSPACE_MIMETYPES):
    terminal_size = os.get_terminal_size().columns - 1
    counter = 1
    print("\nThe following items were skipped:")
    print("-" * terminal_size)
    print(f"{'Num':^4}  | {'Type':^14}    |  File name")
    print("-" * terminal_size)
    for drive_file in skipped_files:
        print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} --->  {drive_file['name']}")
        counter += 1
    print("-" * terminal_size)
    print("Download the files directly from Google Drive if you need them.")
    
def list_folders(search_results):
    terminal_size = os.get_terminal_size().columns - 1
    counter = 1
    print("\nThe following folders were found:")
    print("-" * terminal_size)
    print(f"{'Num':^4}  |  Folder name")
    print("-" * terminal_size)
    for drive_file in search_results:
        print(f"#{counter:>4} |  {drive_file['name']}")
        counter += 1
    print("-" * terminal_size)
    
def print_file_stats(file_name=None, file_size=None, folder_mode=False, folder_stats=None):
    terminal_size = os.get_terminal_size().columns - 1
    if folder_mode == True:
        print("-" * terminal_size)
        for key, value in folder_stats.items():
            # folder_size_calc needs to return the total folder size in bytes, but we
            # don't want to print it in here, as we're already printing the converterd
            # folder size.
            if key != "Bytes":
                print(f"// {key}: {value}")
        print("-" * terminal_size)
    else:
        print("-" * terminal_size) 
        print(f"// File: {file_name}")
        print(f"// Size: {convert_filesize(int(file_size))}")
        print(("-" * terminal_size) + "\n")
        sleep(1)

def prepare_directory(download_dir, gdrive_folder_name):
    folder_path = Path.joinpath(download_dir, gdrive_folder_name)
    try:
        if not folder_path.exists():
            folder_path.mkdir()
            return folder_path
        else:
            return folder_path

    except OSError:
        print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL +
              ": Invalid character in folder name. Rename the folder to remove the invalid characters [\\ / ? : * < > | \"].")
        print("Aborting operation...")
        sleep(0.5)
        exit()

def check_download_dir(file_name, download_dir):
        while True:
            if Path.joinpath(download_dir, file_name).exists():
                print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                      f": File '{file_name}' is already present in '{download_dir}'.")
                print("// S = Replace file.")
                print("// C = Download as copy.")
                choice = input("=> ").strip().upper()

                if choice != "S" and choice != "C":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.RED + "ERROR" + Style.RESET_ALL +f": {choice} is not a valid choice.\n")

                elif choice == "S":
                        return file_name

                else:
                    return  f"Copy of {file_name}"
            # Default case
            else:
                return file_name

def load_progress_bar(description, total_file_size=None, folder_mode=False):
    if folder_mode == False:
        bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}]"
    elif folder_mode == True and total_file_size is None:
        bar_format = "{desc}: {n_fmt}B/Unknown [{elapsed}, {rate_fmt}]{postfix:<70}"    
    else:
       bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}]{postfix:<70}"
        
    if total_file_size is None:
        return tqdm(desc=description, miniters=1, bar_format=bar_format, 
                    unit="B", unit_scale=True, unit_divisor=1024, dynamic_ncols=True)
    else:   
        return tqdm(total=int(total_file_size), desc=description, miniters=1, bar_format=bar_format, 
                    unit="B", unit_scale=True, unit_divisor=1024, dynamic_ncols=True)
class DownloadSystem:
    total_skipped = 0
    skipped_files = []
    def __init__(self, progress_bar=None, unknown_folder_size=False, folder_mode=False, access_token=None):
        self.progress_bar = progress_bar
        self.unknown_folder_size = unknown_folder_size
        self.unknown_folder_size = unknown_folder_size
        self.folder_mode = folder_mode
        self.access_token = access_token
                 
    def get_files(self, folder_id, directory, drive):
        search_results = []
        page_token = None
        while True:
            search_request = drive.files().list(corpora="user", pageToken=page_token, pageSize = 1000, 
                                                fields="nextPageToken, files(id, name, size, mimeType, exportLinks)", 
                                                q=f"'{folder_id}' in parents and trashed=false").execute()
            for item in search_request["files"]:
                search_results.append(item) 
            page_token = search_request.get("nextPageToken", None)
            if page_token is None:
                break
        for file in search_results:
            if file["mimeType"] == "application/vnd.google-apps.folder":
                # Precisa adicionar self nas chamadas ou apenas na definição?
                self.get_files(folder_id=file["id"], 
                               directory=prepare_directory(directory, file["name"]), 
                               drive=drive)
            else:
                self.download_file(drive, directory, file)       

    # Handles both single file downloads (as long as it's not Google Workspace type) and
    # folder file downloads.
    def download_file(self, drive, directory, file_info):
        # get handles google apps script type of file,
        # as it's downloadable but API doesn't return a file size.
        file_size = int(file_info.get("size", 0))
        file_path = Path.joinpath(directory, file_info["name"])

        if file_info["mimeType"] in constants.DRIVE_EXPORT_FORMATS.keys() and file_info["mimeType"] not in constants.UNSUPPORTED_MIMETYPES:
            self.progress_bar.set_postfix({"File": file_info["name"]}, refresh=True)
            file_path = f"{file_path}{constants.DRIVE_EXPORT_FORMATS[file_info['mimeType']][0]['extension']}"
            file = io.FileIO(file_path, "wb")
            if file_size > 10485760:
                self.download_by_http(file_info, file, 
                                format_mimetype=constants.DRIVE_EXPORT_FORMATS[file_info["mimeType"]][0]["mimetype"])
                return

            else:    
                export_mimetype = constants.DRIVE_EXPORT_FORMATS[file_info["mimeType"]][0]["mimetype"]
                request = drive.files().export_media(fileId=file_info["id"], mimeType=export_mimetype)

        elif file_info["mimeType"] in constants.UNSUPPORTED_MIMETYPES:
            DownloadSystem.total_skipped += 1
            DownloadSystem.skipped_files.append({"name": file_info["name"], 
                                                 "mimeType": file_info["mimeType"]})
            return

        # Else handles ordinary files that already have an extension in their name.
        else:
            self.progress_bar.set_postfix({"File": file_info["name"]}, refresh=True)
            request = drive.files().get_media(fileId=file_info["id"])
            file = io.FileIO(f"{file_path}", "w")
        
        downloader = MediaIoBaseDownload(file, request, chunksize=constants.CHUNK_SIZE)
        done = False
        while done == False:
            status, done = downloader.next_chunk()
            if self.folder_mode == True and self.progress_bar.total is not None:
                chunk = status.resumable_progress                        
                """ Folder size is calculated based on the size of the files inside
                the folder, but when exporting files to a different format, they
                can increase in size (depending on the format).
                Because of this change, the progress bar can surpass the maximum
                size value. The code below fix this behavior. """
                if (chunk + self.progress_bar.n) >= self.progress_bar.total:
                    self.progress_bar.n = self.progress_bar.total
                    self.progress_bar.refresh() 
                
                else:    
                    self.progress_bar.update(chunk)                   
            
            elif self.folder_mode == True and self.progress_bar.total is None:
                self.progress_bar.update(status.resumable_progress)
            
            else:
                self.progress_bar.n = status.resumable_progress
                self.progress_bar.refresh()

        if self.folder_mode == False:    
            self.progress_bar.close()
        file.close()

    def download_exported_file(self, file_info, drive, download_dir):
        pbar_loaded = False
        file_size = int(file_info.get("size", 0)) 
        export_formats = constants.DRIVE_EXPORT_FORMATS[file_info["mimeType"]]
        terminal_size = os.get_terminal_size().columns - 1
        while True:
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + ": Google Workspace file detected!")
            print(Fore.YELLOW + "WARNING" + Style.RESET_ALL +
                  f": File {file_info['name']} can't be downloaded directly and needs to be exported to another format beforehand.\n")
            print("Type one of the export formats below to download your file as the chosen format:")
            print("-" * terminal_size)
            for formats in export_formats:
                print(f"# {formats['format']}")
            print("-" * terminal_size)
            print(Fore.YELLOW + "IMPORTANT" + Style.RESET_ALL + ": Some types of files only support one type of export format.")            
            print(Fore.YELLOW + "IMPORTANT" + Style.RESET_ALL + ": This conversion won't affect the file's cloud version!\n")
            print("// A = Abort Operation.")
            choosed_format = input("=> ").strip().upper()
            
            if choosed_format == "A":
                os.system('cls' if os.name == 'nt' else 'clear')
                return choosed_format

            try:
                format_info = next(formats for formats in export_formats if choosed_format == formats["format"].upper())
                break
            except StopIteration:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(Fore.RED + "ERROR" + Style.RESET_ALL + f": {choosed_format} is not a valid format choice.\n")
                continue
        
        file_name = check_download_dir(f"{file_info['name']}{format_info['extension']}", download_dir)
        file = io.FileIO(f"{Path.joinpath(download_dir, file_name)}", "wb")
        
        # Google Drive export() method has a 10MB file size limit.
        # If the file is larger than 10MB, the program will use a
        # direct GET request with a export URL, instead of using export().
        if file_size > 10485760:
            self.download_by_http(file_info, file, format_info["mimetype"])

        else:
            request = drive.files().export_media(fileId=file_info["id"], mimeType=format_info["mimetype"])
            downloader = MediaIoBaseDownload(file, request, chunksize=constants.CHUNK_SIZE)
            done = False
            while done == False:
                status, done = downloader.next_chunk()
                # Different export formats have different total sizes, and because
                # download._total_size is None until next_chunk() is called, we have
                # to call load_progress_bar after at least one next_chunk() call.
                if pbar_loaded == False:
                    progress_bar = load_progress_bar("Downloading", downloader._total_size)
                    sleep(0.5)
                    pbar_loaded = True
                progress_bar.n = status.resumable_progress
                progress_bar.refresh()
        file.close()
    
    def download_by_http(self, file_info, file, format_mimetype=None):
        download_url = file_info["exportLinks"][format_mimetype] 
        header={'Authorization': 'Bearer ' + self.access_token}
        if self.folder_mode == False:
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + ": File is too big to use the export method.")
            print("Trying a direct download through HTTP GET request. This can take a while...")
        
        request = requests.get(download_url, headers=header, stream=True)
        file_size = len(request.content)
        total_transfered = 0
        if self.folder_mode == False:
            progress_bar = load_progress_bar("Downloading", file_size)
        for chunk in request.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                total_transfered += len(chunk)
                
                if self.folder_mode == False:
                    progress_bar.n = total_transfered
                    progress_bar.refresh()
                    
                else:
                    if self.progress_bar.total is not None:
                        if (self.progress_bar.n + len(chunk)) > self.progress_bar.total:
                            self.progress_bar.n = self.progress_bar.total
                            self.progress_bar.refresh() 
                            
                        else:    
                            self.progress_bar.update(len(chunk))
                    else:
                        self.progress_bar.update(len(chunk))
                        
        if self.folder_mode == False:
            progress_bar.close()
        file.close()