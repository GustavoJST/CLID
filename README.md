<img src="/assets/banner.gif" width="100%"/>

<div align="center">
    <h3 align="center">CLID</h3>

A simple, Python based program for downloading/uploading Google Drive files and folders directly from the terminal. 

Python 3.10+ required. Windows/Linux compatible.

For the Portuguese (pt-BR) version of this README, [click here](README-pt-br.md).

**Read the [documentation](docs/guide.md/#table-of-contents) for information on how to setup and use CLID.**
   
<a href="https://github.com/GustavoJST/CLID/labels/bug">Report Bug</a>
    ·
<a href="https://github.com/GustavoJST/CLID/labels/request">Request Feature</a> 
</div>

<details>
 <summary> Table of contents</summary>

- [About the project](#about-the-project)
- [Limitations](#limitations)
</details>

# About the project
CLID (short for CLI Drive) is a simple program whose main purpose is to download/upload files and folders, as well as calculating the size of folders, from Google Drive, using only the terminal. 

CLID was made using the [Google API Python client library](https://github.com/googleapis/google-api-python-client) for API communication with Google Drive, [tqdm](https://github.com/tqdm/tqdm) for the progress bars and [gdrive_folder_size](https://github.com/XtremeRahul/gdrive_folder_size) to help calculate the size of Google Drive folders.

The project idea came from a problem in sincronyzing a folder between my desktop computer and my laptop that I use to study. I was using Google Drive to sync it, but it was getting really repetitive doing it everyday (small repetitive tasks, like opening the browser, downloading the file, unziping it, replacing it... you get the idea). Because of that, I came up with the ideia of making a Python program/script that would handle most of the boring stuff for me, without even having to open my browser.
<br><br>

## Cool story bro... but what can it do? <!-- omit in toc -->
Here's a list of what CLID can and cannot do:

### CLID can: <!-- omit in toc -->
- Download files and folders created/owned by you, or shared with you.
- Upload files/folders.
- Calculate a Google Drive folder size.
- Export Google Workspace files to different formats when downloading.
- Streamline the upload/download process by compressing/extracing folders when needed.
- Handle duplicate files in your Google Drive or local system when uploading/downloading.

### CLID can't: <!-- omit in toc -->
- Download multiple files/folders at a time.
- Interact with Google Drive in any other way that is not one of the features already said above. That includes moving files to different places in Google Drive, sharing files/folders with others, changing the visibility settings for a file, or any other Google Drive feature.
- Download files/folders that are not in the Drive's root directory (AKA main folder/page), with the exception of the files/folders shared with the user. You can, however, download a folder in the root directory, along with all its files and subfolders (no matter how deep the rabbit hole is).
- Make coffee :( . Yet...
<br><br>


# Limitations
- Folder downloads are slower than file downloads. If you find it too slow, it's best to upload/download folders as a compressed file.
- Downloads/uploads are made in chunks as to not load the user's system memory if the file is too big. The problem is that the Python API client for Google Drive is kinda slow at getting requests. To mitigate this and maintain efficiency, the size of each chunk is 100MB. Altough you can change this value in the code, doing so will result in slower downloads speeds.
- Due to the 100MB chunk size mentioned above, progress bars will only update 100MB at a time, which may take some time depending on how fast your internet download speed is. If you change the chunk size, then the progress bar will update accordingly, but your download speed **will** descrease.
- Only one file/folder can be downloaded at a time.
- CLID can only download files that were shared with the user or that are in the Drive's root directory (AKA main folder/page). This means that if you want to download a file/folder that is inside another folder, you'll have to either you download the entire folder that's in the root directory, or download the file/folder you want outside CLID.