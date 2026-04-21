import tkinter as tk
from sample_r.components.top_menu import TopMenu
from sample_r.bus import bus, MessageType, EMPTY_MSG
from sample_r.dsp.audio import AudioData

class SamplerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sampler-R")
        
        # 1. Window Sizing & Aspect Ratio (e.g., 1280x720)
        self.target_ratio = 16 / 9
        self.root.geometry("1280x720")
        
        # Bind the resize event
        self.root.bind('<Configure>', self._maintain_aspect_ratio)

        # 2. Initialize Top Menu
        self.menu_bar = TopMenu(self.root)
        self.root.config(menu=self.menu_bar)

        self.elements = []

        self.dispatch_map = {
            MessageType.IMPORT: self._handle_import,
            MessageType.IMPORT_FAILURE: self._handle_import_failure,
            MessageType.EXPORT: self._handle_export,
            MessageType.DATA_LOADED: self._handle_data_loaded,

        }

        self._poll_bus()

    def _maintain_aspect_ratio(self, event):
        """Forces the window to stay roughly within a 16:9 ratio during resize."""
        # Only trigger if the event is for the root window itself
        if event.widget == self.root:
            new_width = event.width
            new_height = int(new_width / self.target_ratio)
            
            # To avoid infinite recursion during resize, we check if 
            # the height is already correct-ish (tolerance of 5px)
            if abs(event.height - new_height) > 5:
                self.root.geometry(f"{new_width}x{new_height}")

    def _poll_bus(self):
        """
        Drains the bus queue until empty.
        """
        while True:
            msg = bus.pop()
            
            # If we hit the Null Object, the queue is drained
            if msg == EMPTY_MSG:
                break
                
            self.handle_message(msg)

        # Schedule the next poll
        self.root.after(50, self._poll_bus)
    

    def run(self):
        self.root.mainloop()

    def _process_import_queue(self, paths):
        """A generator that processes files one by one."""
        self.elements = []
        for i, p in enumerate(paths):
            try:
                # Using i+1 so ID 0 remains reserved for system/menu
                new_element = AudioData(p, i + 1, 2048)
                self.elements.append(new_element)
                print(f"Loaded {i+1}: {new_element.name}")
            except Exception as e:
                print(f"Failed to load {p}: {e}")
            
            # This 'yield' pauses the loop and returns control to the caller
            yield 

        # Once the loop finishes, notify the system
        bus.push(MessageType.DATA_LOADED, 0, len(self.elements))


    def handle_message(self, msg):
        """Dispatches the message to the appropriate handler."""
        handler = self.dispatch_map.get(msg.msg_type)
        
        if handler:
            handler(msg)
        else:
            print(f"DEBUG: No behavior defined for message type: {msg.msg_type}")

    # --- Individual Handlers ---

    def _handle_import(self, msg):
        """Triggered by the Dispatch Table."""
        paths = msg.value
        # Create the generator instance
        import_gen = self._process_import_queue(paths)
        # Start the 'pump'
        self._next(import_gen)

    def _next(self, gen):
        """Executes one step of the generator, then schedules the next."""
        try:
            next(gen)
            # Schedule the next 'yield' in 1ms to keep UI responsive
            self.root.after(1, lambda: self._next(gen))
        except StopIteration:
            # Generator is exhausted, import is finished
            print("Batch Import Processing Complete.")
    
    def _handle_import_failure(self, msg):
        print("No files imported")

    def _handle_export(self, msg):
        print(f"Exporting data to: {msg.value}")

    def _handle_data_loaded(self, msg):
        print("Model updated. Refreshing UI components...")
        # This is where we will eventually tell the Element List to 'respond'

    