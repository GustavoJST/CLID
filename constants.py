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

GOOGLE_WORKSPACE_MIMETYPES = {"application/vnd.google-apps.script": "Script",
                            "application/vnd.google-apps.presentation": "Presentation",
                            "application/vnd.google-apps.jam": "Jamboard",
                            "application/vnd.google-apps.document": "Docs",
                            "application/vnd.google-apps.drawing" : "Drawing",
                            "application/vnd.google-apps.folder" : "Folder",
                            "application/vnd.google-apps.spreadsheet": "Spreadsheet",
                            "application/vnd.google-apps.form": "Form",
                            "application/vnd.google-apps.map": "Map",
                            "application/vnd.google-apps.site": "Site",
                            "application/vnd.google-apps.photo": "Photo"}
                            
DRIVE_EXPORT_FORMATS = {"application/vnd.google-apps.script",
                                    "application/vnd.google-apps.presentation",
                                    "application/vnd.google-apps.jam",
                                    "application/vnd.google-apps.document",
                                    "application/vnd.google-apps.drawing",
                                    "application/vnd.google-apps.folder",
                                    "application/vnd.google-apps.spreadsheet"}

