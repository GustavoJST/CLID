import requests
import constants
import io
import os, stat
import math
import zipfile
import json
import tarfile
from zipfile import ZipFile
from tqdm import tqdm
from pathlib import Path
from googleapiclient.http import MediaIoBaseDownload
from time import sleep
from colorama import init, Fore, Style
init()  # Colorama init

with open("settings.json", "r") as settings_json:
    settings = json.load(settings_json)

def prompt_duplicate_file(path, local_filename, mode=None):
    while True:
        if mode == "compress":
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                f": Compressed file '{local_filename}' already exists in '{path}'.")
            print("// RP = Replace file.")
            print("// RN = Rename file (Adds a number next to it).")
    
        elif mode == "extract":
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                f": Extraction folder '{local_filename}' already exists in '{path}'.")
            print("// RP = Replace folder.")
            print("// RN = Rename folder (Adds a number next to it).")
            
        else:
            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                f": File '{local_filename}' already exists in '{path}'.")
            print("// RP = Replace file.")
            print("// RN = Rename file (Adds a number next to it).")
            
        choice = input("=> ").strip().upper()
        
        if choice == "RN" or choice == "RP":
            break
        
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + ": Choose a valid option!")
            continue
        
    if choice == "RN":
        counter = 0
        print("\nRenaming file...", end="")
        file_path = Path.joinpath(path, local_filename)
        while file_path.exists():
            counter += 1 
      
            if mode == "extract":
                folder_name = local_filename.strip(f"({counter - 1})")
                file_path = Path(f"{path}/{folder_name}({counter})")
               
            else:
                suffix = Path(local_filename).suffixes
                joined_suffixes = "".join(suffix[0:])
                pure_filename = local_filename.removesuffix(joined_suffixes).strip(f"({counter - 1})")
                if mode == "compress":
                    file_path = Path(f"{path}/{pure_filename}({counter})").with_suffix(settings["preferred_compression_format"])
                else:
                    file_path = Path(f"{path}/{pure_filename}({counter})").with_suffix(joined_suffixes)

        local_filename = file_path.name        
        print(Fore.GREEN + "Done!" + Style.RESET_ALL)     
    return local_filename
        
def compact_directory(file_dir): 
    print("\nFile identified as a directory. Starting compression process...", end="")
    sleep(0.5)
    target_path = Path(file_dir).with_suffix(settings["preferred_compression_format"])
    local_filename = target_path.name
    folder_size = sum(file.stat().st_size for file in file_dir.rglob('*') if file.is_file())
    print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    
    if target_path.exists():
        local_filename = prompt_duplicate_file(Path(target_path).parent, local_filename, "compress")
        target_path = target_path.with_name(local_filename)
        
    progress_bar = load_progress_bar(description="Compressing", 
                                     total_file_size=folder_size, 
                                     folder_mode=True)
      
    if settings["preferred_compression_format"] == ".tar.gz":
        # Mudar compresslevel para 5 para ver se diminui um pouco o tempo de compactação. GarrsMod demorou +20min
        with tarfile.open(target_path,"w:gz", encoding="utf-8", compresslevel=6) as tar:
            for item in file_dir.rglob("*"):
                progress_bar.set_postfix({"File": item.name}, refresh=True)
                tar.add(item, item.relative_to(file_dir), recursive=False)
                if item.is_file():
                    progress_bar.update(item.stat().st_size)
                    
        file_metadata = {"name" : local_filename, 
                         "mimetype" : "application/gzip"}
    
    elif settings["preferred_compression_format"] == ".zip":     
        with ZipFile(target_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
            print()
            for item in file_dir.rglob("*"):       
                current_file_path = str(item.relative_to(file_dir))
                progress_bar.set_postfix({"File": item.name}, refresh=True)
                if item.is_file():
                    with open(item, "rb") as input_file, zfile.open(current_file_path, "w") as output_file:
                        while True:
                            chunk = input_file.read(1048576)
                            progress_bar.update(len(chunk))
                            if not chunk:
                                break
                            output_file.write(chunk)
                else:
                    zfile.write(item, item.relative_to(file_dir)) 
                    
        file_metadata = {"name" : local_filename, 
                         "mimetype" : "application/zip"}
    else:
        print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + 
              ": Invalid 'preferred_compression_format' setting in settings.json. Rename it to a valid option.")
        input("\nPress ENTER to exit.")
        exit()
            
    file_created = True
    return target_path, local_filename, file_metadata, file_created

def extract_file(compressed_file_path, extract_folder_path): 
    if extract_folder_path.exists():
        extract_folder_path = extract_folder_path.with_name(prompt_duplicate_file(extract_folder_path.parent, 
                                                                                  extract_folder_path.name, 
                                                                                  "extract"))
    if compressed_file_path.suffix == ".zip":
        with ZipFile(compressed_file_path, "r", allowZip64=True) as zfile:
            print("\nStarting extraction process...", end="")
            total_size = sum(zinfo.file_size for zinfo in zfile.filelist)
            print(Fore.GREEN + "Done!\n" + Style.RESET_ALL)
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
                
                If you're reading this after Python 3.11 has been released, ZipFile added a 
                'metadata_encoding' argument in the ZipFile constructor. Maybe that can fix
                the encoding problem. """ 
                item.filename = item.filename.replace("╞","ã").replace("Σ","õ")
                progress_bar.set_postfix({"File": item.filename.rsplit("/", 1)[-1]}, refresh=True)
                zfile.extract(item, extract_folder_path)
                progress_bar.update(item.file_size)
        progress_bar.close()
    
    else:
        with tarfile.open(compressed_file_path, "r:*", encoding="utf-8") as tar:
            print("\nStarting extraction process...", end="")
            total_size = sum(member.size for member in tar)
            print(Fore.GREEN + "Done!\n" + Style.RESET_ALL)       
            progress_bar = load_progress_bar(description="Extracting", 
                                                total_file_size=total_size, 
                                                folder_mode=True)
            try:
                Path(extract_folder_path).mkdir()
            except:
                pass
            
            for member in tar:
                progress_bar.set_postfix({"File": Path(member.name).name}, refresh=True)
            
                if member.isfile():
                    destination = Path(extract_folder_path) / member.name 
                    if not destination.parent.exists():
                        destination.parent.mkdir(parents=True, exist_ok=True)      
                    
                    try: 
                        tfobj, out, perms_changed = tar.extractfile(member), open(destination, "wb"), False   
                    # Allows extraction of read-only files.
                    except PermissionError:
                        os.chmod(destination, stat.S_IWRITE)
                        tfobj, out, perms_changed = tar.extractfile(member), open(destination, "wb"), True
                
                    while True:
                        chunk = tfobj.read(1048576)
                        if not chunk:
                            break
                        out.write(chunk)
                        progress_bar.update(len(chunk))
                    tfobj.close()
                    out.close()
                    if perms_changed:
                        os.chmod(destination, stat.S_IREAD)
                    
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

def upload_file(file_size, request):
    print("Starting upload...", end="")
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
        print("\nRemoving the compressed file from system...", end="")
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
    print(f"{'Num':^4}  | {'Type':^16} | {'Size':^11}    |   File name")
    print("-" * terminal_size)
    for drive_file in search_results:
        try:
            if drive_file["mimeType"] in constants.NO_SIZE_TYPES:
                print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^16} | {'-----':^11} --->   {drive_file['name']}")
    
            elif drive_file["mimeType"] in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
                print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^16} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}") 
        # Sometimes even for supported mimetypes like docs or spreadsheet, 
        # the API will not return a "size" key. The 'except' handles this cases.
        except KeyError:
            print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^16} | {'-----':^11} --->   {drive_file['name']}")
        
        if drive_file["mimeType"] not in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
            print(f"#{counter:>4} | {'File':^16} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}")
        counter += 1
    print("-" * terminal_size)
    print(Fore.YELLOW + "WARNING" + Style.RESET_ALL +
          ": Files tagged with '*' are not supported for download.")
    
def list_skipped_files(skipped_files, GOOGLE_WORKSPACE_MIMETYPES):
    terminal_size = os.get_terminal_size().columns - 1
    counter = 1
    print("\nThe following items were skipped:")
    print("-" * terminal_size)
    print(f"{'Num':^4}  | {'Type':^18}    |  File name")
    print("-" * terminal_size)
    for drive_file in skipped_files:
        print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^18} --->  {drive_file['name']}")
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


def load_progress_bar(description, total_file_size=None, folder_mode=False):
    if folder_mode == False:
        bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}]"  
    elif folder_mode == True and total_file_size is None:
        bar_format = "{desc}: {n_fmt}B/Unknown [{elapsed}, {rate_fmt}]{postfix:<60}"     
    else:
       bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}]{postfix:<45}"
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
            # Checks and replace invalid characters in file name
            for char in file["name"]:
                if char in constants.INVALID_FILENAME_CHARACTERS:
                    file["name"] = file["name"].replace(char, "_")
        
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
        # 'get' handles google apps script type of file,
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

        # Else handles ordinary files.
        else:
            self.progress_bar.set_postfix({"File": file_info["name"]}, refresh=True)
            request = drive.files().get_media(fileId=file_info["id"])
            file = io.FileIO(f"{file_path}", "wb")
        
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
        
        #tmp_path = check_download_dir(f"{file_info['name']}{format_info['extension']}", download_dir)
        file_name = prompt_duplicate_file(download_dir, f"{file_info['name']}{format_info['extension']}")
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