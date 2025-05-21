# File Autodelete Utility

## Introduction

The File Autodelete Utility is a desktop application designed to help you automatically manage disk space by deleting files older than a specified number of days from a designated folder. It provides a user-friendly interface to select a folder, set the age threshold for deletion, and continuously monitors the folder in the background.

### Purpose

This tool is particularly useful for:
* Cleaning up folders that accumulate temporary files, logs, or old downloads.
* Automating the removal of outdated backups or archived data.
* Maintaining free disk space by regularly purging old files according to your criteria.

## Key Features

* **Folder Monitoring:** Continuously monitors a selected folder for files to delete.
* **Age-Based Deletion:** Allows users to specify the number of days after which files should be considered old and eligible for deletion (based on file modification time).
* **Background Operation:** The monitoring and deletion process runs in a separate thread, keeping the GUI responsive.
* **Start/Stop Control:** Users can easily start and stop the monitoring process.
* **User-Friendly Interface:** Built with CustomTkinter for a modern look and feel.
* **Activity Logging (GUI):** Displays real-time activity and messages within the application window.
* **Session-Based File Logging:** Creates a unique, timestamped log file for each program run, stored in a dedicated `app_run_logs` folder, detailing all operations and errors.
* **Configurable Monitoring Interval:** Checks the folder at a defined interval (default is 60 seconds, can be adjusted in the code).
* **Supported File Types for Deletion:** By default, it checks common image, document, and archive files (e.g., .png, .jpg, .log, .txt, .zip). This can be extended in the code.

## Without Python
Those people who want to use this program in production with real time `without installing the python can get PictureAutoDelete.exe ` . Contact me below 
  ```
  Email : shergillkuldeep@outlook.com
  ```

## Requirements

* Python 3.7 or newer
* Libraries:
    * CustomTkinter (`customtkinter`)

## Installation

1.  Ensure you have Python 3 installed on your system.
2.  Install the required library using pip:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Save the program code as a Python file (e.g., `main.py`).
2.  Ensure you have an `icon/logo.ico` file in a subfolder named `icon` relative to the script, or modify/remove the `app_icon_path` in the script if you don't have an icon.
3.  Open a terminal or command prompt.
4.  Navigate to the directory where you saved the file.
5.  Run the script using:
    ```bash
    python main.py
    ```
    This will launch the graphical user interface.

## User Manual

The application interface is designed for ease of use:

### 1. Monitor Folder

* **Purpose:** Select the folder that the application will monitor for old files.
* **How to use:** Click the **Browse** button next to "Monitor Folder:" to navigate your file system and choose the target directory. The selected path will appear in the entry field.

### 2. Delete files older than: (Slider)

* **Purpose:** Set the age threshold for file deletion. Files older than this many days (based on their last modification date) will be deleted.
* **How to use:**
    * Drag the **slider** to select the number of days. The default is 7 days. The range is 0 to 365 days.
    * The label next to the slider will update in real-time to show the selected number of days (e.g., "7 days").
    * A value of "0 days" means files modified any time before the current moment today will be deleted.

### 3. Start Monitoring

* **Purpose:** Initiates the continuous background monitoring and deletion process.
* **Action:** When clicked:
    1.  The application verifies that a folder has been selected.
    2.  It starts a background thread that will periodically (e.g., every 60 seconds) scan the "Monitor Folder".
    3.  During each scan, it identifies files whose last modification date is older than the "Delete files older than" setting.
    4.  **Identified old files are permanently deleted.**
    5.  The "Start Monitoring" button will be disabled, and the "Stop Monitoring" button will be enabled. Input fields will also be disabled.

### 4. Stop Monitoring

* **Purpose:** Halts the active background monitoring and deletion process.
* **Action:** When clicked:
    1.  A signal is sent to the background monitoring thread to stop its operations. The thread will finish its current check (if any) and then terminate.
    2.  The "Stop Monitoring" button will be disabled, and the "Start Monitoring" button will be enabled. Input fields will also be re-enabled.

### 5. Activity Log (In-App)

* **Location:** The text box at the bottom of the application window.
* **Purpose:** Displays real-time status messages, including when monitoring starts/stops, which folder is being checked, files that are deleted, and any errors encountered.

## Log Files

For detailed auditing and troubleshooting, the application maintains comprehensive log files:

* **Location:** A folder named `app_run_logs` will be automatically created in the same directory where the application script is located.
* **Naming Convention:** Each time the application is run, a new log file is generated with a unique timestamp, e.g., `app_session_YYYY-MM-DD_HH-MM-SS.log`. This ensures that logs from previous sessions are preserved.
* **Content:** These files record all significant events, including application initialization, start/stop of monitoring, specific files deleted (with their modification dates), and any errors that occurred during the process.

## Important Notes

* **⚠️ PERMANENT DELETION:** Files identified as "old" by this utility are **permanently deleted** from your system. They are **NOT** moved to a Recycle Bin or Trash.
* **TEST CAREFULLY:** It is strongly recommended to test this application on a sample folder with non-critical files first to understand its behavior and ensure it works as you expect.
* **BACKUP IMPORTANT DATA:** Always ensure you have backups of any important data before using a utility that performs automated file deletions.
* **File Modification Times:** The application uses the "last modified" timestamp of files to determine their age.
* **Monitoring Interval:** The background process checks the folder at a set interval (default: 60 seconds). This means there might be a delay of up to this interval before an old file is detected and deleted after monitoring starts.

---

