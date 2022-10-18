""" Since all downloads/uploads in this program are set to resumable=True, these actions
are performed in chunks. Set the desired chunk size (in bytes), in the
variable below.  
NOTE: There are some restrictions with chunk sizes. For files larger than 256KB,
use CHUNK_SIZE values that are multiples of 256KB (1024 * 256 * some_value).
For files smaller than 256KB, there are no restrictions. """
  
# For the best efficiency, try to keep the chunk size as close to the default
# value as possible (104857600) -> 100MB.
CHUNK_SIZE = 104857600  # Equals to 100MB. Default Google Drive chunk size value. 
OPTIONS = ["D", "C", "S", "E"]

GOOGLE_WORKSPACE_MIMETYPES = {"application/vnd.google-apps.script": "Script",
                            "application/vnd.google-apps.presentation": "Presentation",
                            "application/vnd.google-apps.jam": "Jamboard",
                            "application/vnd.google-apps.document": "Docs",
                            "application/vnd.google-apps.drawing" : "Drawing",
                            "application/vnd.google-apps.folder" : "Folder",
                            "application/vnd.google-apps.spreadsheet": "Spreadsheet",
                            "application/vnd.google-apps.form": "*Form",
                            "application/vnd.google-apps.map": "*Map",
                            "application/vnd.google-apps.site": "*Site",
                            "application/vnd.google-apps.photo": "Photo",
                            "application/vnd.google-apps.shortcut": "*Shortcut",
                            "application/vnd.google-apps.drive-sdk": "*3rd Pt Shortcut"}
                            
DRIVE_EXPORT_FORMATS = {"application/vnd.google-apps.script": 
                            [{"format": "JSON", "mimetype": "application/vnd.google-apps.script+json", "extension": ".json"}],
                        
                        "application/vnd.google-apps.presentation": 
                            [{"format": "MS PowerPoint", "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "extension": ".pptx"},
                            {"format": "PDF", "mimetype": "application/pdf", "extension": ".pdf"}],
                        
                        "application/vnd.google-apps.jam": 
                            [{"format": "PDF", "mimetype": "application/pdf", "extension": ".pdf"}],

                        "application/vnd.google-apps.document": 
                            [{"format": "MS Word", "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "extension": ".docx"}, 
                            {"format": "HTML", "mimetype": "text/html", "extension": ".html"},
                            {"format": "Plain Text", "mimetype": "text/plain", "extension": ".txt"},
                            {"format": "PDF", "mimetype": "application/pdf", "extension": ".pdf"}],

                        "application/vnd.google-apps.drawing": 
                            [{"format": "PNG", "mimetype": "image/png", "extension": ".png"},
                            {"format": "JPEG", "mimetype": "image/jpeg", "extension": ".jpeg"},
                            {"format": "SVG", "mimetype": "image/svg+xml", "extension": ".svg"},
                            {"format": "PDF", "mimetype": "application/pdf", "extension": ".pdf"}],

                        "application/vnd.google-apps.spreadsheet":
                            [{"format": "MS Excel", "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "extension": ".xlsx"},
                            {"format": "CSV", "mimetype": "text/csv", "extension": ".csv"},
                            {"format": "PDF", "mimetype": "application/pdf", "extension": ".pdf"}]}

# Google Drive doesn't return the size for these types of files.
NO_SIZE_TYPES = ["application/vnd.google-apps.folder", 
                "application/vnd.google-apps.map",
                "application/vnd.google-apps.site",
                "application/vnd.google-apps.form",
                "application/vnd.google-apps.script",
                "application/vnd.google-apps.shortcut",
                "application/vnd.google-apps.drive-sdk"]

# Can't download those files directly from the API.
UNSUPPORTED_MIMETYPES = ["application/vnd.google-apps.form",
                        "application/vnd.google-apps.map",
                        "application/vnd.google-apps.site",
                        "application/vnd.google-apps.shortcut",
                        "application/vnd.google-apps.drive-sdk"]