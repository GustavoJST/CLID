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

def compact_directory(file_dir): 
    # English: "File identified as a directory. Starting compaction..."
    print("\n=> Arquivo identificado como diretório. Iniciando compactação...")
    sleep(1)
    target_path = Path(f"{file_dir}.zip")
    local_filename = target_path.name
    
    total_files = 0
    for file in file_dir.rglob("*"):
        total_files += 1         
    
    with ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zfile:
        for files in tqdm(file_dir.rglob("*"), total=total_files, desc="Compactando ", dynamic_ncols=True):
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
    print("\nIniciando upload... (Aperte Ctrl+C para abortar)")
    sleep(1)
    progress_bar = load_progress_bar("Fazendo upload", file_size) 
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
    # English: Upload completed successfully!
    print("\nUpload concluído com sucesso!")


def remove_localfile(file_dir):
    if file_dir.exists:
        # English: Removing the created .zip file form the system...
        print("\nRemovendo arquivo ZIP do sistema...")
        sleep(1)
        file_dir.unlink()
        # English: Local .zip file removed successfully!
        print("\nRemoção do arquivo local concluido!")
    else:
        # English: ERROR: File {file_dir} doesn't exist in the system. Aborting operation...
        print(f"\nERRO: Arquivo {file_dir} não existe no sitema. Pulando operação...\n")

# TODO: Será que existe uma maneira de printar automaticamente até o tamanho do
# terminal, e não um valor fixo?
def list_drive_files(search_results, GOOGLE_WORKSPACE_MIMETYPES):
    counter = 1
    print("\nOs seguintes arquivos foram encontrados: ")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(f"{'Num':^4}  | {'Tipo':^14} | {'Tamanho':^11}    |   Nome do Arquivo")
    print("---------------------------------------------------------------------------------------------------------------------------")
    for drive_file in search_results:

        if drive_file["mimeType"] in constants.NO_SIZE_TYPES:
            print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {'-----':^11} --->   {drive_file['name']}")
        
        elif drive_file["mimeType"] in constants.GOOGLE_WORKSPACE_MIMETYPES.keys():
             print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}") 

        else:
            print(f"#{counter:>4} | {'File':^14} | {convert_filesize(drive_file['size']):^11} --->   {drive_file['name']}")
        counter += 1
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("AVISO: Arquivos com o tipo marcado com '*' não possuem suporte para download.")
    
def list_skipped_files(skipped_files, GOOGLE_WORKSPACE_MIMETYPES):
    counter = 1
    print("\nThe following items were skipped:")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(f"{'Num':^4}  | {'Tipo':^14}    |  Nome do Arquivo")
    print("---------------------------------------------------------------------------------------------------------------------------")
    for drive_file in skipped_files:
        print(f"#{counter:>4} | {GOOGLE_WORKSPACE_MIMETYPES[drive_file['mimeType']]:^14} --->  {drive_file['name']}")
        counter += 1
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("Download the files directly from Google Drive if you need them.")
    
def list_folders(search_results):
    counter = 1
    print("\nThe following folders were found:")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(f"{'Num':^4}  |  Folder name")
    print("---------------------------------------------------------------------------------------------------------------------------")
    for drive_file in search_results:
        print(f"#{counter:>4} |  {drive_file['name']}")
        counter += 1
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("NOTE: Listing only folders present in Google Drive's 'root' directory.")  

def print_file_stats(file_name=None, file_size=None, folder_mode=False, folder_stats=None):
    if folder_mode == True:
        print("-------------------------------------------------------------------------------------------------")
        for key, value in folder_stats.items():
            # folder_size_calc needs to return the total folder size in bytes, but we
            # don't want to print it in here, as we're already printing the converterd
            # folder size.
            if key != "Bytes":
                print(f"// {key}: {value}")
        print("-------------------------------------------------------------------------------------------------\n")
    else:   
        print("-------------------------------------------------------------------------------------------------")
        print(f"// Arquivo: {file_name}")
        print(f"// Tamanho: {convert_filesize(int(file_size))}")
        print("-------------------------------------------------------------------------------------------------\n")
        sleep(1)

def prepare_directory(download_dir, gdrive_folder_name):
    folder_path = Path.joinpath(download_dir, gdrive_folder_name)
    try:
        if not folder_path.exists():
            folder_path.mkdir()
            return folder_path
        else:
            return folder_path

    # TODO: Aparentemente,  fazer download colocando a opção de substituir a
    # pasta retorna OSError. Fix this! Talvez colocar um check de se a pasta
    # exitir, continuar sem fazer nada.
    except OSError:
        print("\nERRO: Caractere inválido detectado no nome da pasta. Mude o nome da pasta retirando o caractere inválido [\\ / ? : * < > | \"].")
        print("Encerrando programa...")
        sleep(0.5)
        exit()

def check_download_dir(file_name, download_dir):
        while True:
            if Path.joinpath(download_dir, file_name).exists():
                print(f"\nWARNING: O arquivo {file_name} já está presente no diretório {download_dir}.")
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
            # Default case
            else:
                return file_name

def load_progress_bar(description, total_file_size=None):
    bar_format = "{desc}: {percentage:3.1f}%|{bar}| {n_fmt}B/{total_fmt}B [{elapsed}<{remaining}, {rate_fmt}]"
    return tqdm(total=int(total_file_size), desc=description, miniters=1, bar_format=bar_format, 
                unit="B", unit_scale=True, unit_divisor=1024, dynamic_ncols=True, leave=True)

class DownloadSystem:
    total_skipped = 0
    skipped_files = []
    def __init__(self, progress_bar=None, unknown_folder_size=False, folder_mode=False, access_token=None):
        self.progress_bar = progress_bar
        self.unknown_folder_size = unknown_folder_size
        self.unknown_folder_size = unknown_folder_size
        self.folder_mode = folder_mode
        self.access_token = access_token
        """ self.total_skipped = 0
        self.skipped_files = [] """
                 
    def get_files(self, folder_id, directory, drive):
        search_request = drive.files().list(corpora="user", 
                                            fields="files(id, name, size, mimeType, exportLinks)", 
                                            q=f"'{folder_id}' in parents and trashed=false").execute()
              
        for file in search_request["files"]:
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
            request = drive.files().get_media(fileId=file_info["id"])
            file = io.FileIO(f"{file_path}", "w")
        
        downloader = MediaIoBaseDownload(file, request, chunksize=constants.CHUNK_SIZE)
        done = False
        while done == False:
            status, done = downloader.next_chunk()
            if self.folder_mode == True:                        
                """ Folder size is calculated based on the size of the files inside
                the folder, but when exporting files to a different format, they
                can increase or decrease in size (depending on the format).
                Because of this change, the progress bar can surpass the maximum
                size value, or not reach it. The code below fix this behavior. """
                chunk = self.progress_bar.n + (status.resumable_progress - self.progress_bar.n)
                if (chunk + self.progress_bar.n) >= self.progress_bar.total:
                    self.progress_bar.n = self.progress_bar.total
                    self.progress_bar.refresh() 
                
                else:    
                    #progress_bar.update(Path(file_path).stat().st_size)
                    self.progress_bar.update(chunk)                   
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
        # English: WARNING: Google Workspace File detected!
        while True:
            print("\nAVISO: Arquivo do Google Workspace detectado!")
            # English: WARNING :{file_info['name']} can't be downloaded directly and needs to be exported to another format beforehand.
            print(f"AVISO: O arquivo {file_info['name']} não pode ser baixado diretamente e precisa ser convetido antes.\n")
            print("Digite um dos formatos abaixo para converter o arquivo a ser baixado:")
            print("-----------------------------------------------------")
            for formats in export_formats:
                print(f"# {formats['format']}")
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
                os.system('cls' if os.name == 'nt' else 'clear')
                print("ERRO: Formato inválido. Escolha um dos formatos acima!")
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
                    progress_bar = load_progress_bar("Fazendo download", downloader._total_size)
                    sleep(0.5)
                    pbar_loaded = True
                progress_bar.n = status.resumable_progress
                progress_bar.refresh()
            #print(F'Download {int(status.progress() * 100)}.')
        file.close()
    
    def download_by_http(self, file_info, file, format_mimetype=None):
        download_url = file_info["exportLinks"][format_mimetype] 
        header={'Authorization': 'Bearer ' + self.access_token}
        if self.folder_mode == False:
            print("AVISO: Arquivo é muito grande para usar o método export.\n"
                "Tentando download direto via requisição HTTP. Isto pode demorar um pouco...")
        
        request = requests.get(download_url, headers=header, stream=True)
        file_size = len(request.content)
        total_transfered = 0
        if self.folder_mode == False:
            progress_bar = load_progress_bar("Fazendo Download", file_size)
        for chunk in request.iter_content(chunk_size=8196):
            if chunk:
                file.write(chunk)
                total_transfered += len(chunk)
                
                if self.folder_mode == False:
                    progress_bar.n = total_transfered
                    progress_bar.refresh()
                    
                else:
                    if (self.progress_bar.n + len(chunk)) > self.progress_bar.total:
                        self.progress_bar.n = self.progress_bar.total
                        self.progress_bar.refresh() 
                        
                    else:    
                        self.progress_bar.update(len(chunk))
        if self.folder_mode == False:
            progress_bar.close()
        file.close()