"""  TODO: 
    * Nome do programa = CLID - The CLI Google Drive ou CLI Drive - Google Drive up/downloader.
    * Caso a pesquisa resulte em multiplos arquivos com o mesmo nome, avisar o usuário que multiplos arquivos foram encontrados (WARNING:),
        e listar os arquivos com mesmo nome encontrados, seguido de um prompt para escolher qual arquivo baixar, OU listar/não listar os arquivos
        com nomes iguais, seguido de um prompt se o usuário deseja continuar ou abortar (Y/N).
    * Caso o arquivo seja uma pasta, ele sera baixado como arquivo zip
    * Caso arquivo baixado seja um .zip ou (outro compactado, ver possibilidade) Oferecer opção para descompactar
    * Arquivos baixados/descompactados serão colocados na pasta downloads (ver se da pra achar pasta download do pc independente do sistema),
        caso contrario, fazer uma pasta chamada downloads dentro do root do CLID.
    * Verificar possiblidade de mudar o algoritmo de progresso de compactação.
        Mudar para atualizar a barra conforme os bytes forem lidos,
        e não conforme um arquivo inteiro é comprimido.
    * usar os.system('cls' if os.name == 'nt' else 'clear') para limpar os
      terminais e deixar o terminal menos poluido
    * Usar => apenas para user input e // para multiplas escolhas.
 """

from __future__ import print_function

from pathlib import Path, WindowsPath
import io
import os
import math
import requests
import zipfile
from zipfile import ZipFile
from time import sleep
from tqdm import tqdm
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import constants

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
    
    while True:
        file_created = False
        print ("\n" "\"d\" = download, extrair e substituir a pasta atual \n" 
                    "\"c\" = compactar e fazer upload p/ o drive \n"
                    "\"s\" = verificar se o arquivo já existe e sua versão \n"
                    "\"e\" = sair do programa \n")
                
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
                                                            q="'root' in parents and trashed=false").execute()
                        #search_results = search_request.get("files", [])
                        search_results = search_request["files"]

                    elif search_query == "A":
                        break   

                    else:
                        search_request = drive.files().list(corpora="user", 
                                                            fields="files(id, name, size, mimeType, exportLinks)", 
                                                            q=f"name contains '{search_query}' and trashed=false").execute()
                        #search_results = search_request.get("files", [])
                        search_results = search_request["files"]

                    if len(search_results) == 0:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("ERRO: Nenhum arquivo com o nome especificado foi encontrado.")
                        continue
                        
                    list_drive_files(search_results, constants.GOOGLE_WORKSPACE_MIMETYPES)

                    if len(search_results) > 1:
                        while search_completed != True:
                            try:
                                # TODO: add abort system
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
                                print("ERRO: Digite apenas Y ou N")
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

                #TODO: fazer aqui a verificação do mimetype do arquivo. Se for
                #do google workspace, oferecer opção de conversão baseado no
                #tipo de arquivo.
                while True:
                    print("Digite o diretório onde o arquivo será baixado\n"
                        "ou digite enter para escolher o diretório padrão ('CLID_folder'/downloads)\n")
                    # TODO: Checar o que acontece quando o usuário colocar
                    # caracteres proibidos pelo windows como nome da pasta.
                    download_dir = Path(input(r"=> ").strip("\u202a").strip())

                    if download_dir == WindowsPath("."):
                        if not Path("downloads").exists():
                            Path("downloads").mkdir()
                        download_dir = Path("downloads")
                        break
                    else:
                        try:
                            if not Path(download_dir).exists():
                                raise FileNotFoundError
                            else:
                                break
                        except FileNotFoundError:
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(f"ERRO: Não foi possivel encontrar o caminho '{download_dir}'. "
                                "Especifique um caminho ABSOLUTO ou aperte ENTER.\n")


                # TODO: fazer aqui a verificação do mimetype do arquivo. Se for
                #do google workspace, oferecer opção de conversão baseado no
                #tipo de arquivo.

                if file_info["mimeType"] == "application/vnd.google-apps.folder":

                    file_info["name"] = check_download_dir(file_info["name"], download_dir)
                    directory = prepare_directory(download_dir, file_info["name"])
                    get_files(file_info["id"], directory, drive)
                
                
                # If file is a Google Workspace type but not a folder:
                elif file_info["mimeType"] in constants.DRIVE_EXPORT_FORMATS.keys():
                    # Colocar em uma função chamada download_exported_file()
                    download_exported_file(file_info, drive, download_dir, creds)
                    
         
                # If file did not satisfied the if statements above, then it's a
                # unsuported type (Google Form, Maps or Site)
                elif file_info["mimeType"] in constants.NO_SIZE_TYPES:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"ERRO: O arquivo '{file_info['name']}', do tipo " 
                        f"{constants.GOOGLE_WORKSPACE_MIMETYPES[file_info['mimeType']].strip('*')}, não possui suporte para download. "  
                        "Cancelando Operação...")
                    sleep(1)
                    continue
                
                # Handles ordinary files (files that aren't Google Workspace type).
                else: 
                    file_info["name"] = check_download_dir(file_info["name"], download_dir)
                    progress_bar = load_progress_bar(int(file_info["size"]), "Fazendo Download")
                    download_file(file_info["id"], drive, download_dir, file_info["name"] , file_info["mimeType"], progress_bar)
                    progress_bar.close()

                    """ while True:
                        check_download_dir(file_info["name"])
                        if Path.joinpath(download_dir, file_info["name"]).exists():
                            print(f"\nAVISO: O arquivo {file_info['name']} já está presente no diretório de download.")
                            print("// S = Substituir o arquivo.")
                            print("// C = Baixar como cópia.\n")
                            choice = input("=> ").strip().upper()

                            if choice != "S" and choice != "C":
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print("ERRO: Escolha uma opção válida!\n")

                            elif choice == "S":
                                    progress_bar = load_progress_bar(int(file_info["size"]), "Fazendo Download")
                                    download_file(file_info["id"], drive, download_dir, file_info["name"] , file_info["mimeType"], progress_bar)
                                    progress_bar.close()
                                    break

                            else:
                                progress_bar = load_progress_bar(int(file_info["size"]), "Fazendo Download")
                                file_copy_name = f"Copy of {file_info['name']}"
                                download_file(file_info["id"], drive, download_dir, file_copy_name , file_info["mimeType"])
                                progress_bar.close()
                                break
                        else:
                            # TODO: ter parâmetro folder_mode com valor bool,
                            # que muda o comportamento da função download_file.                
                            progress_bar = load_progress_bar(int(file_info["size"]), "Fazendo Download")
                            download_file(file_info["id"], drive, download_dir, file_info["name"], 
                                                file_info["mimeType"], progress_bar) 
                            progress_bar.close() """   


                
                # print_file_stats(file_info["name"], file_info["size"])
                
              
                # request = drive.files().get_media(fileId=file_id)

                print("\n=> Download concluído com sucesso!")

                
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

            if Path(file_dir).exists():
                if Path(file_dir).is_dir():
                    # Function returns the .zip file name, path, metadata and a
                    # bool informing the .zip file creation status.
                    target_path, local_filename, file_metadata, file_created = compact_directory(file_dir)
                    file_dir = target_path
                    file = MediaFileUpload(file_dir, mimetype="application/zip", resumable=True, chunksize=constants.CHUNK_SIZE)
                     
                else:
                    local_filename = Path(file_dir).name
                    file = MediaFileUpload(file_dir, resumable=True) 
                    file_metadata = {"name" : local_filename}
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("=================================================================================================")
                # English: ERROR: File path doesn't exist.
                print("\nERRO: O caminho do arquivo não existe.")
                print("=================================================================================================")
                continue
            
            file_size = Path(file_dir).stat().st_size 
            print_file_stats(local_filename, file_size)

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
                        os.system('cls' if os.name == 'nt' else 'clear')
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

            print("Operação concluída!")
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
    size_bytes = int(size_bytes)
    if size_bytes == 0:
        return "0B"
    size_unit = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
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
    progress_bar = load_progress_bar(file_size, "Fazendo upload") 
    response = None
    while response is None:
        status, response = request.next_chunk()
        # If the file is smaller than the chunksize (100MB), it will be
        # completely uploaded in a single chunk, skipping the if below.
        # Trying to access status.resumable_progress after the
        # file has been completely uploaded will raise AttributeError.  
        if status:
            progress_bar.n = status.resumable_progress # Keeps track of the total size transfered.
            progress_bar.refresh()

        # Updates bar when the file is uploaded in a single chunk.
        if status is None:
            progress_bar.n = file_size
            progress_bar.refresh() 
    progress_bar.close()
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
        print(f"\nERRO: Arquivo {file_dir} não existe no sitema. Pulando operação...\n")


def list_drive_files(search_results, GOOGLE_WORKSPACE_MIMETYPES):
    counter = 1
    print("\n=> Os seguintes arquivos foram encontrados: ")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(f"{'Num':^4}  | {'Tipo':^14} | {'Tamanho':^11}    |   Nome do Arquivo")
    print("---------------------------------------------------------------------------------------------------------------------------")
    for drive_file in search_results:

        if drive_file["mimeType"] in constants.NO_SIZE_TYPES:
            print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {'----':^11} --->   {drive_file['name']}")
        
        elif drive_file["mimeType"] in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
             print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}") 

        else:
            print(f"#{counter:>4} | {'File':^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}")
        counter += 1
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("AVISO: Arquivos com o tipo marcado com '*' não possuem suporte para download.")

def print_file_stats(file_name, file_size):
    print("\n-----------------------------------------------------------------------------------------------")
    print(f"// Arquivo: {file_name}")
    print(f"// Tamanho: {convert_filesize(file_size)}")
    print("-----------------------------------------------------------------------------------------------\n")
    sleep(1)

def prepare_directory(download_dir, gdrive_folder_name):
    #folder_path = Path(f"{download_dir}/{gdrive_folder_name}")
    folder_path = Path.joinpath(download_dir, gdrive_folder_name)
    if not Path(folder_path).exists():
        try:
            Path(folder_path).mkdir()
            return folder_path
        except OSError:
            print("Caractere inválido detectado no nome da pasta. Mude o nome da pasta retirando o caractere inválido [\\ / ? : * < > | \"]")
            print("Encerrando programa...")
            exit()
    else:
        print(f"A pasta no caminho {folder_path} já existe. Continuar mesmo assim? (Y/N)\n")
        choice = input("=> ").strip().upper()
    
    while True:
        if choice == "Y":
            return folder_path
        elif choice == "N":
            # TODO: este return vazio irá causar erro. arrumar isso
            return
        else:
            print("ERRO: Escolha uma opção válida!")

def get_files(folder_id, directory, drive):
    search_request = drive.files().list(corpora="user", 
                                        fields="files(id, name, size, mimeType)", 
                                        q=f"'{folder_id}' in parents and trashed=false").execute()
    search_results = search_request.get("files", [])

    for file in search_results:
        if file["mimeType"] == "application/vnd.google-apps.folder":
            get_files(file["id"], prepare_directory(directory, file["name"]), drive)
        else:
            download_file(file["id"], drive, directory, file["name"], file["mimeType"])       

# TODO: no futuro, o parâmetro progress_bar talvez não será necessário, pois
# todo download usará uma barra de progresso, mudando apenas a forma que é usada.
def download_file(file_id, drive, directory, file_name, file_mimetype, progress_bar=None, folder_mode=True):
    valid = 0
    skipped = 0
    file_path = Path.joinpath(directory, file_name)
    if file_mimetype in constants.DRIVE_EXPORT_FORMATS.keys() and file_mimetype not in constants.NO_SIZE_TYPES:
        export_mimetype = constants.DRIVE_EXPORT_FORMATS[file_mimetype][0]["mimetype"]
        request = drive.files().export_media(fileId=file_id, mimeType=export_mimetype)
        file = io.FileIO(f"{file_path}{constants.DRIVE_EXPORT_FORMATS[file_mimetype][0]['extension']}", "w")
        #valid += 1
    
    elif file_mimetype in constants.NO_SIZE_TYPES:
        print(f"Arquivo {file_name} não é suportado. Pulando download do arquivo...")
        #skipped +=1
        return

    # Else handles ordinary files that already have an extension in their name.
    else:
        request = drive.files().get_media(fileId=file_id)
        file = io.FileIO(f"{file_path}", "w")

    """ Ao fazer um download, assim que um chunk é baixado, ele é escrito no computador. Ao ler a quantidade
    de bytes escritos em um arquivo, é possivel somar isso ao total de bytes baixados e fazer a diferença 
    com o tamanho total em bytes da pasta. Assim sendo possivel fazer uma progress bar do download da pasta """
    
    downloader = MediaIoBaseDownload(file, request, chunksize=constants.CHUNK_SIZE)
    done = False
    while done == False:
        status, done = downloader.next_chunk()
        if progress_bar != None:
            progress_bar.n = status.resumable_progress
            progress_bar.refresh()
        print(F'Download {int(status.progress() * 100)}.')

    file.close()


    """ with io.FileIO(file_path, "w") as file:
        downloader = MediaIoBaseDownload(file, request, chunksize=constants.CHUNK_SIZE)
        done = False
        # Loads the progress bar
        # total=file_size
        with tqdm( 
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
                    bar.refresh() """

def load_progress_bar(total_file_size, description):
    bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}iB/{total_fmt}iB [{elapsed}<{remaining}, {rate_fmt}]"
    return tqdm(total=int(total_file_size), desc=description, miniters=1, bar_format=bar_format, 
                unit="iB", unit_scale=True, unit_divisor=1024, dynamic_ncols=True)

def download_exported_file(file_info, drive, download_dir, creds):
    pbar_loaded = False
    export_formats = constants.DRIVE_EXPORT_FORMATS[file_info["mimeType"]]
    # English: WARNING: Google Workspace File detected!
    while True:
        print("\nAVISO: Arquivo do Google Workspace detectado!")
        # English: WARNING :{file_info['name']} can't be downloaded directly and needs to be exported to another format beforehand.
        print(f"AVISO: O arquivo {file_info['name']} não pode ser baixado diretamente e precisa ser convetido antes.\n")
        print("Digite um dos formatos abaixo para converter o arquivo a ser baixado:")
        print("-----------------------------------------------------")
        for formats in export_formats:
            print(f"// {formats['format']}")
        print("-----------------------------------------------------")
        print("NOTA: Alguns tipos de arquivo suportam apenas um tipo de formato.")            
        print("NOTA: Essa conversão não modificará seu arquivo salvo no Google Drive!\n")
        print("// A = Abortar operação")
        choosed_format = input("=> ").strip().upper()
        
        if choosed_format == "A":
            os.system('cls' if os.name == 'nt' else 'clear')
            return choosed_format

        try:
            format_info = next(formats for formats in export_formats if choosed_format == formats["format"].upper())
            break
        except StopIteration:
            print("ERRO: Formato inválido. Escolha um dos formatos acima!")
            continue
    
    file_name = check_download_dir(f"{file_info['name']}{format_info['extension']}", download_dir)
    file = io.FileIO(f"{Path.joinpath(download_dir, file_name)}", "wb")

    # Google Drive export() method has a 10MB file size limit.
    # If the file is larger than 10MiB, the program will use a
    # direct GET request through a export URL instead of using export()
    if int(file_info["size"]) > 10485760:
        access_token = creds.token
        download_url = file_info["exportLinks"][format_info["mimetype"]] 
        header={'Authorization': 'Bearer ' + access_token}
        print("AVISO: Arquivo é muito grande para usar o método export.\n"
            "Tentando download direto via requisição HTTP. Isto pode demorar um pouco...") 
        request = requests.get(download_url, headers=header, stream=True)
        file_size = len(request.content)
        total_transfered = 0

        progress_bar = load_progress_bar(file_size, "Fazendo Download")
        for chunk in request.iter_content(chunk_size=8196):
            if chunk:
                file.write(chunk)
                total_transfered += len(chunk)
                progress_bar.n = total_transfered
                progress_bar.refresh()

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
                progress_bar = load_progress_bar(downloader._total_size, "Fazendo download")
                sleep(0.5)
                pbar_loaded = True
            progress_bar.n = status.resumable_progress
            progress_bar.refresh()
           #print(F'Download {int(status.progress() * 100)}.')
    progress_bar.close()
    file.close()

def check_download_dir(file_name, download_dir):
    while True:
        if Path.joinpath(download_dir, file_name).exists():
            print(f"\nAVISO: O arquivo {file_name} já está presente no diretório de download.")
            print("// S = Substituir o arquivo.")
            print("// C = Baixar como cópia.\n")
            choice = input("=> ").strip().upper()

            if choice != "S" and choice != "C":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("ERRO: Escolha uma opção válida!\n")

            elif choice == "S":
                    return file_name

            else:
                return  f"Copy of {file_name}"
        else:
            return file_name
            
if __name__ == "__main__":
    main()

