"""  TODO:
    * Nome do programa = CLID - The CLI Google Drive ou CLI Drive - Google Drive
      up/downloader.
    * Arquivos baixados/descompactados serão colocados na pasta downloads (ver se da pra achar pasta download do pc independente do sistema),
        caso contrario, fazer uma pasta chamada downloads dentro do root do CLID.
    * Verificar possiblidade de mudar o algoritmo de progresso de compactação.
        Mudar para atualizar a barra conforme os bytes forem lidos,
        e não conforme um arquivo inteiro é comprimido.
    * Usar => apenas para user input e // para multiplas escolhas.
    * Substituir a opção S no menu por uma de calcular o tamanho de pastas.
    * Se o arquivo baixado for um .zip, perguntar se ele quer extrair o arquivo.
      Talvez ter suporte a tar.gz?
 """

from __future__ import print_function

import os
import constants
import systems
from systems import DownloadSystem
from folder_size_calc import GoogleDriveSizeCalculate
from time import sleep
from pathlib import Path, WindowsPath
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload



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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    access_token = creds.token
    
    # Builds the google drive service instance.
    drive = build("drive", "v3", credentials=creds)
    
    while True:
        file_created = False
        print ("\n" "\"d\" = Download file \n" 
                    "\"c\" = Upload file \n"
                    "\"s\" = Calculate folder size \n"
                    "\"e\" = Exit \n")
                
        option = input("Digite uma opção: ").lower().strip()
        if option == "e":
            break
        
        print("=================================================================================================")
        if option not in constants.OPTIONS:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=================================================================================================")
            print("ERROR: Select a valid option from the menu below.")
            print("=================================================================================================")
            continue

        if option == "d":  
            try:
                while True:
                    search_completed = False
                    # English: Type the name of the file you want to download, with it's extension:
                    search_query = input("\nDigite o nome do arquivo que você quer baixar (junto com sua extensão), ou digite:\n"
                                        "//  list = Listar os arquivos presentes em seu Google Drive\n"
                                        "//     A = Abortar ação\n \n"
                                        "AVISO: Apenas arquivos na pasta root (e fora da lixeira) do Google Drive serão exibidos.\n"
                                        "=> ").strip().upper()

                    if search_query == "LIST":
                        search_request = drive.files().list(corpora="user", 
                                                            fields="files(id, name, size, mimeType, exportLinks)", 
                                                            q="'root' in parents and trashed=false", 
                                                            orderBy="folder,name").execute()
                        #search_results = search_request.get("files", [])
                        search_results = search_request["files"]

                    elif search_query == "A":
                        break   

                    else:
                        search_request = drive.files().list(corpora="user", 
                                                            fields="files(id, name, size, mimeType, exportLinks)", 
                                                            q=f"name contains '{search_query}' and trashed=false", 
                                                            orderBy="folder,name").execute()
                        search_results = search_request["files"]

                    if len(search_results) == 0:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("ERRO: Nenhum arquivo com o nome especificado foi encontrado.")
                        continue
                        
                    systems.list_drive_files(search_results, constants.GOOGLE_WORKSPACE_MIMETYPES)

                    if len(search_results) > 1:
                        while search_completed != True:
                            try:
                                file_number = input("\nSelecione o número do arquivo para download, ou..."
                                                        "\n// A = Abortar ação\n \n"
                                                        "=> ").strip().upper()
                                if file_number == "A":
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    break
                                # -1 because printed list index (list_drive_files) starts at 1,
                                # while search_results list index starts at 0.
                                file_info = search_results[int(file_number) - 1] 
                                search_completed = True
                                break
                            except (IndexError, ValueError):
                                print("\nERRO: Digite um valor válido!")
                        
                    elif len(search_results) == 1:
                        choice = None
                        while search_completed != True:
                            choice = input("\nProsseguir para o download do arquivo encontrado? (Y/N)\n"
                                    "=> ").upper().strip()
                            if choice not in ["Y", "N"]:
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print("\nERRO: Digite apenas Y ou N")
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
                    print("\nDigite o diretório onde o arquivo será baixado\n"
                        "ou aperte enter para escolher o diretório padrão ([CLID_folder]/downloads)\n")
                    download_dir = Path(input(r"=> ").strip("\u202a").strip())

                    if download_dir == WindowsPath("."):
                        if not Path("downloads").exists():
                            Path("downloads").mkdir()
                        download_dir = Path("downloads")
                        break

                    else:
                        if not download_dir.exists():
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(f"ERRO: Não foi possivel encontrar o caminho '{download_dir}'. "
                                "Especifique um caminho ABSOLUTO ou aperte ENTER.\n")
                            continue
                        else:
                            break
                
                if file_info["mimeType"] == "application/vnd.google-apps.folder":
                    file_info["name"] = systems.check_download_dir(file_info["name"], download_dir)
                    directory = systems.prepare_directory(download_dir, file_info["name"])
                    print("\nCalculando tamanho da pasta...\n")
                    folder_stats = GoogleDriveSizeCalculate(drive).gdrive_checker(file_info["id"])
                    
                    if folder_stats == "Timeout":
                        # TODO: Mudar progress bar aqui pq o tamanho da pasta é desconhecido 
                        print("\nWARNING: Operação durou mais que o esperado. Continuando para download...")
                        sleep(0.5)
                        progress_bar = systems.load_progress_bar(description="Fazendo download")
                        folder_downloader = DownloadSystem(access_token=access_token, 
                                                           progress_bar=progress_bar, 
                                                           unknown_folder_size=True, 
                                                           folder_mode=True)                   
                    else:
                        folder_stats["Archive"] = file_info["name"]
                        print("\nTo be downloaded:") 
                        systems.print_file_stats(folder_stats=folder_stats, folder_mode=True)
                        progress_bar = systems.load_progress_bar("Fazendo Download", folder_stats["Bytes"])
                        folder_downloader = DownloadSystem(access_token=access_token, 
                                                           progress_bar=progress_bar, 
                                                           folder_mode=True)
                    
                    folder_downloader.get_files(file_info["id"], directory, drive)
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
                    print(f"\nERRO: O arquivo '{file_info['name']}', do tipo " 
                        f"{constants.GOOGLE_WORKSPACE_MIMETYPES[file_info['mimeType']].strip('*')}, não possui suporte para download. "  
                        "Cancelando Operação...")
                    sleep(1)
                    continue
                
                # Handles ordinary files (files that aren't Google Workspace type).
                else: 
                    file_info["name"] = systems.check_download_dir(file_info["name"], download_dir)
                    print("\nTo be downloaded:")
                    systems.print_file_stats(file_info["name"], file_info["size"])
                    progress_bar = systems.load_progress_bar("Downloading", file_info["size"])
                    file_downloader = DownloadSystem(progress_bar=progress_bar)
                    file_downloader.download_file(drive, download_dir, file_info)
                    progress_bar.close()
                                   
                print("\nDownload concluído com sucesso!")
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
                            print("\nERROR: Choose a valid option!")
                            continue
               
            # TODO: how to handle htppError?                   
            except HttpError as error:
                print(f"An error occurred: {error}")
                return
                 
        if option == "c":
            # Copying file paths from Windows sometimes adds a invisible
            # character "u+202a". Strip("\u202a") removes it from the beggining of the
            # file_dir string path.
            #
            # English: Type the absolute path of the file you want to upload.
            # NOTE: If the file is a directory (folder), it will be zipped before uploading.
            file_dir = Path(input("Digite o caminho absoluto do arquivo a ser upado:"
                        "\nAVISO: Se o arquivo for um diretório (pasta), ele será upado em formato .zip\n"
                        "=> ").strip("\u202a").strip()) 

            if file_dir.exists():
                if file_dir.is_dir():
                    # Function returns the .zip file name, path, metadata and a
                    # bool informing the .zip file creation status.
                    target_path, local_filename, file_metadata, file_created = systems.compact_directory(file_dir)
                    file_dir = target_path
                    file = MediaFileUpload(file_dir, mimetype="application/zip", resumable=True, chunksize=constants.CHUNK_SIZE)
                     
                else:
                    local_filename = file_dir.name 
                    file = MediaFileUpload(file_dir, resumable=True) 
                    file_metadata = {"name" : local_filename}
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("=================================================================================================")
                # English: ERROR: File path doesn't exist.
                print("ERRO: O caminho do arquivo não existe.")
                print("=================================================================================================")
                continue
            
            file_size = file_dir.stat().st_size 
            print("\nTo be uploaded:")
            systems.print_file_stats(local_filename, file_size)

            try:
                results = drive.files().list(fields="files(id, name)",
                    pageSize=1000, 
                    q=f"name = '{local_filename}' and trashed=false").execute()

                try:
                    items = results.get("files", [])
                    drive_file = next(file for file in items if file["name"] == local_filename)
                    drive_filename = drive_file["name"]
                    file_id = drive_file["id"]
                except StopIteration:
                    # If the file doesn't already exists in google drive...
                    request = drive.files().create(body=file_metadata, media_body=file)

                # If there are two or more files with the exact same
                # name in Drive, it will upload a copy of the file and
                # skip user prompt.
                if len(items) > 1 and drive_filename == local_filename:
                    request = systems.create_gdrive_copy(file_metadata, drive, drive_filename, file)
                    print(f"AVISO: Múltiplos arquivos com o mesmo nome. O Arquivo será upado como \"{file_metadata['name']}\".\n")
                    sleep(1)

                # In case there's only one file with the exact same name
                # as the local file, in google drive.
                elif len(items) > 0 and drive_filename == local_filename:
                    upload_choice = None
                    while upload_choice not in ["Y", "C", "A"]:
                        upload_choice = input("AVISO: O arquivo já existe no Google Drive! Pressione:\n"
                                            "// Y = Atualizar o arquivo\n" 
                                            "// C = Manter os dois arquivos (Arquivo terá \"cópia de ...\" junto ao nome)\n"
                                            "// A = Abortar ação\n"
                                            "=> ").upper().strip()

                        if upload_choice not in ["Y", "C", "A"]:
                            print("\nERRO: Selecione uma opção válida.\n") 
                        elif upload_choice == "Y":
                            request = drive.files().update(fileId=file_id, body=file_metadata, media_body=file)  
                            break
                        elif upload_choice == "C":
                            request = systems.create_gdrive_copy(file_metadata, drive, drive_filename, file)
                            break
                    if upload_choice == "A":
                        os.system('cls' if os.name == 'nt' else 'clear')
                        continue
            
                systems.upload_file(file_size, request)
                
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f"An error occurred: {error}") 
                return
            
            file.stream().close()
            if file_created == True:
                systems.remove_localfile(file_dir)
                file_created = False

            print("Operação concluída!")
        print("=================================================================================================")

    drive.close() 
         
if __name__ == "__main__":
    main()

