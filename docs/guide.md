
# Table of contents <!-- omit in toc -->
- [Quickstart](#quickstart)
  - [Google Cloud project setup](#google-cloud-project-setup)
  - [Windows installation](#windows-installation)
  - [Linux installation](#linux-installation)
  - [First Run](#first-run)
  - [Moving the CLID folder](#moving-the-clid-folder)
- [User guide](#user-guide)
  - [Downloading](#downloading)
  - [Uploading](#uploading)
  - [Calculating folder size](#calculating-folder-size)
  - [Settings and preferences](#settings-and-preferences)

<hr>
<br>

# Quickstart
## Google Cloud project setup
To use CLID, you need to create a Google Cloud project. Follow the step-by-step tutorial to set it up. 
1. Open the [Google Cloud Console](https://console.cloud.google.com/getting-started) web page and log in.
2. On the top-left, click on **Select project** and create a new project.
3. Give the project a name (any name will do) and click **Create**
4. Go to the [OAuth Consent](https://console.cloud.google.com/apis/credentials/consent) screen, select your project and set the user type to External.
5. Fill only the necessary fields (App name, support email and developer email). The last two can be the same email you used to log in Google Cloud. After filling the information, skip until you reach **Test Users**.
6. In Test Users, add the emails you want to use with CLID (you can specify one or more emails). After that, click **Save and Continue**.
7. Open the [Google Drive API](https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com?q=search&referrer=search) page, select the project you've created and activate the API.
8. Now, go to the [Credentials](https://console.cloud.google.com/apis/credentials) page and create a new **OAauth Client credential**.
9.  In **Application type**, choose **Desktop app**, give it a name and click **Create**.
10. In the pop-up window that will open, download the **JSON** file.
11. The JSON file will be named **client_secrets_(longStringHere).json**. Rename it to `credentials.json`.
12. Move the `credentials.json` file to the CLID folder (Same place where `CLID.py` is located) after doing the installation steps mentioned below, for your respective operating system.
<br> <br>

## Windows installation
1. Clone/download the repository.
2. Install virtualenv using `pip install virtualenv`.
3. Navigate to the project folder using `cd path/to/[CLID_folder]`.
4. Create a new virtual environment in the project folder, named `CLID_env`, using `virtualenv CLID_env`.
5. Activate the virtual environment by navigating to the `Scripts` folder using `cd CLID_env/Scripts`. After that, type `activate`.
6. After activating the virtual environment, install the required dependencies using `pip install -r requirements.txt`.
7. Open `CLID.py` in the editor, copy the Windows shebang and paste it on the first line of the code.
8. You can then run CLID in the terminal using only `CLID.py` or directly clicking on the `CLID.py` file or a shortcut.
<br><br>

## Linux installation
1. Clone/download the repository.
2. Install virtualenv using `pip install virtualenv`.
3. Navigate to the project folder using `cd path/to/[CLID_folder]`.
4. Create a new virtual environment in the project folder, named `CLID_env`, using `virtualenv CLID_env`.
5. Activate the virtual environment using `source CLID_env/bin/activate`.
6. After activating the virtual environment, install the required dependencies using `pip install -r requirements.txt`.
7. Open `CLID.py` in the code editor, copy the Linux shebang and paste it on the first line of the code.
8. Make `CLID.py` executable by using `chmod u+x CLID.py`.
9. You can then run CLID in the terminal using `./CLID.py`. <br><br> 
 
## First Run
The first time you run CLID, a authentication flow will start, and the browser will open. At last, choose the account in which you want to access its Google Drive with CLID (and remember, only accounts that are **Test Users** will work. Refer to step 6 of [Google Cloud project setup](#google-cloud-project-setup) for more information).<br>

After that, a `token.json` file will be generated from `credentials.json`. If you want to switch accounts, simply delete `token.json`, run CLID and choose another (test user) account in the authentication flow. <br> <br> 

## Moving the CLID folder
Be careful when moving the CLID folder around your system after you've created `CLID_env`. virtualenv created folders will break when being moved, making CLID stop working. <br>

If you need to move the CLID folder another place in your system, delete `CLID_env`, move the CLID folder and redo the virtual environment creation steps, [mentioned above](#windows-installation), for your operating system.
<br><br>    

# User guide
## Downloading
Downloading a file/folder is really easy:

1. From the menu, type `D` to enter the download mode. 
2. Search for the file you want by typing its name, or type `list` to get a list of the files/folders present in your Drive. 
3. Choose the number of the file you want to download
4. Choose a download directory... <br>
    
And that's it! If the file is compressed, you'll get a option to extract it after the download. Supported formats for extraction are `.zip`, `.tar.gz` and `.tar`.  
<br>
Although the download process is simple, there are some important things you need to keep in mind: <br>

### Google Workspace file/folder download <!-- omit in toc -->
In CLID, it's possible to download either a single file or a folder. Note that, when downloading a folder, it's not going to get zipped beforehand. CLID will instead 'copy' your Google Drive folder structure, creating folders in your local system when needed, and downloading the files inside said folders.
<br>

Now, about Google Workspace files. When downloading a Google Workspace file (Docs, Presentation, etc), you'll be able to choose to what format you want the export the file before download. On the other hand, when downloading a folder that has a Google workspace file(s), CLID will choose a export format automatically, and if the file is of an unsupported type, it will skip it.

In conclusion, trying to download a unsupported file will **cancel** the download operation (for single file downloads), or **skip** the file (when downloading folders). You can refer to the table below for information about what export formats are supported for each download mode (single file or folder).<br><br>


| Google Workspace File         | Single file download            | Folder download       |
| ----------------------------- | :-----------------------------: | :-------------------: |
| Google Documents              | MS Word, HTML, Plain Text or PDF| MS Word               |
| Google Slides (Presentation)  | MS PowerPoint or PDF            | MS PowerPoint         |
| Google Sheets                 | MS Excel, CSV or PDF            | MS Excel              |
| Google Jamboard               | PDF                             | PDF                   |
| Google Drawing                | PNG, JPEG, SVG or PDF           | PNG                   |
| Google App Scripts            | JSON                            | JSON                  |
| Google Sites                  | :x: Not supported :x:           | :x: Not supported :x: |
| Google Forms                  | :x: Not supported :x:           | :x: Not supported :x: |
| Google My Maps                | :x: Not supported :x:           | :x: Not supported :x: |

<hr>

## Uploading

Uploading a file with CLID is also very simple:
1. From the menu, type `C` to enter the upload mode.
2. Specify the **absolute path** of the file you want to upload.
   
After the two steps mentioned above, the upload process will begin. If the file is a directory (folder), CLID will automaticaly compress the directory before uploading to Google Drive (you can use a 3rd party app inside Google Drive to unzip the file if you want). <br>

CLID also checks if the file is already present in your Drive, and if it is, it gives you the option to replace the file or to keep both files, renaming the file you're uploading to something like `file(1).zip`. <br><br>

## Calculating folder size
CLID can also calculate the folder size of a Drive folder. It does that by iterating over all files present in the folder, getting their size and adding to a total. At the end of the operation, you'll get a summary with information about the folder's name, size, total number of files, folders, Google Workspace files and unsupported files.<br>

This process can take a while for folder with a lot of subfolders inside. The more **subfolders** a folder has, the longer it will take to calculate its size.


**Important**: Do note that this number is and approximation, as depenending of the contents of the folder, the final size may be different when downloaded in your local system. This happens when dealing with Google Workspace files, mainly because of file size differences, depending of which format the file was exported to (some export format are lighter/heavier than others).
<br><br>

## Settings and preferences
CLID has a  `settings.json` file that lets the user change how CLID behaves.  **For any change you made in `settings.json` to take effect, you'll need to restart CLID**. Here's a rundown of what each setting do: <br><br>

### download_directory (string/null) <!-- omit in toc -->
Allows the user to specify a download directory for all the files/folders downloaded with CLID. If `"download_directory": null`, CLID will ask for a download directory every time you want to download a file.

Example:
`"download_directory": "C:\\Users\\Gustavo\\Downloads"` <br>

 CLID will skip the download directory prompt, and all files/folders downloaded with CLID will end up in the `Downloads` folder. Note that the specified path must be an **absolute path**. 

 By default, this setting value is `null`. <br><br>
 
### upload_path (string/null) <!-- omit in toc -->
Almost the same thing as `download_directory`, but it regards file uploading. Specify a **absolute path** of a file you want to upload, and CLID will skip the prompt for a file path when in upload mode. Really useful if you upload the same file/folder to Google Drive a lot of times. If `"upload_path": null`, CLID will ask for a file path every time you want to upload a file.

Example: `"upload_path": "C:\\Users\\Gustavo\\file.txt"` 

 By default, this setting value is `null`. <br><br>

**IMPORTANT: For both `download_directory` and `upload_path`, remember to use double backslashes ( \\\\ ) or single foward slash ( / ) in the file/directory path.** This is common issue in Windows because when copying the path of a file or directory, it is usually separated using a single backslash ( \\ ), which is not supported by JSON. <br> <br>


### shared_with_me (bool) <!-- omit in toc -->
Modifies how CLID sees and lists your Google Drive files. 
* `false` : CLID will search/list only files and folders **created/owned by the user** when downloading or calculating a folder size.
* `true` : CLID will search/list files and folders **created/owned by the user**, as well as files/folders **shared with the user**, when downloading or calculating a folder size.

By default, this setting value is `false`.<br><br>

### preferred_compression_format (string) <!-- omit in toc -->
Changes the preferred compression format when compressing folders for upload. The supported formats are:
* `".zip"` 
* `".tar.gz"`

Example: 
`"preferred_compression": ".tar.gz"`

If you plan to use CLID to upload/download files that will be used between Windows and Linux systems, it's best to use `.tar.gz` format, as it can help avoid character encoding problems that can occur when using `.zip`.

If you plan to use CLID only on Windows systems, then `.zip` should be enough. If problems with file names appear, try switching to `.tar.gz`.

By default, this setting value is `".tar.gz"`.<br><br>