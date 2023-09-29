# Important Notes:

# # OpenHardwareMonitor app is an ESSENTIAL app to get cpu temperature and gpu wattage usage, you can run the app without it.
# # Failed to get GPU usage for a specific app due to bad GPU driver or other missing issues.

# CPU details are for a specific app you choose, GPU details are for the whole pc.

# My laptop specifications are AMD CPU and RTX GPU, all the GPU's functions work well with nvidia cards, mac needs other cmd commands.

# Every measure should take approximately 4s.
# To make it less time but less accurate you can decrease the sample CPU usage for 1s
# and the time.sleep() in the get_cpu_power_consumption_and_usage function in 'main.py'.

# Default app choosen is 'code.exe' which is VSCode app, you can change it by changing the default current_app value.

import main
import tkinter as tk
import threading
import psutil

# Create a 1280x720 window.
root = tk.Tk()
root.geometry("1280x720")

# Create two columns one is for the CPU and the other one is for the GPU.
# Make the borders solid black and thick.
column1 = tk.Frame(root, borderwidth=4, relief=tk.SOLID,highlightbackground="black")
column2 = tk.Frame(root, borderwidth=4, relief=tk.SOLID,highlightbackground="black")

# column1 get the left side and column2 get the right side.
column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
column2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# CPU column
label000 = tk.Label(column1, text="CPU Specs", fg="black")
label000.config(font=("Arial", 14, "bold"))
label000.config(text=main.get_cpu_name())
label000.pack(pady=5,padx=5)

label00 = tk.Label(column1, text="CPU STATUS FOR THE APP: ", fg="black")
label00.config(font=("Arial", 13, "bold"))
label00.pack(pady=10)

label1 = tk.Label(column1, text="CPU Power Consumption", fg="black")
label1.config(font=("Arial", 12, "bold"))
label1.pack(pady=5)

label2 = tk.Label(column1, text="CPU Usage", fg="black")
label2.config(font=("Arial", 12, "bold"))
label2.pack(pady=5)

label3 = tk.Label(column1, text="CPU Temperature", fg="red")
label3.config(font=("Arial", 12, "bold"))
label3.pack(pady=5)


# GPU column
label010 = tk.Label(column2, text="CPU Specs", fg="black")
label010.config(font=("Arial", 14, "bold"))
label010.config(text=main.get_gpu_info()[0]["Name"])
label010.pack(pady=5)

label01 = tk.Label(column2, text="GPU STATUS FOR PC/LAPTOP:", fg="black")
label01.config(font=("Arial", 13, "bold"))
label01.pack(pady=10)

label4 = tk.Label(column2, text="GPU Power Consumption", fg="black")
label4.config(font=("Arial", 12, "bold"))
label4.pack(pady=5)

label5 = tk.Label(column2, text="GPU Usage", fg="black")
label5.config(font=("Arial", 12, "bold"))
label5.pack(pady=5)

label6 = tk.Label(column2, text="GPU Temperature", fg="red")
label6.config(font=("Arial", 12, "bold"))
label6.pack(pady=5)

def update_cpu_gpu_values():
    global current_app

    # To lower case in order to avoid mismatching.
    current_app = current_app.lower()

    # Get the CPU power and percent usage from the main file, for the current app.
    cpu_power_and_usage = main.get_cpu_power_consumption_and_usage(current_app)
    cpu_power_consumption = cpu_power_and_usage[0]
    label1.config(text="CPU power consumption: "+str(cpu_power_consumption)+" Watts")
    cpu_usage = cpu_power_and_usage[1]
    label2.config(text="CPU usage: "+str(cpu_usage)+"%")
    
    # Get the CPU temperature.
    temp = main.get_cpu_temp()
    label3.config(text="CPU Temperature: "+str(temp)+" C")

    # Get the GPU utilization.
    gpu_usage = main.get_app_gpu_utilization(current_app)[1][0]
    label5.config(text="GPU Usage: "+str(gpu_usage)+"%")

    # Get the GPU temperature.
    temperature = main.get_gpu_temperature()
    label6.config(text="GPU Temperature: "+str(temperature)+" C")
    # Repeat 'update_cpu_values' every 100 milliseconds.
    root.after(100, update_cpu_gpu_values)

def update_gpu_values():
    # Get GPU power consumption for the whole pc/laptop.
    gpu_power = main.get_gpu_power_consumption()
    label4.config(text="GPU power consumption: "+str(gpu_power)+" Watts")
    # Repeat every 100 milliseconds.
    root.after(100, update_gpu_values)

def start_update_threads():
    drop_down_list.pack()
    # Using threads to make the app implementing faster for update_cpu_gpu_values function.
    cpu_thread = threading.Thread(target=update_cpu_gpu_values)
    cpu_thread.daemon = True
    cpu_thread.start()
    # 
    update_gpu_values()


# Create a drop-down list to choose the app.

# Create a frame to hold the drop-down list
frame = tk.Frame(root)
frame.pack()

# Create a drop-down list
drop_down_list = tk.Listbox(frame)
drop_down_list.pack()

# Create a dictionary to store the apps that have already been added to the drop-down list
apps_added = {}

# Populate the drop-down list with the names of all the running apps
for app in psutil.process_iter():
    if app.name() not in apps_added:
        drop_down_list.insert(tk.END, app.name())
        apps_added[app.name()] = True

# Create a label to display the current app
label = tk.Label(frame, text="Current App:")
label.pack()

# Create a variable to store the current app
current_app = "code.exe"

# Callback function for the drop-down list
def select_app(event):
    global current_app
    current_app = drop_down_list.get(drop_down_list.curselection())
    label.config(text="Current App: "+current_app)

app_name=current_app.lower()

# Bind the drop-down list's select event to the callback function
drop_down_list.bind("<<ListboxSelect>>", select_app)


# Start the main job.
start_update_threads()

root.mainloop()