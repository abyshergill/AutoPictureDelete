# Monitors a folder for new image files and processes them. 

import threading
import logging
import os
import time
from datetime import datetime, timedelta, date


class FileWatcher:
    """
    Monitors a folder for new image files and processes them.
    """
    def __init__(self, folder_path, set_days, log_queue_callback, update_interval=1):
        """
        Initializes the FileWatcher.

        Args:
            folder_path (str): Path to the folder to monitor.
            image_processor (ImageProcessor): Instance of ImageProcessor to handle image processing.
            log_queue_callback (function): Callback function to add messages to the app's log queue.
            update_interval (int): How often to check for new files, in seconds.  Defaults to 1.
        """
        self.folder_path = folder_path
        self.set_days = set_days
        self.log_queue_callback = log_queue_callback # Use callback for logging to app
        self.update_interval = update_interval
        self.stop_flag = threading.Event()
        self.processed_files = set()

    def watch(self):
        """
        Starts monitoring the folder for new image files.
        """
        self.log_message_to_app(f"Watching folder: {self.folder_path}")
        while not self.stop_flag.is_set():

            try:
                days_to_keep = self.set_days 
                #self.log_message_to_app(f"Starting autodelete process for folder: {self.folder_path}, keeping files newer than {self.set_days} days.")
                day_gap = datetime.now() - timedelta(days=days_to_keep)
                for filename in os.listdir(self.folder_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                        file_path = os.path.join(self.folder_path, filename)
                        try :
                            mod_time = os.path.getmtime(file_path)
                            file_datetime = datetime.fromtimestamp(mod_time)
                            if file_datetime < day_gap: 
                                    os.remove(file_path)
                                    log_message = f" {datetime.now()}: Deleted {filename} (Modified: {file_datetime})\n"
                                    self.log_message_to_app(log_message)
                        except OSError as e:
                                error_message = f" {datetime.now()}: Error processing {filename}: {e}\n"
                                self.log_message_to_app(error_message)
                if self.stop_flag.is_set(): break
                time.sleep(self.update_interval)
            except FileNotFoundError:
                 self.log_message_to_app(f"Error: Monitored folder {self.folder_path} not found. Stopping watch.")
                 logging.error(f"Monitored folder {self.folder_path} not found during watch.")
                 break # Exit the loop
            except Exception as e:
                logging.error(f"Error watching folder {self.folder_path}: {e}")
                self.log_message_to_appe(f"Error in watcher: {e}")
                time.sleep(self.update_interval * 2) 

        self.log_message_to_app("File watcher stopped.")


    def log_message_to_app(self, message):
        """
        Uses the callback to add a message to the main application's log queue.
        """
        self.log_queue_callback(message) 

    def stop(self):
        """
        Sets the stop flag, signaling the watching thread to exit.
        """
        self.stop_flag.set()
        logging.info("Stopping file watcher signaled.")