# ===============================================================================
# Slightly modified code from XtremeRahul"s gdrive_folder_size project
# Check => https://github.com/XtremeRahul/gdrive_folder_size
# Thanks for your project!!
# ===============================================================================

from timeit import default_timer
from constants import UNSUPPORTED_MIMETYPES, DRIVE_EXPORT_FORMATS

class GoogleDriveSizeCalculate:
    def __init__(self, service):
        self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__service = service
        self.total_bytes = 0
        self.total_files = 0
        self.total_folders = 0
        self.total_unsupported_files = 0
        self.google_workspace_files = 0
        self.start = default_timer()
        self.timeout = False

    def gdrive_checker(self, file_id):              
        error = False
        try:
            drive_file = self.__service.files().get(fileId=file_id, 
                                                    fields="id, name, mimeType, size").execute()
            name = drive_file["name"]
            if drive_file["mimeType"] == self.__G_DRIVE_DIR_MIME_TYPE:
                self.total_folders += 1
                self.gDrive_directory(**drive_file)
            else:
                self.total_files += 1
                self.gDrive_file(**drive_file)

        except Exception as e:
            print("\n")
            if "HttpError" in str(e):
                h_e = str(e)
                ori = h_e
                try:
                    h_e = h_e.replace("<", "").replace(">", "")
                    h_e = h_e.split("when")
                    f = h_e[0].strip()
                    s = h_e[1].split(""")[1].split(""")[0].strip()
                    e =  f"{f}\n{s}"
                except:
                    e = ori
            print(str(e))
            error = True
        finally:
            if error:
                return
            elif self.timeout == True:
                return "Timeout"
            else:
                # Import is here to avoid a circular import error 
                from app_tqdm import convert_filesize
                return {"Archive": name,
                        "Size": convert_filesize(self.total_bytes),
                        "Files": self.total_files,
                        "Folders": self.total_folders,
                        "Google Workspace Files": self.google_workspace_files,
                        "Unsupported files (Google Forms, Sites or Maps)": self.total_unsupported_files,
                        "Bytes": self.total_bytes}
                    

    def list_drive_dir(self, file_id: str) -> list:
            query = f"'{file_id}' in parents and (name contains '*') and trashed=false"
            fields = "nextPageToken, files(id, mimeType, size)"
            page_token = None
            page_size = 1000
           
            while True:
                response = self.__service.files().list(q=query, pageToken=page_token,
                                                    fields=fields, corpora="user",
                                                    pageSize=page_size,
                                                    orderBy="folder, name").execute()
                                               
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
            return response["files"]

    def gDrive_file(self, **kwargs):

        try:
            size = int(kwargs["size"])
        except:
            size = 0
        self.total_bytes += size

    def gDrive_directory(self, **kwargs) -> None:
        elapsed_time = default_timer() - self.start
        if elapsed_time >= 10:
            self.timeout = True
            return
        files = self.list_drive_dir(kwargs["id"])    
        if len(files) == 0:
            return
        for file_ in files:
            if file_["mimeType"] == self.__G_DRIVE_DIR_MIME_TYPE: 
                self.total_folders += 1
                self.gDrive_directory(**file_)
            
            elif file_["mimeType"] in UNSUPPORTED_MIMETYPES:
                self.total_unsupported_files += 1

            elif file_["mimeType"] in DRIVE_EXPORT_FORMATS.keys():
                self.google_workspace_files += 1
                self.gDrive_file(**file_)
            else:
                self.total_files += 1
                self.gDrive_file(**file_)
                    