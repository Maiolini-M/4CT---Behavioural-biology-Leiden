# -*- coding: utf-8 -*-
"""
Created on Fri May  3 14:12:03 2024

@author: marco
"""

##IMPORT PYTHON FUNCTIONS
import tkinter as tk
from tkinter import ttk
from tkinter import Scrollbar
from datetime import datetime
from tkinter import filedialog, simpledialog #scrolledtext
from tkinter import messagebox
import os
import pygame
import serial.tools.list_ports   #ARDUINO
import webbrowser

ser = None

# Function to initialize the serial port
def initialize_serial(port, baud_rate):
    global ser
    try:
        ser = serial.Serial(port, baud_rate)
        print(f"Serial communication initialized on port {port} with baud rate {baud_rate}")
    except serial.SerialException as e:
        print(f"Failed to initialize serial communication: {e}")

# Function to handle serial port selection
def handle_serial_selection(port, baud_rate):
    if baud_rate:
        initialize_serial(port, baud_rate)
    else:
        print("Please select a baud rate.")
     
 # Function to handle serial port selection
def handle_baud_rate_selection(baud_rate, port):
    if port:
        initialize_serial(port, baud_rate)
    else:
        print("Please select a port.")
         
# Function to exit the program
def exit_program():
    if ser is not None:
        ser.close()  # Close the serial port before exiting if it's open
    root.destroy()

#---------------------------------------------------
#Window name
root = tk.Tk()
root.title("4CT")
root.geometry("1800x900")
root.resizable(width=False, height=False)
    
###Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

#Get the serial ports
available_ports = [port.device for port in serial.tools.list_ports.comports()]

# Add a submenu for port selection
port_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Select Port", menu=port_menu)
for port in available_ports:
    port_menu.add_command(label=port, command=lambda p=port: handle_serial_selection(p))
  
# Populate the baud rates
baud_rates = ["9600", "115200"]

# Add a submenu for baud rate selection
baud_rate_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Select Baud Rate", menu=baud_rate_menu)
for baud_rate in baud_rates:
    baud_rate_menu.add_command(label=baud_rate, command=lambda br=baud_rate: handle_baud_rate_selection(br))

#Window to select the shortcuts
def open_shortcut_selection_window():
    # Create a new window
    shortcut_window = tk.Toplevel(root)
    shortcut_window.title("Keyboard Shortcut Selection")

    # Add widgets for selecting keyboard shortcuts
    shortcut_label = tk.Label(shortcut_window, text="Select Keyboard Shortcut:")
    shortcut_label.pack()

    # Add an entry field for the keyboard shortcut
    shortcut_entry = tk.Entry(shortcut_window)
    shortcut_entry.pack()

    # Add buttons for saving or canceling the selection
    save_button = tk.Button(shortcut_window, text="Save")
    save_button.pack()

    cancel_button = tk.Button(shortcut_window, text="Cancel", command=shortcut_window.destroy)
    cancel_button.pack()
    
file_menu.add_command(label="Select Shortcut", command=open_shortcut_selection_window)

file_menu.add_separator()

file_menu.add_command(label="Exit", command=exit_program)

##HELP TAB
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
guideline_menu = tk.Menu(help_menu, tearoff=0)

def open_4CT_documentation():
    webbrowser.open("https://github.com/Maiolini-M/4CT---Behavioural-biology-Leiden/tree/main/Guideline")

help_menu.add_cascade(label="Guidelines", menu=guideline_menu)
guideline_menu.add_command(label="4CT Documentation", command=open_4CT_documentation)

#------------------------------------------------------------------------------
#Store the log entries and action count
log_data = []
action_count = 0
selected_files_dict = {"SongA": [], "SongB": [], "SongC": [], "SongD": []}
start_time_first_timer = None
stop_first_timer_flag = False
start_time_second_timer = None
stop_second_timer_flag = False

#------------------------------------------------------------------------------
#Design the log of action
def log_action(action, selected_option):
    global action_count
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]
    action_count += 1
    n_experiment = experiment_name.get()
    if selected_option == "Other":
        custom_value = other1_entry.get()
        log_entry = f"{action_count}_{n_experiment}_{custom_value}_{current_time}_{action}"
    else:
        log_entry = f"{action_count}_{n_experiment}_{selected_option}_{current_time}_{action}"
    log_data.append(log_entry)
    log_text.insert(tk.END, log_entry + "\n")
    log_text.see(tk.END)

# Export the log as txt
def export_to_txt():
    #Define the export folder
    export_folder = filedialog.askdirectory(title="Select the Folder where you would like to export")
    if not export_folder:
        return
    # Ask the user for the desired file name
    file_name = simpledialog.askstring("File Name", "Enter the desired file name:")
    if file_name is None:
        return
    file_path = os.path.join(export_folder, f"{file_name}.txt")
    try:
        with open(file_path, "w") as file:
            for log_entry in log_data:
                file.write(log_entry + "\n")
            
            messagebox.showinfo("Export Successful", f"File exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred during export: {e}")

#Define the export to csv
def export_to_csv():
    export_folder = filedialog.askdirectory(title="Select the Folder where you would like to export")
    if not export_folder:
        return
    # Ask the user for the desired file name
    file_name = simpledialog.askstring("File Name", "Enter the desired file name:")
    if file_name is None:
        return
    file_path = os.path.join(export_folder, f"{file_name}.csv")
    try:
        with open(file_path, "w", newline="") as file:
            for log_entry in log_data:
                file.write(log_entry + "\n")
            
            messagebox.showinfo("Export Successful", f"File exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred during export: {e}")

# Clear the log
def clear_log():
    log_text.delete("1.0", tk.END) #Clear the log.text
    log_data.clear()
#------------------------------------------------------------------------------
#SET THE TIME SCALES
def create_time_values():
    time_values = []
    for hour in range(24):
        for minute in range(60):
            for second in range(60):
                time_values.append(f"{hour:02d}:{minute:02d}:{second:02d}")
    return time_values

#Function for timing with milliseconds
def milliseconds_time_values():
    second_values = []
    for second in range(60):
        for millisecond in range(1000):
                second_values.append(f"{second:02d}.{millisecond:03d}")
    return second_values
#------------------------------------------------------------------------------
#Handle the species selection
def handle_species_choice():
    selected_option = species_var.get()
    if selected_option == "Other":
        other1_entry.config(state="normal")  # Enable input for "Other"
    else:
        other1_entry.delete(0, tk.END)  # Clear the "Other" entry field
        other1_entry.config(state="readonly")  # Disable input for other options
#------------------------------------------------------------------------------
#SONG FRAME Functions
# Dictionary to store selected files for each sensor:
selected_files_dict = {"SongA": [], "SongB": [], "SongC": [], "SongD": []}

def update_selected_files_textbox(song_name, selected_files_textbox):
    selected_files = selected_files_dict[song_name]
    text_content = "; ".join(selected_files) if selected_files else "None"
    selected_files_textbox.configure(state=tk.NORMAL)
    selected_files_textbox.delete("1.0", tk.END)  # Clear previous content
    selected_files_textbox.insert(tk.END, f"{text_content}")
    selected_files_textbox.configure(state=tk.DISABLED)

def select_audio_files(song_name):
    error_occurred = False
    file_paths = filedialog.askopenfilenames(
        filetypes=[("Audio Files", "*.wav;*.mp3")],
        title=f"Select audio files for {song_name}",
    )

    selected_files = list(file_paths)  # Store full file paths
 #   selected_files = [os.path.splitext(os.path.basename(file_path))[0] for file_path in file_paths]
    
    if len(selected_files) > 0:
            for other_song in selected_files_dict:
                if other_song != song_name and set(selected_files) & set(selected_files_dict[other_song]):
                    messagebox.showerror("File Selection Error", f"Files in {song_name} should be different from files selected in {other_song}.")
                    error_occurred = True
                    break
    
            if not error_occurred:
                selected_files_dict[song_name] = selected_files
                update_selected_files_textbox(song_name, selected_file_labels[song_name])
                # Log each selected audio file
                for file_name in selected_files:
                    log_action(f"Selected audio file for {song_name}: {os.path.basename(file_name)}", species_var.get())
    else:
            # Clear the label text
            selected_file_labels[song_name].configure(state=tk.NORMAL)
            selected_file_labels[song_name].delete("1.0", tk.END)
            selected_file_labels[song_name].insert(tk.END, "Selected file: None")
            selected_file_labels[song_name].configure(state=tk.DISABLED)

def play_sounds(song_name, selected_files):
    pygame.mixer.init()
    if selected_files:
        for file_path in selected_files:
            if os.path.exists(file_path):
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                log_action(f"{song_name} played this file: {os.path.basename(file_path)}", species_var.get())
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                log_action(f"File not found: {file_path}", species_var.get())
    else:
        log_action(f"No sound selected for {song_name}", species_var.get())
#------------------------------------------------------------------------------
#Experimental details

# def change_songs():

    

def check_start_time(switch_button, start_time):
    if switch_button.get() == 1:
        overall_time = start_time_var.get()
        if overall_time == start_time.get():
            print("Record ready to start")
        else:
            messagebox.showerror("Time error","Starting time of the first switch does not match the overall starting time")
    else:
        print("Checkbutton error, Time is correct but the chechbutton is unchecked")

def check_end_time(switch_button, end_time):
    if switch_button.get() == 1:
        overall_time = end_time_var.get()
        if overall_time == end_time.get():
            #Count the microswitch
            print("Record ready to start")
        else:
            messagebox.showerror("Time error","Ending time of the last switch does not match the overall ending time")
    else:
        print("Checkbutton error, Time is correct but the chechbutton is unchecked")

def check_only_one_checkbutton(selected_button, conflicting_button1, conflicting_button2, conflicting_button3,
                               conflicting_button4, conflicting_button5):
    if selected_button.instate(['selected']):
        conflicting_button1.state(['disabled'])
        conflicting_button2.state(['disabled'])
        conflicting_button3.state(['disabled'])
        conflicting_button4.state(['disabled'])
        conflicting_button5.state(['disabled'])
    else:
        conflicting_button1.state(['!disabled'])
        conflicting_button2.state(['!disabled'])
        conflicting_button3.state(['!disabled'])
        conflicting_button4.state(['!disabled'])
        conflicting_button5.state(['!disabled'])
#------------------------------------------------------------------------------
# Timer Function
def start_timer():
    global start_time, stop_timer_flag
    stop_timer_flag = False
    start_time = datetime.now()

def stop_timer():
    global stop_timer_flag
    stop_timer_flag = True
            
# Function of the datetime
def update_datetime_label():
    current_datetime = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    datetime_label.config(text=current_datetime)
    first_frame.after(1000, update_datetime_label)

#LOG FUNCTION
def log_variable_state():
    current_datetime = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
       
    # Get the selected files for each sensor
    files_songA = selected_files_dict.get("SongA", [])
    files_songB = selected_files_dict.get("SongB", [])
    files_songC = selected_files_dict.get("SongC", [])
    files_songD = selected_files_dict.get("SongD", [])
    
    log_entry = (f"{current_datetime}\nExperiment name: {experiment_name.get()}\nSpecies tested: {species_var.get()}\nStarting position: {start_var.get()}\
                \nPerch timeout(s): {button_delay.get()}\
                \nThe files selected for Song A are: {', '.join(files_songA)}\nThe files selected for Song C are: {', '.join(files_songB)}\
                \nThe files selected for Song C are: {', '.join(files_songC)}\nThe files selected for Song D are: {', '.join(files_songD)}\
                \nStart time setted for {start_time_spinbox.get()} & End time setted for {end_time_spinbox.get()}")
    log_data.append(log_entry)
    log_text.insert(tk.END, log_entry + "\n")
    log_text.see(tk.END)

#Variable of timing
Save_at_state = tk.BooleanVar(value=True) #Initially ON
#Switch_state
first_switch_state1 = tk.BooleanVar(value=False) #Initially OFF
first_switch_state2 = tk.BooleanVar(value=False) #Initially OFF
first_switch_state3 = tk.BooleanVar(value=False) #Initially OFF
first_switch_state4 = tk.BooleanVar(value=False) #Initially OFF
first_switch_state5 = tk.BooleanVar(value=False) #Initially OFF
first_switch_state6 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state1 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state2 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state3 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state4 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state5 = tk.BooleanVar(value=False) #Initially OFF
last_switch_state6 = tk.BooleanVar(value=False) #Initially OFF

#-----------------------------------------
#LOG
#Configure the dimensions of the window
root.rowconfigure(0, minsize=800, weight=1)
root.columnconfigure(1, minsize=800, weight=1)

#Set a main frame
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

#Create a side panel for the log
log_frame = ttk.Frame(main_frame, width= 80)
log_frame.pack(side="right", fill="both")

log_label = tk.Label(log_frame, text="Experimental Log", font=("Times New Roman",9,"bold"))
log_label.pack()

# Create horizontal and vertical scrollbars for the log text widget
log_x_scrollbar = Scrollbar(log_frame, orient=tk.HORIZONTAL)
log_x_scrollbar.pack(side="bottom", fill="x")

log_y_scrollbar = Scrollbar(log_frame, orient=tk.VERTICAL)
log_y_scrollbar.pack(side="right", fill="y")

log_text = tk.Text(
    log_frame,
    wrap=tk.NONE,
    xscrollcommand=log_x_scrollbar.set,
    yscrollcommand=log_y_scrollbar.set,
)
log_text.pack(fill="both", expand=True)

# Configure the horizontal scrollbar to control the log text widget
log_x_scrollbar.config(command=log_text.xview)

# Configure the vertical scrollbar to control the log text widget
log_y_scrollbar.config(command=log_text.yview)

#Export button at the end of the log
export_button = tk.Button(log_frame, text="Export as TXT", command=export_to_txt, bg="blue", fg="white", font=("Times New Roman", 12, "bold"))
export_button.pack(side="right", pady=10)

#Export button at the end of the log
export_button2 = tk.Button(log_frame, text="Export as CSV", command=export_to_csv, bg="blue", fg="white", font=("Times New Roman", 12, "bold"))
export_button2.pack(side="right", pady=10)

#Clear the log
clear_log_button = tk.Button(log_frame, text="Clear Log", command=clear_log, bg="red", fg="white", font=("Times New Roman", 12, "bold"))
clear_log_button.pack(side="right", padx=5, pady=10)

notebook = ttk.Notebook(main_frame)
notebook.pack(fill="both", expand=True)

#-----------------------------------------
#FIRST FRAME[0]
first_frame = ttk.Frame(main_frame, width=1138, height=180)
first_frame.place(x=00, y=00)

#Subtitle 1
subtitle_1_label = tk.Label(first_frame, text="Experiment details", font=("Helvetica",12))
subtitle_1_label.place(x=480, y=35, relx=0.01, rely=0.01)

##Experiment name
experiment_label = tk.Label(first_frame, text= "Experiment name", font=("Times New Roman",10))
experiment_label.place(x=75, y=90)
experiment_name = tk.Entry(first_frame, state="normal", width=25)
experiment_name.place(x=180, y=90)

#Timer
datetime_label = ttk.Label(first_frame, text="")
datetime_label.place(x=380, y=90)

#Call the function to update the datetime label
update_datetime_label()

#Delay setting
button_delay_std = tk.StringVar(value= "0.200")
button_delay_label = ttk.Label(first_frame, text="Perch timeout (s)", font=("Times New Roman",10))
button_delay_label.place(x=75, y=140)
button_delay = ttk.Spinbox(first_frame, textvariable=button_delay_std, values= milliseconds_time_values(), width=8)
button_delay.place(x=180, y= 140)

#Species details
species_var = tk.StringVar()
species_var.set("Zebra finch")

#Label Radio frame species [1]
species_label1_tab2 = tk.Label(first_frame, text= "Species", font=("Times New Roman",10))
species_label1_tab2.place(x=580, y=90)
species_option1 = ttk.Radiobutton(first_frame, text="Zebra finch", variable=species_var, value="Zebra finch", command=handle_species_choice)
species_option1.place(x=650, y=90)
species_option2 = ttk.Radiobutton(first_frame, text="Budgerigar", variable=species_var, value="Budgerigar", command=handle_species_choice)
species_option2.place(x=760, y=90)
species_option3 = ttk.Radiobutton(first_frame, text="Other", variable=species_var, value="Other", command=handle_species_choice)
species_option3.place(x=870, y=90)
other1_entry = tk.Entry(first_frame, state="normal")
other1_entry.place(x=950, y=90)

#Switching
start_label = tk.Label(first_frame, text= "Starting position", font=("Times New Roman",10))
start_label.place(x=280, y=140)
start_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
start_combox = ttk.Combobox(first_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=start_var, width=20, state="readonly", justify="center")
start_combox.place(x=400,y=140)

#START AND END OPTIONS
start_time_var =tk.StringVar(value="08:00:00")
start_time_label = tk.Label(first_frame, text="Start time")
start_time_label.place(x=580, y=140)
start_time_spinbox = ttk.Spinbox(first_frame, textvariable=start_time_var, values=create_time_values(), wrap="True", width= 10)
start_time_spinbox.place(x=650, y=140)

end_time_var =tk.StringVar(value="16:00:00")
end_time_label = tk.Label(first_frame, text="End time")
end_time_label.place(x=750, y=140)
end_time_spinbox = ttk.Spinbox(first_frame, textvariable=end_time_var, values=create_time_values(), wrap="True", width= 10)
end_time_spinbox.place(x=820, y=140)

# Create a Checkbutton widget
Save_at = ttk.Checkbutton(first_frame, text="Save at 00:00:00 hour", variable=Save_at_state) #, command=perform_action12)
Save_at.place(x=935, y=140)

#--------------------------------------------------------------
## SONG FRAME [1]
# Frame
song_frame = ttk.Frame(main_frame, width=1138, height=300)
song_frame.place(x=0, y=180)

#Subtitle 2
subtitle_2_label = tk.Label(song_frame, text="Song selection", font=("Helvetica",12))
subtitle_2_label.place(x=495, y=15, relx=0.01, rely=0.01)

# Labels Randomization/Audio selection/Selected Files/Last played audio/Audio played in total/Audio repeated
audio_selection_label = tk.Label(song_frame, text="Audio selection")
audio_selection_label.place(x=135, y=50)
selected_files_label = tk.Label(song_frame, text="Selected files")
selected_files_label.place(x=550, y=50)

#---------------------------------------------------------------------------------------------
# SONG A
# Label
song1_label = tk.Button(song_frame, text="Song A", font=("Times New Roman", 12), command=lambda: play_sounds("SongA", selected_files_dict["SongA"]))
song1_label.place(x=40, y=85)
# Selection and Button
select_file_button1 = ttk.Button(song_frame, text="Select File for Song A", command=lambda: select_audio_files("SongA"))
select_file_button1.place(x=120, y=88)

# Listbox widget for displaying selected files
listbox_x_scrollbar1 = Scrollbar(song_frame, orient=tk.HORIZONTAL)
listbox_x_scrollbar1.place(x=260, y=115)

selected_files_textbox1 = tk.Text(
    song_frame,
    wrap=tk.NONE,
    xscrollcommand=listbox_x_scrollbar1.set,
    height=1,
    width=100,
    state=tk.NORMAL)
selected_files_textbox1.insert(tk.END, "Selected file: None")
selected_files_textbox1.place(x=260, y=90)  # Adjust the y-coordinate as needed

listbox_x_scrollbar1.config(command=selected_files_textbox1.xview)

#---------------------------------------------------------------------------------------------
# SONG B
# Label
song2_label = tk.Button(song_frame, text="Song B", font=("Times New Roman", 12), command=lambda: play_sounds("SongB", selected_files_dict["SongB"]))
song2_label.place(x=40, y=140)
# Selection and Button
select_file_button2 = ttk.Button(song_frame, text="Select File for Song B", command=lambda: select_audio_files("SongB"))
select_file_button2.place(x=120, y=140)

# Listbox widget for displaying selected files
listbox_x_scrollbar2 = Scrollbar(song_frame, orient=tk.HORIZONTAL)
listbox_x_scrollbar2.place(x=260, y=165)

selected_files_textbox2 = tk.Text(
    song_frame,
    wrap=tk.NONE,
    xscrollcommand=listbox_x_scrollbar2.set,
    height=1,
    width=100,
    state=tk.NORMAL)
selected_files_textbox2.insert(tk.END, "Selected file: None")
selected_files_textbox2.place(x=260, y=140)  # Adjust the y-coordinate as needed

listbox_x_scrollbar2.config(command=selected_files_textbox2.xview)

#---------------------------------------------------------------------------------------------
# SONG C
# Label
song3_label = tk.Button(song_frame, text="Song C", font=("Times New Roman", 12), command=lambda: play_sounds("SongC", selected_files_dict["SongC"]))
song3_label.place(x=40, y=190)
# Selection and Button
select_file_button3 = ttk.Button(song_frame, text="Select File for Song C", command=lambda: select_audio_files("SongC"))
select_file_button3.place(x=120, y=190)

# Listbox widget for displaying selected files
listbox_x_scrollbar3 = Scrollbar(song_frame, orient=tk.HORIZONTAL)
listbox_x_scrollbar3.place(x=260, y=215)

selected_files_textbox3 = tk.Text(
    song_frame,
    wrap=tk.NONE,
    xscrollcommand=listbox_x_scrollbar3.set,
    height=1,
    width=100,
    state=tk.NORMAL)
selected_files_textbox3.insert(tk.END, "Selected file: None")
selected_files_textbox3.place(x=260, y=190)  # Adjust the y-coordinate as needed

listbox_x_scrollbar3.config(command=selected_files_textbox3.xview)

#---------------------------------------------------------------------------------------------
# SONG D
# Label
song4_label = tk.Button(song_frame, text="Song D", font=("Times New Roman", 12), command=lambda: play_sounds("SongD", selected_files_dict["SongD"]))
song4_label.place(x=40, y=240)
# Selection and Button
select_file_button4 = ttk.Button(song_frame, text="Select File for Song D", command=lambda: select_audio_files("SongD"))
select_file_button4.place(x=120, y=240)

# Listbox widget for displaying selected files
listbox_x_scrollbar4 = Scrollbar(song_frame, orient=tk.HORIZONTAL)
listbox_x_scrollbar4.place(x=260, y=265)

selected_files_textbox4 = tk.Text(
    song_frame,
    wrap=tk.NONE,
    xscrollcommand=listbox_x_scrollbar4.set,
    height=1,
    width=100,
    state=tk.NORMAL)
selected_files_textbox4.insert(tk.END, "Selected file: None")
selected_files_textbox4.place(x=260, y=240)  # Adjust the y-coordinate as needed

listbox_x_scrollbar4.config(command=selected_files_textbox4.xview)

# Dictionary to check the file selection
selected_file_labels = {
    "SongA": selected_files_textbox1,
    "SongB": selected_files_textbox2,
    "SongC": selected_files_textbox3,
    "SongD": selected_files_textbox4}
#--------------------------------------------------------
#Switch frame
switch_frame = tk.Frame(main_frame, width=1138, height=350)
switch_frame.place(x=00, y=470)

#Subtitle 3
subtitle_3_label = tk.Label(switch_frame, text="Switching", font=("Helvetica",12))
subtitle_3_label.place(x=480, y=15, relx=0.01, rely=0.01)

# Labels Randomization/Audio selection/Selected Files/Last played audio/Audio played in total/Audio repeated
switch_position_label = tk.Label(switch_frame, text="Switch position")
switch_position_label.place(x=350, y=50)
start_time_label = tk.Label(switch_frame, text="Start time")
start_time_label.place(x=490, y=50)
end_time_label = tk.Label(switch_frame, text="End time")
end_time_label.place(x=590, y=50)
first_switch_label = tk.Label(switch_frame, text="First switch")
first_switch_label.place(x=690, y=50)
end_switch_label = tk.Label(switch_frame, text="Last switch")
end_switch_label.place(x=790, y=50)

#---------------------------------------------------------------------------------------------
# First switch
# Label
switch1_label = tk.Label(switch_frame, text="First switch", font=("Times New Roman", 12))
switch1_label.place(x=230, y=90)
# Selection
switch_selection1 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=start_var, width=20, state="readonly", justify="center")
switch_selection1.place(x=320, y=90)

# Start time
start_time1_var = tk.StringVar(value="08:00:00")
start_time1_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time1_var, values=create_time_values(), wrap="True", width= 10)
start_time1_spinbox.place(x=480, y=90)
# End time
end_time1_var = tk.StringVar(value="12:00:00")
end_time1_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time1_var, values=create_time_values(), wrap="True", width= 10)
end_time1_spinbox.place(x=580, y=90)
#First switch button
first_switch_button1 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state1,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button1, first_switch_button5, first_switch_button4,
                                                                                  first_switch_button3, first_switch_button2, first_switch_button6), 
                                                        check_start_time(first_switch_state1, start_time1_var)])
first_switch_button1.place(x=710, y=90)
#End switch button
last_switch_button1 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state1,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button1, last_switch_button2, last_switch_button3,
                                                                                last_switch_button4, last_switch_button5, last_switch_button6),
                                                      check_end_time(last_switch_state1, end_time1_var)])
last_switch_button1.place(x=810, y=90)

#---------------------------------------------------------------------------------------------
# Second switch
# Label
switch2_label = tk.Label(switch_frame, text="2nd switch", font=("Times New Roman", 12))
switch2_label.place(x=230, y=130)
# Selection
switch_selection2_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
switch_selection2 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=switch_selection2_var, width=20, state="readonly", justify="center")
switch_selection2.place(x=320, y=130)

# Start time
start_time2_var = end_time1_var
start_time2_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time2_var, values=create_time_values(), wrap="True", width= 10)
start_time2_spinbox.place(x=480, y=130)
# End time
end_time2_var = tk.StringVar(value="16:00:00")
end_time2_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time2_var, values=create_time_values(), wrap="True", width= 10)
end_time2_spinbox.place(x=580, y=130)
#First switch button
first_switch_button2 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state2,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button2, first_switch_button5, first_switch_button4,
                                                                                  first_switch_button3, first_switch_button6, first_switch_button1),
                                                        check_start_time(first_switch_state2, start_time2_var)])
first_switch_button2.place(x=710, y=130)
#End switch button
last_switch_button2 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state2,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button2, last_switch_button1, last_switch_button3,
                                                                                last_switch_button4, last_switch_button5, last_switch_button6),
                                                      check_end_time(last_switch_state2, end_time2_var)])
last_switch_button2.place(x=810, y=130)

#---------------------------------------------------------------------------------------------
# Third switch
# Label
switch3_label = tk.Label(switch_frame, text="3rd switch", font=("Times New Roman", 12))
switch3_label.place(x=230, y=170)
# Selection
switch_selection3_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
switch_selection3 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=switch_selection3_var, width=20, state="readonly", justify="center")
switch_selection3.place(x=320, y=170)

# Start time
start_time3_var = end_time2_var
start_time3_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time3_var, values=create_time_values(), wrap="True", width= 10)
start_time3_spinbox.place(x=480, y=170)
# End time
end_time3_var = tk.StringVar(value="00:00:00")
end_time3_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time3_var, values=create_time_values(), wrap="True", width= 10)
end_time3_spinbox.place(x=580, y=170)
#First switch button
first_switch_button3 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state3,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button3, first_switch_button5, first_switch_button4,
                                                                                  first_switch_button6, first_switch_button2, first_switch_button1),
                                                        check_start_time(first_switch_state3, start_time3_var)])
first_switch_button3.place(x=710, y=170)
#End switch button
last_switch_button3 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state3,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button3, last_switch_button2, last_switch_button1,
                                                                                last_switch_button4, last_switch_button5, last_switch_button6),
                                                      check_end_time(last_switch_state3, end_time3_var)])
last_switch_button3.place(x=810, y=170)

#---------------------------------------------------------------------------------------------
# Four switch
# Label
switch4_label = tk.Label(switch_frame, text="4th switch", font=("Times New Roman", 12))
switch4_label.place(x=230, y=210)
# Selection
switch_selection4_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
switch_selection4 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=switch_selection4_var, width=20, state="readonly", justify="center")
switch_selection4.place(x=320, y=210)

# Start time
start_time4_var = end_time3_var
start_time4_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time4_var, values=create_time_values(), wrap="True", width= 10)
start_time4_spinbox.place(x=480, y=210)
# End time
end_time4_var = tk.StringVar(value="00:00:00")
end_time4_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time4_var, values=create_time_values(), wrap="True", width= 10)
end_time4_spinbox.place(x=580, y=210)
#First switch button
first_switch_button4 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state4,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button4, first_switch_button5, first_switch_button6,
                                                                                  first_switch_button3, first_switch_button2, first_switch_button1),
                                                        check_start_time(first_switch_state4, start_time4_var)])
first_switch_button4.place(x=710, y=210)
#End switch button
last_switch_button4 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state4,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button4, last_switch_button2, last_switch_button3,
                                                                                last_switch_button1, last_switch_button5, last_switch_button6),
                                                      check_end_time(last_switch_state4, end_time4_var)])
last_switch_button4.place(x=810, y=210)

#---------------------------------------------------------------------------------------------
# Fifth switch
# Label
switch5_label = tk.Label(switch_frame, text="5th switch", font=("Times New Roman", 12))
switch5_label.place(x=230, y=250)
# Selection
switch_selection5_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
switch_selection5 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=switch_selection5_var, width=20, state="readonly", justify="center")
switch_selection5.place(x=320, y=250)

# Start time
start_time5_var = end_time4_var
start_time5_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time5_var, values=create_time_values(), wrap="True", width= 10)
start_time5_spinbox.place(x=480, y=250)
# End time
end_time5_var = tk.StringVar(value="00:00:00")
end_time5_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time5_var, values=create_time_values(), wrap="True", width= 10)
end_time5_spinbox.place(x=580, y=250)
#First switch button
first_switch_button5 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state5,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button5, first_switch_button6, first_switch_button4,
                                                                                  first_switch_button3, first_switch_button2, first_switch_button1),
                                                        check_start_time(first_switch_state5, start_time5_var)])
first_switch_button5.place(x=710, y=250)
#End switch button
last_switch_button5 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state5,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button5, last_switch_button2, last_switch_button3,
                                                                                last_switch_button4, last_switch_button1, last_switch_button6),
                                                      check_end_time(last_switch_state5, end_time5_var)])
last_switch_button5.place(x=810, y=250)

#---------------------------------------------------------------------------------------------
# Sisxth switch
# Label
switch6_label = tk.Label(switch_frame, text="6th switch", font=("Times New Roman", 12))
switch6_label.place(x=230, y=290)
# Selection
switch_selection6_var = tk.StringVar(value="A-1, B-2, C-3, D-4")
switch_selection6 = ttk.Combobox(switch_frame, values=["A-1, B-2, C-3, D-4", "A-4, B-1, C-2, D-3", "A-3, B-4, C-1, D-2", "A-2, B-3, C-4, D-1",
                                                  "A-2, B-1, C-4, D-3", "A-1, B-4, C-3, D-2", "A-4, B-3, C-2, D-1", "A-3, B-2, C-1, D-4",
                                                  "A-1, B-2, C-4, D-3", "A-4, B-1, C-3, D-2", "A-3, B-4, C-2, D-1", "A-2, B-3, C-1, D-2",
                                                  "A-2, B-1, C-3, D-4", "A-1, B-4, C-2, D-3", "A-4, B-3, C-1, D-2", "A-3, B-2, C-4, D-1"],
                             textvariable=switch_selection6_var, width=20, state="readonly", justify="center")
switch_selection6.place(x=320, y=290)

# Start time
start_time6_var = end_time5_var
start_time6_spinbox = ttk.Spinbox(switch_frame, textvariable=start_time6_var, values=create_time_values(), wrap="True", width= 10)
start_time6_spinbox.place(x=480, y=290)
# End time
end_time6_var = tk.StringVar(value="00:00:00")
end_time6_spinbox = ttk.Spinbox(switch_frame, textvariable=end_time6_var, values=create_time_values(), wrap="True", width= 10)
end_time6_spinbox.place(x=580, y=290)
#First switch button
first_switch_button6 = ttk.Checkbutton(switch_frame, text="", variable=first_switch_state6,
                                       command=lambda: [check_only_one_checkbutton(first_switch_button6, first_switch_button5, first_switch_button4,
                                                                                  first_switch_button3, first_switch_button2, first_switch_button1),
                                                        check_start_time(first_switch_state6, start_time6_var)])
first_switch_button6.place(x=710, y=290)

#End switch button
last_switch_button6 = ttk.Checkbutton(switch_frame, text="", variable=last_switch_state6,
                                     command=lambda: [check_only_one_checkbutton(last_switch_button6, last_switch_button2, last_switch_button3,
                                                                                last_switch_button4, last_switch_button5, last_switch_button1),
                                                      check_end_time(last_switch_state6, end_time6_var)])
last_switch_button6.place(x=810, y=290)
#--------------------------------------------------------
#FINAL FRAME
#Frame
final_frame = tk.Frame(main_frame, width=1138, height=100)
final_frame.place(x=00, y=800)

#START BUTTON
start_button = tk.Button(final_frame, text="START", bg="green", fg="white", font=("Times New Roman", 12, "bold"),
                         command=lambda: [start_timer(), log_variable_state()])
start_button.place(x=960, y=15)

#END BUTTON
end_button = tk.Button(final_frame, text="END", bg="red", fg="white", font=("Times New Roman", 12, "bold"),
                       command=lambda: [stop_timer(), export_to_txt()])
end_button.place(x=1060, y=15)
#------------------------------------------------------------------------------
# Function to close the serial port if it's open
def close_serial_port_if_open():
    global ser
    if ser is not None:
        try:
            ser.close()
        except AttributeError:
            print("Failed to close the serial port.")

# Function to handle window close event
def on_closing():
    close_serial_port_if_open()
    root.destroy()

# Bind the window close event to the on_closing function
root.protocol("WM_DELETE_WINDOW", on_closing)


root.mainloop()

