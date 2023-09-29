# Important Notes:

# To try the app kindly go to 'app.py' file and run it.

# Don't forget to install the missing modules on your PC/Laptop.
# The values were correct when measuring VSCode app consumption and usage.

# # OpenHardwareMonitor app is an ESSENTIAL app to get cpu temperature and gpu wattage usage, you can run the app without it.
# # Failed to get GPU usage for a specific app due to bad GPU driver or other missing issues.

# You are going to see GPU power consumption is ~28 Watts with 0% GPU usage,
# that's real because  the GPU won't be off if you are not using it, it will be on idle mode waiting for apps to use it.

# Sorry for all these NOTES :)

import psutil
import time
import subprocess
import os
import wmi
import cpuinfo
import GPUtil

# CPU:

def get_cpu_power_consumption_and_usage(app_name):
    total_cpu_percent = 0.0
    num_processes = 0

    # Sample CPU usage for 2 seconds
    for _ in range(2):
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            if proc.info['name'].lower() == app_name.lower():
                total_cpu_percent += proc.info['cpu_percent']
                num_processes += 1
        time.sleep(0.4)
    if num_processes > 0:
        avg_cpu_percent = total_cpu_percent / num_processes
        # IMPORTANT Note:
        # The average voltage used between CPUs is 1.2 volt, if the CPU is so powerful it may use 1.4~1.6v

        # get the average CPU TDP (Which is the power of the CPU) by multiplying CPU maximum frequency by 1.4v dividing them by 100 to get the watt.
        average_cpu_tdp = psutil.cpu_freq().max * 1.4 / 100

        # Get the CPU power consumption by multiplying the average CPU percentage usage by CPU TDP dividing it by 100.
        power_consumption = avg_cpu_percent * average_cpu_tdp / 100

        # Round the numbers, for not getting so many numbers for each value.
        return round(power_consumption, 2), round(avg_cpu_percent, 2)
    
    return None

def get_cpu_temp():
    try:
        # Connect to the Open Hardware Monitor namespace in order to get the CPU temperature.
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        for sensor in temperature_infos:
            if sensor.SensorType == "Temperature" and sensor.Name == "CPU Package":
                return sensor.Value
    except Exception as e:
        print(f"Error retrieving CPU temperature: {str(e)}")

    # Return None if the CPU temperature is not found.
    return None

def get_cpu_name():
    cpu_info = cpuinfo.get_cpu_info()
    cpu_name = cpu_info['brand_raw']
    return cpu_name


# GPU:

def get_gpu_power_consumption():
    # Connect to the Open Hardware Monitor namespace
    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")

    # Query the GPU power consumption.
    query = f"SELECT Value FROM Sensor WHERE SensorType='Power' AND Name LIKE 'GPU Power'"
    sensors = w.query(query)

    # Extract the power consumption value from the query result.
    if sensors:
        return round(sensors[0].Value,2)

    # Return None if the GPU power consumption is not found.
    return None

def get_app_gpu_utilization(process_name):

    # Use cmd commands in order to get processes ids, memory usage from the GPU and names.
    app_command = "nvidia-smi --query-compute-apps=pid,used_gpu_memory,process_name --format=csv,noheader"
    # Use cmd commands in order to get GPU usage.
    gpu_command = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader"
    # In this part there are unused lines of code in the app,
    # but it is possible to use it and get the MiB usage of the GPU memory for each running app.
    try:
        app_output = subprocess.check_output(app_command, shell=True, stderr=subprocess.STDOUT)
        gpu_output = subprocess.check_output(gpu_command, shell=True, stderr=subprocess.STDOUT)

        app_output_lines = app_output.decode().strip().split('\n')
        gpu_output_lines = gpu_output.decode().strip().split('\n')

        app_utilization = []
        for line in app_output_lines:
            values = line.split(',')
            if len(values) < 3:
                continue  # Skip lines without enough values, which are: pid,used_gpu_memory,process_name.
            pid = int(values[0])
            memory_usage = values[1]
            app_name = values[2].strip()
            name = os.path.basename(app_name)
            if process_name.lower() in app_name.lower():
                app_utilization.append({'pid': pid, 'memory_usage': memory_usage, 'app_name': name})

        gpu_utilization = [int(x.rstrip('%')) for x in gpu_output_lines]

        return app_utilization, gpu_utilization
    except subprocess.CalledProcessError as e:
        print("Error executing nvidia-smi command:", e.output)
    except Exception as e:
        print("An error occurred:", str(e))

# Unused function:

# # #
def get_gpu_full_memory():
    # Get the GPU full memory using the nvidia-smi command.

    # Run the nvidia-smi command.
    gpu_memory = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total', '--format=csv'])

    # Parse the output of the command
    gpu_memory = gpu_memory.decode('utf-8').split('\n')[1:]
  
    # Get the full memory in MiB
    # gpu_memory_mib = [int(gpu_memory_line.split(',')[0].replace(' MiB', '')) for gpu_memory_line in gpu_memory]

    return int(gpu_memory[0].replace(' MiB', ''))
# # #

def get_gpu_temperature():
    # Run the nvidia-smi command.
    command = 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'
    result = subprocess.run(command, capture_output=True, text=True)
    temperature = result.stdout.strip()
    return temperature

def get_gpu_info():
    # Get GPU information.
    # We used only the name in our application,
    # but we can use more if needed especially GPU temperature if your gpu is not nvidia.
    gpus = GPUtil.getGPUs()
    gpu_info = []

    for gpu in gpus:
        gpu_info.append({
            "ID": gpu.id,
            "Name": gpu.name,
            "Memory": f"{gpu.memoryUsed}MB / {gpu.memoryTotal}MB",
            "Temperature": f"{gpu.temperature} °C"
        })

    return gpu_info
