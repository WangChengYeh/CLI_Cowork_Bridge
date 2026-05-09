import os
import sys
import subprocess
from pathlib import Path

# Add lib to sys.path
sys.path.append(str(Path.cwd() / 'lib'))

from runtime_pid_cleanup.procfs import read_proc_cmdline, read_proc_path

def test_macos_procfs():
    if sys.platform != 'darwin':
        print("This test is intended for macOS (Darwin).")
        return

    marker = "/tmp/ccb_procfs_test"
    dummy_proc = subprocess.Popen(['python3', '-c', 'import time; time.sleep(100)', marker], cwd="/tmp")
    pid = dummy_proc.pid
    
    try:
        print(f"Started dummy process with PID {pid}")
        
        cmdline = read_proc_cmdline(pid)
        print(f"Read cmdline: {cmdline}")
        if marker in cmdline:
            print("SUCCESS: read_proc_cmdline found the marker.")
        else:
            print("FAILURE: read_proc_cmdline did NOT find the marker.")
            
        cwd = read_proc_path(pid, 'cwd')
        print(f"Read cwd: {cwd}")
        if cwd and str(cwd).startswith('/private/tmp') or str(cwd) == '/tmp':
             print("SUCCESS: read_proc_path found the cwd.")
        else:
             print("FAILURE: read_proc_path did NOT find the expected cwd.")
             
    finally:
        dummy_proc.terminate()
        dummy_proc.wait()

if __name__ == "__main__":
    test_macos_procfs()
