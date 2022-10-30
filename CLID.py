#!./CLID_env/Scripts/python

""" Pick one of the shebangs below (according to your operating system) 
and place it on the first line of the script:

Windows 
#!./CLID_env/Scripts/python

Linux
#!./CLID_env/bin/python """

import os
import constants
import systems
import json
from systems import DownloadSystem
from folder_size_calc import GoogleDriveSizeCalculate
from time import sleep
from pathlib import Path, WindowsPath, PosixPath
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from colorama import init, Fore, Style


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    access_token = creds.token
    init()  # Colorama init
    
    # Loads settings.json:
    # download_directory(string) = Absolute path of the directory you want your files to be downloaded.
    # upload_path(string) = Absolute path of a file you want to upload when in upload mode.
    # Useful if you don't want to be prompted for a download directory every time
    # or need to upload the same file every time.
    # shared_with_me(bool) = Controls file listing behaviour. 
    # 'true' will list files created/owned by the user and files shared with the user, 
    # while 'false' only displays files created/owned by the user.
    with open("settings.json", "r") as settings_json:
        settings = json.load(settings_json)
    
    # Builds the google drive service instance.
    drive = build("drive", "v3", credentials=creds)
    
    while True:
        terminal_size = os.get_terminal_size().columns - 1
        DownloadSystem.total_skipped = 0
        DownloadSystem.skipped_files = []
        print ("\n// D = Download file \n" 
               "// C = Upload file \n"
               "// S = Calculate folder size \n"
               "// E = Exit \n")
                
        option = input("Choose an option: ").upper().strip()
        if option == "E":
            break
        
        if option not in constants.OPTIONS:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Fore.RED + "ERROR" + Style.RESET_ALL + ": Select a valid option from the menu below.")
            continue
        
        print("=" * terminal_size)
        if option == "D":  
            try:
                while True:
                    search_results = []
                    search_completed = False
                    print("\nType the name of the file/folder you want to download (with it's extension) or type:")
                    print("//  list = lists all files/folders present in your Google Drive")
                    print("//     A = Abort operation")
                    search_query = input("=> ").strip().upper()
                    
                    if search_query == "LIST":
                        if settings["shared_with_me"] == False:
                            query="'root' in parents and trashed=false"
                            fields="nextPageToken, files(id, name, size, mimeType, exportLinks)"
                        else:    
                            query="'root' in parents and trashed=false or sharedWithMe and trashed=false"
                            fields="nextPageToken, files(id, name, size, mimeType, exportLinks, shared)"
                        page_token = None
                        while True:
                            search_request = drive.files().list(corpora="user", pageSize=1000, 
                                                                pageToken=page_token,
                                                                fields=fields, 
                                                                q=query, 
                                                                orderBy="folder, name").execute()
                            for item in search_request["files"]:
                                search_results.append(item)                  
                            page_token = search_request.get("nextPageToken", None)
                            if page_token is None:
                                break
                    elif search_query == "A":
                        break   

                    else:
                        if settings["shared_with_me"] == False:
                            query=f"name contains '{search_query}' and trashed=false and 'root' in parents"
                            fields="nextPageToken, files(id, name, size, mimeType, exportLinks)"
                        else:    
                            query=f"name contains '{search_query}' and trashed=false and sharedWithMe"
                            fields="nextPageToken, files(id, name, size, mimeType, exportLinks, shared)"
                            
                        page_token = None
                        while True:
                            search_request = drive.files().list(corpora="user", pageSize= 1000, 
                                                                pageToken=page_token,
                                                                fields=fields, 
                                                                q=query, 
                                                                orderBy="folder,name").execute()
                            for item in search_request["files"]:
                                search_results.append(item) 
                            page_token = search_request.get("nextPageToken", None)
                            if page_token is None:
                                break
                            
                    if len(search_results) == 0:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.RED + "ERROR" + Style.RESET_ALL + ": No file with the specified name was found.")
                        continue
                        
                    systems.list_drive_files(search_results, constants.GOOGLE_WORKSPACE_MIMETYPES)

                    if len(search_results) > 1:
                        while search_completed != True:
                            try:
                                print("\nSpecify the file number to download, or...")
                                print("// A = Abort operation.")
                                file_number = input("=> ").strip().upper()
                                if file_number == "A":
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    break
                                # -1 because the printed list index (list_drive_files) starts at 1,
                                # while search_results list index starts at 0.
                                file_info = search_results[int(file_number) - 1] 
                                search_completed = True
                                break
                            except (IndexError, ValueError):
                                print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + ": Invalid value or out of range.")
                        
                    elif len(search_results) == 1:
                        choice = None
                        while search_completed != True:
                            print("\nOnly one file found. Continue the download process? (Y/N)")
                            choice = input("=> ").upper().strip()
                            if choice not in ["Y", "N"]:
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + f": {choice} is not a valid choice.")
                                systems.list_drive_files(search_results, constants.GOOGLE_WORKSPACE_MIMETYPES)
                                continue
                            elif choice == "Y":
                                file_info = search_results[0]
                                search_completed = True
                                break
                            else:
                                break
                        if choice == "N":
                            os.system('cls' if os.name == 'nt' else 'clear')
                            continue
                    if search_completed == True:
                        break  

                # Handles user abort operation    
                if search_completed != True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                while True:
                    if settings["download_directory"] is not None:
                        download_dir = Path(settings["download_directory"])
                        from_json_download = True
                    else:
                        print("\nSpecify the directory (ABSOLUTE PATH) where the file will be downloaded")
                        print("or press enter to choose the default download directory ([CLID_folder]/downloads)")
                        download_dir = Path(input(r"=> ").strip("\u202a").strip())

                    if download_dir == (WindowsPath(".") if os.name == 'nt' else PosixPath(".")):
                        if not Path("downloads").exists():
                            Path("downloads").mkdir()
                        download_dir = Path("downloads")
                        break
                    else:
                        if not download_dir.exists():
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(Fore.RED + "ERROR" + Style.RESET_ALL + 
                                  f": Unable to find specified path '{download_dir}'.", end=" ")
                            try:
                                if from_json_download == True:
                                    print("Specify an ABSOLUTE path or check your settings.json file if you're using it.")
                                    input("\nPress ENTER to exit.")
                                    exit()
                            except UnboundLocalError:
                                pass
                            print("Specify an ABSOLUTE path or press ENTER.")
                            continue
                        
                        elif not download_dir.is_dir():
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + 
                                  f": Specified path '{download_dir}' is not a directory.", end=" ")
                            try:
                                if from_json_download == True:
                                    print("Specify an ABSOLUTE path to a directory or" 
                                          "check your settings.json file if you're using it.")
                                    input("\nPress ENTER to exit.")
                                    exit()
                            except UnboundLocalError:
                                pass
                            print("Specify an ABSOLUTE path to a directory or press Enter.")
                            continue
                        else:
                            break
                
                if file_info["mimeType"] == "application/vnd.google-apps.folder":
                    if Path.joinpath(download_dir, file_info["name"]).exists():
                        file_info["name"] = systems.prompt_duplicate_file(download_dir, file_info["name"])
                    directory = systems.prepare_directory(download_dir, file_info["name"])
                    print("\nCalculating folder size...", end="")
                    folder_stats = GoogleDriveSizeCalculate(drive).gdrive_checker(file_info["id"])
                    
                    if folder_stats == "Timeout":
                        print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                              ": Operation took longer than expected. Skipping to download...\n")
                        sleep(0.5)
                        progress_bar = systems.load_progress_bar(description="Downloading", folder_mode=True)
                        folder_downloader = DownloadSystem(access_token=access_token, 
                                                           progress_bar=progress_bar, 
                                                           unknown_folder_size=True, 
                                                           folder_mode=True)                   
                    else:
                        print(Fore.GREEN + "Done!" + Style.RESET_ALL)
                        folder_stats["Archive"] = file_info["name"]
                        print("\nTo be downloaded:") 
                        systems.print_file_stats(folder_stats=folder_stats, folder_mode=True)
                        progress_bar = systems.load_progress_bar("Downloading", folder_stats["Bytes"], folder_mode=True)
                        folder_downloader = DownloadSystem(access_token=access_token, 
                                                           progress_bar=progress_bar, 
                                                           folder_mode=True)
                    
                    folder_downloader.get_files(file_info["id"], directory, drive)
                    
                    # Fills progress bar in case of exported files that shrank
                    # in size during download.
                    if progress_bar.n != progress_bar.total:
                        progress_bar.n = progress_bar.total
                        progress_bar.refresh()
                    progress_bar.close()
                        
                # If file is a Google Workspace type but not a folder:
                elif file_info["mimeType"] in constants.DRIVE_EXPORT_FORMATS.keys():           
                    systems.print_file_stats(file_info["name"], file_info["size"])
                    file_downloader = DownloadSystem(access_token=access_token)
                    file_downloader.download_exported_file(file_info, drive, download_dir)
                                     
                # If file did not satisfied the if statements above, then it's a
                # unsuported type (Google Form, Maps or Site)
                elif file_info["mimeType"] in constants.NO_SIZE_TYPES:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + f": File '{file_info['name']}', of type " 
                        f"'{constants.GOOGLE_WORKSPACE_MIMETYPES[file_info['mimeType']].strip('*')}', isn't supported for download.")  
                    print("Aborting Operation...")
                    sleep(1)
                    continue
                
                # Handles ordinary files (files that aren't Google Workspace type).
                else:      
                    for char in file_info["name"]:
                        if char in constants.INVALID_FILENAME_CHARACTERS:
                            file_info["name"] = file_info["name"].replace(char, "_")
                            
                    if Path.joinpath(download_dir, file_info["name"]).exists():
                        file_info["name"] = systems.prompt_duplicate_file(download_dir, file_info["name"])
                    print("\nTo be downloaded:")
                    systems.print_file_stats(file_info["name"], file_info["size"])
                    progress_bar = systems.load_progress_bar("Downloading", file_info["size"])
                    
                    file_downloader = DownloadSystem(progress_bar=progress_bar)
                    file_downloader.download_file(drive, download_dir, file_info)
                    progress_bar.close()
                                   
                print("\nDownload completed successfully!")
                if DownloadSystem.total_skipped > 0:
                    while True:
                        print(f"\n{DownloadSystem.total_skipped} file(s) were skipped during download")
                        print("Do you want to list the skipped files? (Y/N)")
                        choice = input("=> ").upper().strip()

                        if choice == "Y":
                            systems.list_skipped_files(DownloadSystem.skipped_files, constants.GOOGLE_WORKSPACE_MIMETYPES)                            
                            input("\nPress any key to continue")
                            break
                        
                        elif choice == "N":
                            break
                        
                        else:
                            print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + ": Choose a valid option!")
                            continue
                
                # Handles compressed file extraction if the user wants to.
                joined_suffix = "".join(Path(file_info["name"]).suffixes[0:])       
                if joined_suffix in [".zip", ".tar.gz", ".tgz", ".tar"]:
                    while True:
                        print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL +
                            ": Looks like the file you downloaded a compressed file. "
                            "Do you want to extract it to where it was downloaded? (Y/N)")
                        choice = input("=> ").strip().upper()
                        if choice == "N" or choice == "Y":
                            break
                        else:
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + ": Choose a valid option!")
                            continue
                    
                    if choice != "N":
                        compressed_file_path = Path.joinpath(download_dir, file_info["name"])
                        extract_folder_path = Path.joinpath(download_dir, compressed_file_path.name.removesuffix(joined_suffix))
                        systems.extract_file(compressed_file_path, extract_folder_path)
                        print("\nExtraction completed!")
                        systems.remove_localfile(compressed_file_path)
                
            # TODO: how to handle htppError?                   
            except HttpError as error:
                print(f"An error occurred: {error}")
                return
                 
        if option == "C":
            file_created = False
            while True:
                if settings["upload_path"] is not None:
                    file_dir = Path(settings["upload_path"])
                    from_json_upload = True
                else:
                    print("\nSpecify the absolute path of the file to be uploaded, or...")
                    print("// A = Abort.")
                    print(Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                        ": If the file is a directory, it will be zipped before uploading.")
                    # Copying file paths from Windows sometimes adds a invisible
                    # character "u+202a". Strip("\u202a") removes it from the beggining of the
                    # file_dir string path.
                    file_dir = input("=> ").strip("\u202a").strip()
                        
                    if file_dir.upper() == "A":
                        file_dir = "A"
                        break
                    else:
                        file_dir = Path(file_dir).resolve()
                
                if file_dir.exists() and file_dir != (WindowsPath(".") if os.name == "nt" else PosixPath(".")):
                    if file_dir.is_dir():
                        # Function returns the .zip file name, path, metadata and a
                        # bool informing the .zip file creation status.
                        file_dir, local_filename, file_metadata, file_created = systems.compact_directory(file_dir)
                        file = MediaFileUpload(file_dir, mimetype=file_metadata["mimetype"], 
                                                resumable=True, chunksize=constants.CHUNK_SIZE)
                        break                        
                    else:
                        local_filename = file_dir.name 
                        file = MediaFileUpload(file_dir, resumable=True, chunksize=constants.CHUNK_SIZE)
                        file_metadata = {"name" : local_filename}
                        break
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.RED + "ERROR" + Style.RESET_ALL + f": Unable to find specified path '{file_dir}'.", end=" ")
                    try:
                        if from_json_upload == True:
                            print("Specify an ABSOLUTE path or check your settings.json file if you're using it.")
                            input("\nPress ENTER to exit.")
                            exit()
                    except UnboundLocalError:
                        pass
                    print("Specify an ABSOLUTE path.")
                    continue
            
            # Handles abort operation for upload mode.
            if file_dir == "A":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            try:  
                suffix = Path(local_filename).suffixes
                joined_suffixes = "".join(suffix[0:])
                pure_local_filename = local_filename.strip(joined_suffixes)     
                search_results = []
                
                query = f"name contains '{pure_local_filename}' and trashed=false and 'root' in parents"
                page_token = None
                while True:
                    request = drive.files().list(fields="nextPageToken, files(id, name)", 
                                                 pageSize=1000, 
                                                 pageToken=page_token, 
                                                 q=query).execute()
                    for item in request["files"]:
                        search_results.append(item)
                    page_token = request.get("nextPageToken", None)
                    if page_token is None:
                        break
                try:
                    drive_file = next(file for file in search_results if file["name"] == local_filename)
                    drive_filename = drive_file["name"]
                    file_id = drive_file["id"]
                    
                    # If the file already exists in Google Drive.
                    if len(search_results) > 0 and drive_filename == local_filename:
                        upload_choice = None
                        while upload_choice not in ["RP", "RE", "A"]:
                            print("\n" + Fore.YELLOW + "WARNING" + Style.RESET_ALL + 
                                f": File '{local_filename}' already exists in Google Drive.")
                            print("// RP = Replace file.")
                            print("// RN = Keep both files (renames the file with a number next to it).")
                            print("// A = Abort operation")
                            upload_choice = input("=> ").upper().strip()

                            if upload_choice not in ["RP", "RN", "A"]:
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + 
                                    f": {upload_choice} is not a valid choice.\n")
                                continue
                            else:
                                break
                            
                        if upload_choice == "A":
                            file.stream().close()
                            systems.remove_localfile(file_dir)
                            sleep(1)
                            os.system('cls' if os.name == 'nt' else 'clear')
                            continue
                        
                        elif upload_choice == "RP":
                            request = drive.files().update(fileId=file_id, body=file_metadata, media_body=file)  

                        else:
                            print("\nRenaming file...", end="")
                            counter = 0
                            drive_fnames_list = [name["name"] for name in search_results]
                            
                            while local_filename in drive_fnames_list:
                                counter += 1
                                suffix = Path(local_filename).suffixes
                                joined_suffixes = "".join(suffix[0:])
                                pure_name = Path(local_filename).stem.removesuffix(".tar").strip(f"({counter - 1})")
                                local_filename = f"{pure_name}({counter}){joined_suffixes}"  

                            print(Fore.GREEN + "Done!\n" + Style.RESET_ALL)
                            file_metadata["name"] = local_filename
                            request = drive.files().create(body=file_metadata, media_body=file)
                                              
                except StopIteration:
                    # If the file doesn't already exists in Google Drive.
                    request = drive.files().create(body=file_metadata, media_body=file)      
  
                file_size = file_dir.stat().st_size 
                print("\nTo be uploaded:")
                systems.print_file_stats(local_filename, file_size)        
                systems.upload_file(file_size, request)
                print("\nUpload Completed Successfully!")
                
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f"An error occurred: {error}") 
                return
            
            file.stream().close()
            if file_created == True:
                systems.remove_localfile(file_dir)
                file_created = False
            
        if option == "S":
            search_results = []
            if settings["shared_with_me"] == False:
                query = ("'root' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'") 
            else:    
                query = ("'root' in parents and trashed=false and mimeType='application/vnd.google-apps.folder' " 
                        "or sharedWithMe and mimeType='application/vnd.google-apps.folder' and trashed=false")  
            page_token = None
            while True:
                search_request = drive.files().list(corpora="user", 
                                                    pageSize= 1000, 
                                                    pageToken=page_token, 
                                                    fields="files(id, name)", 
                                                    q=query, 
                                                    orderBy="folder, name").execute()
                for item in search_request["files"]:
                    search_results.append(item)  
                page_token = search_request.get("nextPageToken", None)
                if page_token is None:
                    break
                
            while True:
                systems.list_folders(search_results)
                if settings["shared_with_me"] == False:
                    print(Fore.YELLOW + "WARNING" + Style.RESET_ALL +
                        ": Listing only folders present in Google Drive's 'root' directory.")    
                else:
                    print(Fore.YELLOW + "WARNING" + Style.RESET_ALL +
                        ": Listing folders present in Google Drive's 'root' directory and folders shared with the user.")
                    
                print("Select a folder number to calculate it's size, or...")
                print("// A = Abort operation")
                folder_number = input("=> ").strip().upper()
    
                if folder_number == "A":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    break
                try:
                    folder_info = search_results[int(folder_number) - 1]                     
                    break
                except (IndexError, ValueError):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n" + Fore.RED + "ERROR" + Style.RESET_ALL + 
                            ": Type a valid value!")
                    continue
                
            if folder_number == "A":
                continue     
            else:
                print("\nCalculating folder size. This can take a while...\n")
                bar_format = "{desc}: {n_fmt} Files Found [{elapsed}, {rate_fmt}{postfix}]"
                with systems.tqdm(desc="Calculating size", dynamic_ncols=True, 
                                  unit="Files", bar_format=bar_format, initial=1) as progress_bar:
                    folder_stats = GoogleDriveSizeCalculate(drive, progress_bar).gdrive_checker(folder_info["id"])
                print()
                systems.print_file_stats(folder_stats=folder_stats, folder_mode=True)                                    
        print("=" * terminal_size)
    drive.close() 
 
if __name__ == "__main__":
    main()
