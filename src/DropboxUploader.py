import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import filedialog
import time
import pandas as pd
from time import sleep
from up_and_down import UpAndDown


#--------------------------------------------------------------------------
class DropboxUploader(object):
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the GUI
        Args:
            root - root window
        """
        self.root = root
        self.root.title("Dropbox Uploader v1.0.0")
        self.root.geometry("825x315")

        self.login_frame = tk.Frame(root)
        self.login_frame.pack(padx=10, pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:", font=("Helvetica", 16))
        self.password_label.pack(pady=(50, 10))

        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Helvetica", 16))
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login, font=("Helvetica", 16))
        self.login_button.pack(pady=10)

        self.main_frame = None
    

    def login(self) -> None:
        """
        Check if the password is correct
        """
        password = self.password_entry.get()
        if password == "Admin123":
            self.login_frame.destroy()
            self.initialize_main_frame() # Call the initialize_main_frame method without passing self as an argument
        else:
            messagebox.showerror("Login Failed", "Incorrect password. Please try again.")


    def initialize_main_frame(self) -> None:
        """
        Initialize the main frame after logging in
        """
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Create a box to input access token
        self.access_token = tk.StringVar()
        self.token_label = tk.Label(self.main_frame, text="Access Token", font=("Helvetica", 11))
        self.token_label.grid(row=0, column=0, padx=0, pady=2)
        self.token_entry = tk.Entry(self.main_frame, textvariable=self.access_token, font=("Helvetica", 11), width=50)
        self.token_entry.grid(row=0, column=1, columnspan=2, padx=0, pady=2, sticky='w')

        # Create a box to input folder name
        self.dropbox_folder = tk.StringVar()
        self.folder_label = tk.Label(self.main_frame, text="Dropbox Folder", font=("Helvetica", 11))
        self.folder_label.grid(row=1, column=0, padx=0, pady=2)
        self.folder_entry = tk.Entry(self.main_frame, textvariable=self.dropbox_folder, font=("Helvetica", 11))
        self.folder_entry.grid(row=1, column=1, padx=0, pady=2, sticky='w')

        # Create a choice box to select the file type
        self.files_var = tk.StringVar()
        self.files_var.set("Excel Files")  # Set the default value to "United States"
        self.files_choices = ["Excel Files", "CSV Files", "Images Folder"]
        self.files_choice_box = tk.OptionMenu(self.main_frame, self.files_var, *self.files_choices)
        self.files_choice_box.config(width=22)  # Set the width of the choice box
        self.files_choice_box['menu'].config(font=("Helvetica", 11))  # Set the font of the choices in the dropdown menu
        self.files_choice_box.grid(row=1, column=2, padx=0, pady=2, sticky='nsew')

        # Create a button to import images
        self.import_button = tk.Button(self.main_frame, text="Import Images File", command=self.import_file, width=24)
        self.import_button.grid(row=0, column=4, padx=0, pady=2, sticky='w')

        # Create a tree to display session information
        self.tree = ttk.Treeview(self.main_frame, columns=("Session ID", "Status", "Elapsed Time"))
        self.tree.heading("#1", text="Session ID")
        self.tree.heading("#2", text="Status")
        self.tree.heading("#3", text="Elapsed Time")
        self.tree.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky='w')
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)  # Bind event handler

        self.sessions = {}  # Store session information
        self.session_id_counter = 1  # Counter for session IDs
        self.import_lock = threading.Lock()  # Lock for session synchronization


    def import_file(self) -> None:
        """
        Import a file (either directory, CSV, or XLSX) from the user's device.
        """
        # Create a dialog to select the file type
        file_type = self.files_var.get()
        
        if file_type:
            file_types = [("All files", "*.*")]  # Default filter
            if file_type == "Images Folder":
                selected_path = filedialog.askdirectory()
            elif file_type == "CSV Files":
                file_types = [("CSV files", "*.csv"), ("All files", "*.*")]
                selected_path = filedialog.askopenfilename(filetypes=file_types)
            elif file_type == "Excel Files":
                file_types = [("Excel files", "*.xlsx"), ("All files", "*.*")]
                selected_path = filedialog.askopenfilename(filetypes=file_types)
            
            if selected_path:
                session_id = self.session_id_counter
                self.session_id_counter += 1
                self.sessions[session_id] = {
                    "file_path": selected_path,  # Store the file or folder path for this session
                    "status_label": tk.Label(root, text="Waiting for previous session"),
                    "start_time": time.time()
                }
                self.tree.insert("", "end", iid=session_id, values=(session_id, "Waiting...", ""))
                self.run_import(session_id)


    def run_import(self, session_id: int) -> None:
        """
        Run the import process in a separate thread
        Args:
            session_id: int - ID of the session
        """
        import_thread = threading.Thread(target=self.do_import, args=(session_id,))
        import_thread.start()


    def do_import(self, session_id: int) -> None:
        """
        Import the Excel file
        Args:
            session_id: int - ID of the session
        """
        with self.import_lock:
            start_time = time.time()
            self.sessions[session_id]["status_label"].config(text="Running...")
            self.update_status_label(session_id, start_time)
            # Simulate a long-running process
            TOKEN = self.access_token.get()
            FOLDER = self.dropbox_folder.get()
            try:
                loader = UpAndDown(TOKEN, FOLDER)
                output_workbook = loader.up_and_down(dir=self.sessions[session_id]["file_path"])
                self.sessions[session_id]["output_workbook"] = output_workbook
                self.sessions[session_id]["finished"] = True
                elapsed_time = int(time.time() - start_time)
                self.sessions[session_id]["status_label"].config(text="Done")
                self.tree.item(session_id, values=(session_id, "Done", f"{elapsed_time}s"))
            except Exception as e:
                self.sessions[session_id]["finished"] = True
                elapsed_time = int(time.time() - start_time)
                self.sessions[session_id]["status_label"].config(text="Failed")
                self.tree.item(session_id, values=(session_id, "Failed", f"{elapsed_time}s"))
                messagebox.showerror(message=f"error: {str(e)}")


    def update_status_label(self, session_id: int, start_time: float) -> None:
        """
        Update the status label every second
        Args:
            session_id: int - ID of the session
            start_time: float - Start time of the session
        """
        if "finished" not in self.sessions[session_id]:
            elapsed_time = int(time.time() - start_time)
            self.tree.item(session_id, values=(session_id, "Running...", f"{elapsed_time}s"))
            self.root.after(1000, lambda: self.update_status_label(session_id, start_time))


    def on_tree_select(self, event) -> None:
        """
        Event handler for selecting a session in the tree
        Args:
            event: event - Event object
        """
        selected_item = self.tree.selection()
        if selected_item:
            session_id = int(self.tree.item(selected_item[0], "values")[0])
            self.export_confirmation(session_id)


    def export_confirmation(self, session_id: int) -> None:
        """
        Ask the user if they want to export the output
        Args:
            session_id: int - ID of the session
        """
        response = messagebox.askyesno("Export Confirmation", f"Do you want to export the output for Session {session_id}?")
        if response:
            self.export_excel(session_id)


    def export_excel(self, session_id: int) -> None:
        """
        Export the output to an Excel file
        Args:
            session_id: int - ID of the session
        """
        if "output_workbook" in self.sessions[session_id]:
            output_workbook = self.sessions[session_id]["output_workbook"]
            output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if output_path:
                try:
                    output_workbook.to_excel(output_path, index=False)
                    self.sessions[session_id]["status_label"].config(text="Exported")
                except Exception as e:
                    print("An error occurred while exporting:", e)
        else:
            print("No data to export.")
            messagebox.showerror("Error", "No data to export.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DropboxUploader(root)
    root.mainloop()