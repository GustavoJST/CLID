"""  TODO: 
    * função de busca simples por nome do arquivo, apenas na pasta root do google drive (página inicial)
    * Nome do programa = CLID - The CLI Google Drive ou CLI Drive - Google Drive up/downloader.
    * Items na lixeira não serão pesquisados
    * Caso a pesquisa resulte em multiplos arquivos com o mesmo nome, avisar o usuário que multiplos arquivos foram encontrados (WARNING:),
        e listar os arquivos com mesmo nome encontrados, seguido de um prompt para escolher qual arquivo baixar, OU listar/não listar os arquivos
        com nomes iguais, seguido de um prompt se o usuário deseja continuar ou abortar (Y/N).
    * Caso o arquivo seja uma pasta, ele sera baixado como arquivo zip
    * Caso arquivo baixado seja um .zip ou (outro compactado, ver possibilidade) Oferecer opção para descompactar
    * Arquivos baixados/descompactados serão colocados na pasta downloads (ver se da pra achar pasta download do pc independente do sistema),
        caso contrario, fazer uma pasta chamada downloads dentro do root do CLID.
    
 """

from __future__ import print_function

from pathlib import Path
import io
from time import sleep
from zipfile import ZipFile
import zipfile
import math
from tqdm import tqdm
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Builds the google drive service instance 
    drive = build("drive", "v3", credentials=creds)

    # Since all downloads/uploads in this program are set to resumable=True, these actions
    # are performed in chunks. Set the desired chunk size (in bytes), in the
    # variable below.  
    # NOTE: There are some restrictions with chunk sizes. For files larger than 256KB,
    # use CHUNK_SIZE values that are multiples of 256KB (1024 * 256 * some_value).
    # For files smaller than 256KB, there are no restrictions.
    #  
    # For the best efficiency, try to keep the chunk size as close to the default
    # value as possible.
    CHUNK_SIZE = 104857600  # Equals to 100MB. Default Google Drive chunk size value. 
    OPTIONS = ["d", "c", "s", "e"]
    file_created = False

    while True:
        print ("\n" "\"d\" = download, extrair e substituir a pasta atual \n" 
                    "\"c\" = compactar e fazer upload p/ o drive \n"
                    "\"s\" = verificar se o arquivo já existe e sua versão \n"
                    "\"e\" = sair do programa \n")
                
        option = input("Digite uma opção: ").lower().strip()
        if option == "e":
            break 
        
        print("=================================================================================================")
        if option not in OPTIONS:
            print("=> Select a valid option from the menu below.")
            print("=================================================================================================")
            continue

        if option == "d":
            # TODO: fazer dict
            drive_workspace_mimetypes = {"application/vnd.google-apps.script",
                                        "application/vnd.google-apps.presentation",
                                        "application/vnd.google-apps.jam",
                                        "application/vnd.google-apps.document",
                                        "application/vnd.google-apps.drawing",
                                        "application/vnd.google-apps.folder",
                                        "application/vnd.google-apps.spreadsheet"}
            try:
                #while True:
                # English: Type the name of the file you want to download, with it's extension:
                search_query = input("\nDigite o nome do arquivo que você quer baixar (junto com sua extensão), ou digite:\n"
                                    "//  list = Listar os arquivos presentes em seu Google Drive\n"
                                    "//     A = Abortar ação\n \n"
                                    "AVISO: Apenas arquivos na pasta root (e fora da lixeira) do Google Drive serão exibidos.\n"
                                    "=> ").strip().lower()
               

                if search_query == "list":
                    search_request = drive.files().list(corpora="user", 
                                                        fields="files(id, name, size, mimeType)", 
                                                        q="'root' in parents and trashed=false").execute()
                    search_results = search_request.get("files", [])
                    list_files(search_results)


                    
                else:
                    search_request = drive.files().list(corpora="user", 
                                                fields="files(id, name, size, mimetype)", 
                                                q=f"name contains '{search_results}' and trashed=false").execute()
                    search_results = search_request.get("files", [])
                    
                    if search_results > 1:
                        list_files(search_results)


                        try:
                            items = results.get("files", [])
                            file_id = items[0]["id"]
                            file_size = int(items[0]["size"])

                        except IndexError:
                            print("Error: File not found in Drive.")
                            print("=================================================================================================")
                            continue
                    

                request = drive.files().get_media(fileId=file_id)
                with io.FileIO("C:/Users/Gustavo/VSCode_projects.zip", "w") as file:
                    downloader = MediaIoBaseDownload(file, request, chunksize=CHUNK_SIZE)
                    done = False
                    # Loads the progress bar
                    with tqdm(total=file_size, 
                        unit="B", 
                        desc="Downloading ",
                        ncols=90, 
                        unit_scale=True,
                        unit_divisor=1024,
                        miniters=1,
                        bar_format="{desc}: {percentage:3.1f}%|{bar}| " 
                            "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as bar: 
                        while done == False:
                            status, done = downloader.next_chunk()
                            print(status)
                            print(done)
                            if status:
                                bar.n = status.resumable_progress
                                bar.refresh()

                print("\n=> Download concluído com sucesso!")

                print("\n=> Iniciando extração do arquivo...")
                sleep(0.5)
                # Iterates through all files inside the zip file, extracting them.
                with ZipFile("C:/Users/Gustavo/VSCode_projects.zip") as zfile:
                    for files in tqdm(zfile.infolist(), desc="Extraindo ", ncols=90):
                        zfile.extract(files,"C:/Users/Gustavo/VSCode_projects")
                print("\n=> Extração e substituição da pasta concluídos com sucesso!")

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
            file_dir = Path(input("Digite o caminho absoluto do arquivo a ser upado."
                        "\nAVISO: Se o arquivo for um diretório (pasta), ele será upado em formato .zip\n"
                        "=> ").strip("\u202a").strip()) 

            if Path(file_dir).exists():
                if Path(file_dir).is_dir():
                    # Function returns the .zip file name, path, metadata and a
                    # bool informing the .zip file creation status.
                    target_path, local_filename, file_metadata, file_created = compact_directory(file_dir)
                    file_dir = target_path
                    file = MediaFileUpload(file_dir, mimetype="application/zip", resumable=True)
                     
                else:
                    local_filename = Path(file_dir).name
                    file = MediaFileUpload(file_dir, resumable=True) 
                    file_metadata = {"name" : local_filename}
            else:
                # English: ERROR: File path doesn't exist.
                print("\nERRO: O caminho do arquivo não existe.")
                print("=================================================================================================")
                continue
            
            file_size = Path(file_dir).stat().st_size 
            print_file_stats(local_filename, file_size)

            try:
                results = drive.files().list(fields="nextPageToken, files(id, name)",
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
                    request = create_gdrive_copy(file_metadata, drive, drive_filename, file)
                    print(f"AVISO: Múltiplos arquivos com o mesmo nome. O Arquivo será upado como \"{file_metadata['name']}\".\n")
                    sleep(1)

                # In case there's only one file with the exact same name
                # as the local file, in google drive.
                elif len(items) > 0 and drive_filename == local_filename:
                    upload_choice = None;
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
                            request = create_gdrive_copy(file_metadata, drive, drive_filename, file)
                            break
                    if upload_choice == "A":
                        continue
            
                upload_file(file_size, request)
                
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f"An error occurred: {error}") 
                return
            
            file.stream().close()
            if file_created == True:
                remove_localfile(file_dir)
                file_created = False
        
        print("=================================================================================================")

    drive.close()   

def compact_directory(file_dir): 
    # English: "File identified as a directory. Starting compaction..."
    print("\n=> Arquivo identificado como diretório. Iniciando compactação...")
    sleep(1) 
    target_path = Path(f"{file_dir}.zip")
    local_filename = Path(target_path).name
   
    file_quantity = 0
    for file in file_dir.rglob("*"):
        file_quantity += 1         
        
    with ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zfile:
        for files in tqdm(file_dir.rglob("*"), total=file_quantity, desc="Compactando ", ncols=90):
            zfile.write(files, files.relative_to(file_dir)) 

    file_metadata = {
        "name" : local_filename,
        "mimetype" : "application/zip"
                }
    file_created = True
    return target_path, local_filename, file_metadata, file_created


def convert_filesize(size_bytes):
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
    file_metadata["name"] = f"Cópia de {drive_filename}"
    request = drive.files().create(body=file_metadata, media_body=file)
    return request


def upload_file(file_size, request):
    print("\n=> Iniciando upload... (Aperte Ctrl+C para abortar)")
    sleep(1)
    with tqdm(total=file_size, 
        unit="B", 
        desc="Fazendo upload ", 
        ncols=90, 
        unit_scale=True, 
        unit_divisor=1024, 
        miniters=1,
        bar_format="{desc}: {percentage:3.1f}%|{bar}| "
                "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as bar:     
        response = None
        while response is None:
            status, response = request.next_chunk()
            # If the file is smaller than the chunksize (100MB), it will be
            # completely uploaded in a single chunk, skipping the if below.
            # Trying to access status.resumable_progress after the
            # file has been completely uploaded will raise AttributeError.  
            if status:
                bar.n = status.resumable_progress # Keeps track of the total size transfered.
                bar.refresh()

        # Updates bar when the file is uploaded in a single chunk.
        if status is None:
            bar.n = file_size
            bar.refresh() 
    # English: Upload completed successfully!
    print("\n=> Upload concluído com sucesso!")

def remove_localfile(file_dir):
    if Path(file_dir).exists:
        # English: Removing the created .zip file form the system...
        print("\n=> Removendo arquivo ZIP do sistema...")
        sleep(1)
        Path(file_dir).unlink()
        # English: Local .zip file removed successfully!
        print("\n=> Remoção do arquivo local concluido!")
    else:
        # English: ERROR: File {file_dir} doesn't exist in the system. Aborting operation...
        print(f"\nERRO: Arquivo {file_dir} não existe no sitema. Cancelando operação...")


def list_files(search_results):
    counter = 1
    print("\n=> Os seguintes arquivos foram encontrados: ")
    print("---------------------------------------------------------------------------------------------------------------------------")
    for drive_file in search_results:
        try:
            print(f"#{counter:>4} | {convert_filesize(int(drive_file['size'])):^16} --->   {drive_file['name']}")
        # If 'size' key is not found, it's a Google Drive folder,
        # since GD folder doesn't have any size.   
        except KeyError:
            print(f"#{counter:>4} | {'(Drive folder)':^16} --->   {drive_file['name']}")
        counter += 1
    print("---------------------------------------------------------------------------------------------------------------------------")


def print_file_stats(file_name, file_size):
    print("\n-----------------------------------------------------------------------------------------------")
    print(f"// Arquivo: {file_name}")
    print(f"// Tamanho: {convert_filesize(file_size)}")
    print("-----------------------------------------------------------------------------------------------\n")
    sleep(1)


if __name__ == "__main__":
    main()

