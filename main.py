import os
import customtkinter as ctk
from tkinter import filedialog, messagebox 
from collections import deque
import threading
import logging
from datetime import datetime, timedelta, date

from utility import FileWatcher 

#--- Global Varibalbe for the logs directory----
LOGS_DIRECTORY = "app_run_logs"

class ImageProcessingApp(object):
    """
    Main application class for the image processing and file watching GUI.
    """
    def __init__(self, root_window):
        """
        Initializes the main application window.
        """
        self.root = root_window
        self.root.title("Picture Autodelete Utility")
        self.root.geometry("750x550")
        self.root.iconbitmap(r"icon\logo.ico")
        self.root.minsize(700, 500)
        self.setup_logging()
        self.log_queue = deque(maxlen=200)

        self.watcher_thread = None
        self.is_watching = False
        self.image_processor = None
        self.watcher = None

        # To store the slider's current value
        self.selected_days_value = 0 

        # --- Button Styling ---
        self.button_corner_radius = 8
        self.button_fg_color = ("#5DADE2", "#2E86C1")  
        self.button_hover_color = ("#85C1E9", "#3498DB")
        self.button_text_color = ("#FFFFFF", "#FFFFFF")
        self.button_border_width = 0
        self.button_border_spacing = 5

        self.create_widgets()
        self.update_log_display_periodically() 
    
    def setup_logging(self):
        """
        Configures logging to create a new timestamped log file in a 'logs' directory
        for each application run.
        """
        if not os.path.exists(LOGS_DIRECTORY):
            try:
                os.makedirs(LOGS_DIRECTORY)
            except OSError as e:
                print(f"CRITICAL: Could not create logs directory '{LOGS_DIRECTORY}': {e}")
                return

        current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"app_session_{current_time_str}.log"
        log_filepath = os.path.join(LOGS_DIRECTORY, log_filename)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        try:
            file_handler = logging.FileHandler(log_filepath, mode='w')
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except IOError as e:
            print(f"CRITICAL: Could not create file handler for '{log_filepath}': {e}")

        logging.info(f"Logging initialized. Log file: {log_filepath}")


    def create_widgets(self):
        """
        Creates the UI elements.
        """
        self.root.grid_columnconfigure(1, weight=1) 

        # --- Input Folder Selection ---
        self.input_folder_label = ctk.CTkLabel(self.root, text="Monitor Folder:")
        self.input_folder_label.grid(row=0, column=0, padx=(20, 5), pady=10, sticky="w")

        self.input_folder_entry = ctk.CTkEntry(self.root, placeholder_text="Path to folder with original images")
        self.input_folder_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.browse_input_button = ctk.CTkButton(
            self.root, text="Browse", command=self.select_input_folder,
            corner_radius=self.button_corner_radius, fg_color=self.button_fg_color,
            hover_color=self.button_hover_color, text_color=self.button_text_color,
            border_width=self.button_border_width, width=100
        )
        self.browse_input_button.grid(row=0, column=2, padx=(5, 20), pady=10, sticky="e")

        # --- Days Slider ---
        self.set_days_label = ctk.CTkLabel(self.root, text="Set Number of Days:") 
        self.set_days_label.grid(row=1, column=0, padx=(20, 5), pady=10, sticky="w") 

        self.set_days_slider = ctk.CTkSlider(self.root, from_=0, to=365,
                                        # width=1000, # Width is better controlled by grid sticky
                                        orientation= "horizontal",
                                        command=self._update_days_label) # Link command to update method
        self.set_days_slider.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="ew") # Use sticky="ew" for responsiveness
        self.set_days_slider.set(0) # Set initial value for the slider (e.g., 0 days)

        self.slider_days_selection_label = ctk.CTkLabel(self.root, text="0 days") # Initialize with default text
        self.slider_days_selection_label.grid(row=1, column=2, padx=(10, 20), pady=10, sticky="w") # Use sticky="w"


        # --- Control Buttons ---
        controls_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        controls_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=20, sticky="ew")
        controls_frame.grid_columnconfigure((0,1), weight=1) # Distribute space

        self.start_button = ctk.CTkButton(
            controls_frame, text="Start Watching", command=self.start_watching,
            corner_radius=self.button_corner_radius, fg_color=("green", "darkgreen"), # Specific color for start
            hover_color=("#A9DFBF", "#58D68D"), text_color=self.button_text_color,
            height=35, font=("Arial", 13, "bold")
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            controls_frame, text="Stop Watching", command=self.stop_watching, state="disabled",
            corner_radius=self.button_corner_radius, fg_color=("red", "darkred"), # Specific color for stop
            hover_color=("#F5B7B1", "#EC7063"), text_color=self.button_text_color,
            height=35, font=("Arial", 13, "bold")
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # --- Log Display ---
        self.log_label = ctk.CTkLabel(self.root, text="Activity Log:")
        self.log_label.grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")

        self.log_text = ctk.CTkTextbox(self.root, state="disabled", height=150, wrap="word")
        self.log_text.grid(row=4, column=0, columnspan=3, padx=20, pady=(0,10), sticky="nsew")
        self.root.grid_rowconfigure(4, weight=1) 

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self.root, text="Status: Idle", text_color="gray", font=("Arial", 12, "italic"))
        self.status_label.grid(row=5, column=0, columnspan=3, padx=20, pady=(5,10), sticky="w")

        # --- Status Label ---
        self.Creator_label = ctk.CTkLabel(self.root, text="Creator : Aby | Repo: github.com/abyshergill | License: Apache 2.0", text_color="gray", font=("Arial", 12, "bold"))
        self.Creator_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(5,10), sticky="w")


    def select_input_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Monitor")
        if folder_path:
            self.input_folder_entry.delete(0, ctk.END)
            self.input_folder_entry.insert(0, folder_path)
            self.add_log_message(f"Input folder selected: {folder_path}")

    def _update_days_label(self, value):
        """
        Called when the slider value changes. Updates the label.
        The 'value' argument is automatically provided by the CTkSlider's command.
        """
        self.selected_days_value = int(value)
        self.slider_days_selection_label.configure(text=f"{self.selected_days_value} days")

    def start_watching(self):
        input_folder_path = self.input_folder_entry.get().strip()

        if not input_folder_path:
            messagebox.showerror("Input Error", "Please select or enter an input folder path to monitor.")
            self.add_log_message("Error: Input folder path is empty.")
            return
        if not os.path.exists(input_folder_path) or not os.path.isdir(input_folder_path):
            messagebox.showerror("Input Error", f"The input folder path does not exist or is not a directory:\n{input_folder_path}")
            self.add_log_message(f"Error: Invalid input folder path: {input_folder_path}")
            return

        if self.is_watching:
            self.add_log_message("Already watching. Please stop the current session first.")
            return
        
        if not input_folder_path:
            messagebox.showerror("Error", "Please select a folder first.")
            self.add_log_message("Error: Start Autodelete attempted without selecting a folder.")
            return



        #self.image_processor = ImageProcessor(output_folder=output_folder_path)
        self.watcher = FileWatcher(input_folder_path, self.selected_days_value, self.add_log_message) # Pass callback

        self.watcher_thread = threading.Thread(target=self.watcher.watch, daemon=True)
        self.watcher_thread.start()

        self.is_watching = True
        self.update_ui_for_watch_state(True, input_folder_path)
        #self.add_log_message(f"Started watching '{os.path.basename(input_folder_path)}'. Output to '{os.path.basename(output_folder_path)}'.")


    def stop_watching(self):
        if self.is_watching and self.watcher:
            self.add_log_message("Stopping file watcher...")
            self.watcher.stop()
            if self.watcher_thread and self.watcher_thread.is_alive():
                self.watcher_thread.join(timeout=5)
                if self.watcher_thread.is_alive():
                    self.add_log_message("Warning: Watcher thread did not terminate gracefully.")
                    logging.warning("Watcher thread did not terminate in time.")

            self.is_watching = False
            self.update_ui_for_watch_state(False)
            self.add_log_message("Stopped watching folder.")
        else:
            self.add_log_message("Not currently watching or watcher not initialized.")


    def update_ui_for_watch_state(self, watching, folder_name=""):
        if watching:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.browse_input_button.configure(state="disabled")
            self.input_folder_entry.configure(state="disabled")
            self.status_label.configure(text=f"Status: Watching '{os.path.basename(folder_name)}'...", text_color="green")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.browse_input_button.configure(state="normal")
            self.input_folder_entry.configure(state="normal")
            self.status_label.configure(text="Status: Idle", text_color="gray")

    def add_log_message(self, message):
        """
        Adds a message to the log queue for display and logs it to file.
        This method is thread-safe for appending to deque and logging.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}"
        self.log_queue.append(log_entry)
        logging.info(message)

    def update_log_display_periodically(self):
        """
        Periodically updates the log display with new entries.
        Runs in the main Tkinter thread.
        """
        self.log_text.configure(state="normal")
        current_log_content = self.log_text.get("1.0", ctk.END).strip()
        new_log_entries = "\n".join(list(self.log_queue))

        if current_log_content != new_log_entries: 
            self.log_text.delete("1.0", ctk.END)
            for log_entry in self.log_queue: 
                self.log_text.insert(ctk.END, log_entry + "\n")
            self.log_text.see(ctk.END) 
        self.log_text.configure(state="disabled")

        self.root.after(500, self.update_log_display_periodically) 


    def on_closing(self):
        """
        Handles the window closing event.
        """
        if self.is_watching:
            # Give a chance to confirm or stop gracefully
            if messagebox.askyesno("Confirm Exit", "The file watcher is active. Are you sure you want to exit? This will stop the watcher."):
                self.stop_watching()
                self.root.destroy()
            else:
                return 
        else:
            self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("Light") # System, Dark, Light
    ctk.set_default_color_theme("blue") # blue, dark-blue, green

    app_root = ctk.CTk()
    app = ImageProcessingApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app_root.mainloop()