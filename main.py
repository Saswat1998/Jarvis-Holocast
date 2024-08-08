import subprocess

# Start the hand gesture detection script
gesture_process = subprocess.Popen(['python', 'hand_gesture.py'])

# Start the holocast interface script
interface_process = subprocess.Popen(['python', 'holocast_interface.py'])

# Wait for both scripts to complete
gesture_process.wait()
interface_process.wait()
