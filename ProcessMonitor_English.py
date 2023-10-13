# Name Software: Process Monitor
# Author: Bocaletto Luca
# License: GPLv3
# Import necessary libraries
import tkinter as tk  # For GUI
from tkinter import ttk
import psutil  # For getting process information
import subprocess  # For starting new processes

# Declaration of global variables
column_sorting = 'name'  # Initial sorting column
ascending_order = True  # Initial order is ascending
columns_to_display = ["PID", "Name", "CPU", "Memory", "Status", "User", "Start Time", "Priority", "Parent PID", "Working Directory", "Memory Usage"]
selected_columns = {}  # Dictionary to keep track of selected columns

# Function to display processes
def display_processes(filter=""):
    # Get a list of process objects with specific attributes
    processes = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'username', 'create_time', 'nice', 'ppid', 'cwd', 'memory_percent']))

    # Clear processes from the display
    for row in process_list.get_children():
        process_list.delete(row)

    # Function to get the value of a column for a process
    def get_value(process, column):
        value = process.info.get(column)
        return value if value is not None else ""

    # Function to get 'nice' as an integer
    def get_nice_as_int(process):
        nice = process.info.get('nice')
        return int(nice) if nice is not None else 0

    # Sort processes based on the sorting column and order
    sorted_processes = sorted(processes, key=lambda p: get_nice_as_int(p) if column_sorting == 'nice' else get_value(p, column_sorting))
    if not ascending_order:
        sorted_processes.reverse()

    # Add processes to the list
    for process in sorted_processes:
        pid = process.info['pid']
        name = process.info['name']
        cpu_percent = process.info['cpu_percent']
        memory = process.info['memory_info'].rss / (1024 * 1024)  # Convert to MB
        status = process.info['status']
        user = get_value(process, 'username')
        create_time = process.info['create_time']
        nice = process.info['nice']
        parent_pid = process.info['ppid']
        working_directory = get_value(process, 'cwd')
        memory_percent = process.info['memory_percent']

        # Filter processes based on the entered filter and add them to the display
        if filter.lower() in name.lower():
            process_list.insert('', 'end', values=(pid, name, f"{cpu_percent:.2f}%", f"{memory:.2f} MB", status, user, create_time, nice, parent_pid, working_directory, f"{memory_percent:.2f}%"))

# Function to change column sorting
def change_sorting(column):
    global ascending_order, column_sorting
    if column == column_sorting:
        ascending_order = not ascending_order
    else:
        column_sorting = column
        ascending_order = True
    display_processes(search_field.get())

# Function to terminate a process
def terminate_process():
    selected = process_list.selection()
    if selected:
        pid = int(process_list.item(selected, 'values')[0])
        try:
            # Get the process object and terminate the process
            process_to_terminate = psutil.Process(pid)
            process_to_terminate.terminate()
            display_processes()  # Update the display
        except psutil.NoSuchProcess:
            pass

# Function to start a new process
def start_process():
    process_to_start = start_field.get()
    try:
        # Start the new process
        subprocess.Popen(process_to_start, shell=True)
        start_field.delete(0, tk.END)  # Clear the start field
    except Exception as e:
        tk.messagebox.showerror("Error", f"Unable to start the process:\n{str(e)}")  # Show an error message

# Function to display selected columns
def show_selected_columns():
    global columns_to_display
    columns_to_display = [col for col, var in selected_columns.items() if var.get() == 1]
    process_list.config(columns=columns_to_display)  # Configure the displayed columns

    for col in columns_to_display:
        process_list.heading(col, text=col)
    
    display_processes(search_field.get())  # Update the display

# Function to open the options window
def open_options_window():
    options_window = tk.Toplevel(root)
    options_window.title("Options")

    columns_frame = tk.Frame(options_window)
    columns_frame.grid(row=0, column=0, rowspan=4, pady=5, padx=10)
    tk.Label(columns_frame, text="Columns to Display:").grid(row=0, column=0, columnspan=2)

    for i, col in enumerate(columns_to_display):
        var = tk.IntVar()
        if col in columns_to_display:
            var.set(1)
        selected_columns[col] = var
        tk.Checkbutton(columns_frame, text=col, variable=var).grid(row=i + 1, column=0, columnspan=2, sticky="w")

    confirm_columns_button = tk.Button(columns_frame, text="Confirm", command=show_selected_columns)
    confirm_columns_button.grid(row=i + 2, column=0, columnspan=2)

# Create the main window
root = tk.Tk()
root.title("Process Monitor")  # Set the title

title_label = tk.Label(root, text="Process Monitor")
title_label.grid(row=0, column=0, columnspan=5, sticky="w")  # Add a title

search_field = tk.Entry(root, width=20)
search_field.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="we")  # Search field

process_list = ttk.Treeview(root, columns=columns_to_display, show="headings")
process_list.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky="news")  # Process display

vertical_scrollbar = ttk.Scrollbar(root, orient="vertical", command=process_list.yview)
vertical_scrollbar.grid(row=2, column=5, sticky="ns")
process_list.configure(yscrollcommand=vertical_scrollbar.set)  # Vertical scrollbar

horizontal_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=process_list.xview)
horizontal_scrollbar.grid(row=3, column=0, columnspan=5, sticky="ew")
process_list.configure(xscrollcommand=horizontal_scrollbar.set)  # Horizontal scrollbar

for col in columns_to_display:
    process_list.heading(col, text=col, command=lambda c=col: change_sorting(c))
    process_list.column(col, width=50, minwidth=50, anchor="center")  # Column headings and widths

action_frame = tk.Frame(root)
action_frame.grid(row=4, column=0, columnspan=5, pady=10, sticky="w")  # Frame for actions

start_field = tk.Entry(action_frame, width=20)
start_field.grid(row=0, column=0, padx=5, sticky="w")  # Field to start new processes

start_button = tk.Button(action_frame, text="Start", command=start_process)
start_button.grid(row=0, column=1, padx=5, sticky="w")  # Button to start a new process

terminate_button = tk.Button(action_frame, text="Terminate Process", command=terminate_process)
terminate_button.grid(row=0, column=2, padx=5, sticky="w")  # Button to terminate a process

update_button = tk.Button(action_frame, text="Update", command=lambda: display_processes(search_field.get()))
update_button.grid(row=0, column=3, padx=5, sticky="w")  # Button to update the process display

options_button = tk.Button(action_frame, text="Options", command=open_options_window)
options_button.grid(row=0, column=4, padx=5, sticky="w")  # Button to open the options window

root.grid_rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

display_processes()  # Show processes on startup

root.mainloop()  # Start the application
