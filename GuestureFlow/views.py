
import subprocess
import os
import time
from django.shortcuts import render
from django.http import HttpResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):
    return render(request, 'index.html')

def run_script(request):
    if request.method == 'POST':
        script_to_run = request.POST.get('script')
        
        # Define the mapping between script identifiers and their paths
        script_paths = {
            'script1': os.path.join(BASE_DIR, 'pyscript', 'volume.py'),
            'script2': os.path.join(BASE_DIR, 'pyscript', 'laptopcontrol.py'),
            'script3': os.path.join(BASE_DIR, 'pyscript', 'DrawOnScreen.py'),
            'script4': os.path.join(BASE_DIR, 'pyscript', 'gesture_VidGame-master', 'camera.py'),
            'script5': os.path.join(BASE_DIR, 'pyscript', 'gesture_VidGame-master', 'main.py'),
            'script6': os.path.join(BASE_DIR, 'pyscript', 'virtual_keyboard.py'),
            'script7': os.path.join(BASE_DIR, 'pyscript', 'gym.py'),
            'script8': os.path.join(BASE_DIR, 'pyscript', 'brightness_controller_main.py'),
            'script9': os.path.join(BASE_DIR, 'pyscript', 'eye_controller.py'),
            'script4_script5_combo': [
                os.path.join(BASE_DIR, 'pyscript', 'gesture_VidGame-master', 'camera.py'),
                os.path.join(BASE_DIR, 'pyscript', 'gesture_VidGame-master', 'main.py')
            ],
        }
        
        # Log the received script identifier for debugging
        print(f"Received script to run: {script_to_run}")

        # Get the path to the selected script(s)
        script_path = script_paths.get(script_to_run)
        
        if script_path:
            try:
                output = ""
                if script_to_run == 'script4_script5_combo':
                    # Start camera.py first as a background process
                    process1 = subprocess.Popen(['python', script_path[0]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(5)  # Wait for camera.py to initialize

                    # Check if camera.py process is still running
                    if process1.poll() is None:
                        # camera.py is running, now start main.py
                        process2 = subprocess.Popen(['python', script_path[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout2, stderr2 = process2.communicate()

                        output += f"Output from main.py:\n{stdout2.decode('utf-8')}"
                        if stderr2:
                            output += f"\nErrors/Warnings from main.py:\n{stderr2.decode('utf-8')}"
                    else:
                        output += "\n\nCamera failed to start. main.py will not be executed."
                else:
                    process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    output = filter_output(stdout.decode('utf-8'))
                    if stderr:
                        output += "\nErrors/Warnings:\n" + filter_output(stderr.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                output = f"Error: {e}"
        else:
            output = "Invalid script selection or script file not found."

        return render(request, 'script_result.html', {'output': output})

    return HttpResponse("Only POST method is allowed")

def filter_output(output):
    # Filter out common library logs and warnings
    lines = output.splitlines()
    filtered_lines = [line for line in lines if not (
        line.startswith('INFO:') or
        line.startswith('WARNING:') or
        'UserWarning:' in line or
        'DeprecationWarning:' in line
    )]
    return '\n'.join(filtered_lines)

