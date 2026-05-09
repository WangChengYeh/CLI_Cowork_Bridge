import os
import sys
import subprocess
import time
from pathlib import Path

# Add lib to sys.path
sys.path.append(str(Path.cwd() / 'lib'))

from runtime_pid_cleanup.collection import collect_project_process_candidates

def test_macos_collection():
    if sys.platform != 'darwin':
        print("This test is intended for macOS (Darwin).")
        return

    # Use a unique marker that is likely to be found in the command line
    marker = Path.cwd() / ".ccb_test_marker"
    
    # Start a dummy process with this marker in its command line
    # We use 'sleep 100' and append the marker as an argument
    dummy_proc = subprocess.Popen(['sleep', '100', str(marker)])
    pid = dummy_proc.pid
    
    try:
        print(f"Started dummy process with PID {pid} and marker {marker}")
        
        # Test collection. We need a dummy project root.
        # collect_project_process_candidates looks for markers in cmdline.
        # It calls _project_runtime_markers(project_root, ccb_root=ccb_root)
        # which returns (ccb_root, layout.runtime_state_root / 'agents', layout.runtime_state_root / 'ccbd')
        
        # To make it work, we can just pass a project_root that when expanded and appended with .ccb
        # matches our marker. Or we can just mock _project_runtime_markers but let's try to use it as is.
        
        # Actually, let's look at _project_runtime_markers again.
        # def _project_runtime_markers(project_root: Path, *, ccb_root: Path) -> tuple[Path, ...]:
        #    layout = PathLayout(project_root)
        #    markers: list[Path] = [ccb_root]
        #    ...
        
        # ccb_root = project_root.expanduser() / '.ccb'
        # So if we set project_root to (marker.parent), then ccb_root will be (marker.parent / '.ccb')
        # If we start the process with (marker.parent / '.ccb') in its args, it should match.
        
        project_root = marker.parent
        ccb_marker = project_root / '.ccb'
        
        # Restart dummy process with the correct marker
        dummy_proc.terminate()
        dummy_proc.wait()
        
        dummy_proc = subprocess.Popen(['python3', '-c', 'import time; time.sleep(100)', str(ccb_marker)])
        pid = dummy_proc.pid
        print(f"Restarted dummy process with PID {pid} and marker {ccb_marker}")

        candidates = collect_project_process_candidates(project_root)
        
        print(f"Candidates found: {candidates}")
        
        if pid in candidates:
            print(f"SUCCESS: Found PID {pid} in candidates.")
        else:
            print(f"FAILURE: PID {pid} not found in candidates.")
            # Print all candidates for debugging
            for p, m in candidates.items():
                print(f"  PID {p}: {m}")
            
    finally:
        dummy_proc.terminate()
        dummy_proc.wait()

if __name__ == "__main__":
    test_macos_collection()
