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
    * Para fazer upload de arquivos, usar prompt p/ usuário pedindo qual o path do arquivo que ele quer upar.
    * Se o arquivo for um diretório (pasta), perguntar se ele quer upar de forma zipada ou como pasta (ver possibilidade de como upar como pasta).
    * Se o arquivo for um arquivo normal (não é pasta), upar normalmente.
 """

from __future__ import print_function

from pathlib import Path
import io
from time import sleep
from zipfile import ZipFile
import zipfile
from tqdm import tqdm
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaUpload
from googleapiclient.http import MediaUploadProgress

from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    creds = None
    # The file token.json stores the user"s access and refresh tokens, and is
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

    # Since all downloads/uploads in this program are resumable, these action
    # are performed in chunks. Set the desired chunk size (in bytes), in the
    # variable below.  
    # Note: There are some restrictions with chunk sizes. For files larger than 256KB,
    # use chunk_size values that are multiples of 256KB (1024 * 256 * some_value).
    # For files smaller than 256KB, there are no restrictions.
    #  
    # For the best efficiency, try to keep the chunksize as close to the default
    # value as possible.
    chunk_size = 104857600  # Equals to 100MB. Default Google Drive chunksize value. 
    options = ["d", "c", "s", "e"]

    while True:
        print ("\n" "\"d\" = download, extrair e substituir a pasta atual \n" 
                    "\"c\" = compactar e fazer upload p/ o drive \n"
                    "\"s\" = verificar se o arquivo já existe e sua versão \n"
                    "\"e\" = sair do programa \n")
                
        option = input("Digite uma opção:  ").lower()
        if option == "e":
            break 
        
        print("=================================================================================================")
        if option not in options:
            print("=> Select a valid option from the menu below.")
            print("=================================================================================================")
            continue

        
        if option == "d":
            
            try:
                results = drive.files().list(fields="files(id, name, size)", q="name contains 'VSCode_projects.zip' and trashed=false").execute()
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
                    downloader = MediaIoBaseDownload(file, request, chunksize=chunk_size)
                    done = False
                    # Loads the progress bar
                    with tqdm(
                        total=file_size, 
                        unit="B", 
                        desc="Downloading ",
                        ncols=90, 
                        unit_scale=True,
                        unit_divisor=1024,
                        miniters=1,
                        bar_format="{desc}: {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as bar: 
                        while done is False:
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
                               
            except HttpError as error:
                print(f"An error occurred: {error}")
                 
        if option == "c":

            file_dir = input("Type the path of the file you want to upload."
                        "\nNOTE: If the file is a directory (folder), it will be zipped to a .zip file.\n"
                        "=> ")

            try:
                directory = Path(r"C:/Users/Gustavo/VSCode_projects")
                target_path = Path(r"C:/Users/Gustavo/VSCode_projects.zip")
                local_filename = Path(target_path).name

                file_quantity = 0
                for i in directory.rglob("*"):
                    file_quantity += 1         
                
                with ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zfile:
                    for files in tqdm(directory.rglob("*"), total=file_quantity, desc="Compactando ", ncols=90):
                        zfile.write(files, files.relative_to(directory)) 

                file_metadata = {
                    "name" : local_filename,
                    "mimetype" : "application/zip"
                }
                file = MediaFileUpload(target_path, mimetype="application/zip",resumable=True)

                results = drive.files().list(fields="files(id, name)", 
                    q=f"name contains '{local_filename}' and trashed=false").execute()
        
                try:
                    items = results.get("files", [])
                    file_id = items[0]["id"]
                    drive_filename = items[0]["name"] 

                    if len(items) > 0 and drive_filename == local_filename:
                        print("\n=> O arquivo já existe no Drive. Atualizando arquivo...")
                        sleep(1.5)
                        request = drive.files().update(fileId=file_id, body=file_metadata, media_body=file)  
                
                except IndexError:
                    print("\n=> O arquivo não existe no Drive. Criando novo arquivo...")
                    sleep(1.5)
                    request = drive.files().create(body=file_metadata, media_body=file)


                file_size = Path(target_path).stat().st_size  
                                                
                # Loads the upload progress bar.
                with tqdm(total=file_size, unit="B", desc="Fazendo Upload ", ncols=90, unit_scale=True, unit_divisor=1024, miniters=1,
                    bar_format="{desc}: {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as bar:     
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
                print("\n=> Upload concluído com sucesso!")
                

            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f"An error occurred: {error}") 
            
            file.stream().close()
            if Path(target_path).exists:
                print("\n=> Removendo arquivo ZIP do sistema...")
                sleep(1)
                Path(target_path).unlink()
                print("\n=> Remoção do arquivo local concluido!")
            else:
                print(f"\n=> ERRO: Arquivo {target_path} não existe no sitema. Cancelando operação...")
        
        print("=================================================================================================")

    drive.close()   

if __name__ == "__main__":
    main()

