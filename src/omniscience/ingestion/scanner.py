import os
from pathlib import Path
from typing import List, Callable

IGNORED_DIRS = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
SUPPORTED_EXTS = {".py", ".ts", ".tsx"}

def scan_workspace(workspace_dir: str) -> List[str]:
    """Scan the workspace for supported files, ignoring standard ignored directories."""
    files_to_process = []
    
    for root, dirs, files in os.walk(workspace_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in SUPPORTED_EXTS:
                files_to_process.append(os.path.join(root, file))
                
    return files_to_process

class WorkspaceWatcher:
    def __init__(self, workspace_dir: str, callback: Callable[[str], None]):
        self.workspace_dir = workspace_dir
        self.callback = callback
        self._observer = None

    def start(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class Handler(FileSystemEventHandler):
            def __init__(self, cb, ws_dir):
                self.cb = cb
                self.ws_dir = ws_dir

            def on_modified(self, event):
                if not event.is_directory:
                    self._process(event.src_path)

            def on_created(self, event):
                if not event.is_directory:
                    self._process(event.src_path)

            def _process(self, path):
                # Check ignores
                parts = Path(path).parts
                if any(ignored in parts for ignored in IGNORED_DIRS):
                    return
                ext = os.path.splitext(path)[1]
                if ext in SUPPORTED_EXTS:
                    self.cb(path)

        self._observer = Observer()
        self._observer.schedule(Handler(self.callback, self.workspace_dir), self.workspace_dir, recursive=True)
        self._observer.start()

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
