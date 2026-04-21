import tkinter as tk
from tkinter import filedialog
from sample_r.components.base import BaseComponent
from sample_r.bus import bus, MessageType

class TopMenu(tk.Menu, BaseComponent):
    def __init__(self, master, **kwargs):
        # ID 0 for the entry-point component
        BaseComponent.__init__(self, 0, MessageType.TOP_MENU)
        tk.Menu.__init__(self, master, **kwargs)

        # Initialize Dropdowns
        self._setup_file_menu()
        self._setup_action_menu()

    def _setup_file_menu(self):
        file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Import", command=self._on_import)
        file_menu.add_command(label="Export", command=self._on_export)

    def _setup_action_menu(self):
        action_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Action", menu=action_menu)
        
        action_menu.add_command(label="Sort", command=lambda: self.emit("SORT_REQUEST"))
        action_menu.add_command(label="Analyze All", command=lambda: self.emit("ANALYZE_ALL"))

    def _on_import(self):
        # Open file dialog for audio files
        paths = filedialog.askopenfilenames(
            title="Import Samples",
            filetypes=[("Audio Files", "*.wav *.flac *.mp3"), ("All Files", "*.*")]
        )
        if paths:
            bus.push(MessageType.IMPORT, self.cid, paths)
        else:
            bus.push(MessageType.IMPORT_FAILURE, self.cid, [])

    def _on_export(self):
        # Logic for choosing export directory or filename
        path = filedialog.asksaveasfilename(title="resynthesis.wav")
        if path:
            bus.push(MessageType.FILE_EXPORT, self.cid, path)