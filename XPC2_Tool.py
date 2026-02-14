import os
import struct
from tkinter import Tk, Label, Button, Entry, filedialog, Text, Scrollbar, END, Frame, StringVar, messagebox
from tkinter import ttk
import threading

class XPC2Tool:
    def __init__(self, root):
        self.root = root
        self.root.title("XPC2 Tool - Extractor & Packer")
        self.root.geometry("800x600")
        
        # Variables for extract tab
        self.input_xpc2 = StringVar()
        self.output_dir_extract = StringVar()
        
        # Variables for pack tab
        self.dds_file = StringVar()
        self.dat_file = StringVar()
        self.output_bin = StringVar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Extract tab
        self.extract_frame = Frame(self.notebook)
        self.notebook.add(self.extract_frame, text="Extract XPC2")
        self.setup_extract_tab()
        
        # Pack tab
        self.pack_frame = Frame(self.notebook)
        self.notebook.add(self.pack_frame, text="Pack to XPC2")
        self.setup_pack_tab()
        
    def setup_extract_tab(self):
        frame = self.extract_frame
        
        # Input XPC2 file
        Label(frame, text="XPC2 File:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.input_xpc2, width=60).grid(row=0, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_xpc2).grid(row=0, column=2)
        
        # Output directory
        Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.output_dir_extract, width=60).grid(row=1, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_output_extract).grid(row=1, column=2)
        
        # Extract button
        Button(frame, text="Extract Files", command=self.start_extraction, 
               bg="green", fg="white", padx=20, pady=5).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.extract_progress = ttk.Progressbar(frame, orient="horizontal", length=600, mode="indeterminate")
        self.extract_progress.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew", padx=5)
        
        # Status
        self.extract_status = Label(frame, text="Ready", fg="blue")
        self.extract_status.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Log area
        Label(frame, text="Log:").grid(row=5, column=0, sticky="w", pady=5, padx=5)
        
        log_frame = Frame(frame)
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5)
        
        self.extract_log = Text(log_frame, height=20, wrap="word")
        scrollbar = Scrollbar(log_frame, orient="vertical", command=self.extract_log.yview)
        self.extract_log.configure(yscrollcommand=scrollbar.set)
        
        self.extract_log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Grid weights
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
    def setup_pack_tab(self):
        frame = self.pack_frame
        
        # DDS file
        Label(frame, text="DDS File:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.dds_file, width=60).grid(row=0, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_dds).grid(row=0, column=2)
        
        # DAT file
        Label(frame, text="DAT File:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.dat_file, width=60).grid(row=1, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_dat).grid(row=1, column=2)
        
        # Output BIN file
        Label(frame, text="Output BIN:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.output_bin, width=60).grid(row=2, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_output_bin).grid(row=2, column=2)
        
        # Pack button
        Button(frame, text="Pack to BIN", command=self.start_packing, 
               bg="blue", fg="white", padx=20, pady=5).grid(row=3, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.pack_progress = ttk.Progressbar(frame, orient="horizontal", length=600, mode="indeterminate")
        self.pack_progress.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew", padx=5)
        
        # Status
        self.pack_status = Label(frame, text="Ready", fg="blue")
        self.pack_status.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Log area
        Label(frame, text="Log:").grid(row=6, column=0, sticky="w", pady=5, padx=5)
        
        log_frame = Frame(frame)
        log_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=5)
        
        self.pack_log = Text(log_frame, height=20, wrap="word")
        scrollbar = Scrollbar(log_frame, orient="vertical", command=self.pack_log.yview)
        self.pack_log.configure(yscrollcommand=scrollbar.set)
        
        self.pack_log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Info label
        info_text = "Simply appends .dat file with .dds file to create .bin"
        Label(frame, text=info_text, fg="gray").grid(row=8, column=0, columnspan=3, pady=10)
        
        # Grid weights
        frame.grid_rowconfigure(7, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
    # Extract tab functions
    def browse_xpc2(self):
        filename = filedialog.askopenfilename(filetypes=[("XPC2 files", "*.bin;*.xpc2"), ("All files", "*.*")])
        if filename:
            self.input_xpc2.set(filename)
            self.log_extract(f"Selected XPC2 file: {filename}")
            
    def browse_output_extract(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_extract.set(directory)
            self.log_extract(f"Selected output directory: {directory}")
    
    # Pack tab functions
    def browse_dds(self):
        filename = filedialog.askopenfilename(filetypes=[("DDS files", "*.dds"), ("All files", "*.*")])
        if filename:
            self.dds_file.set(filename)
            self.log_pack(f"Selected DDS file: {filename}")
            # Auto-suggest output name
            self.suggest_output_name()
            
    def browse_dat(self):
        filename = filedialog.askopenfilename(filetypes=[("DAT files", "*.dat"), ("All files", "*.*")])
        if filename:
            self.dat_file.set(filename)
            self.log_pack(f"Selected DAT file: {filename}")
            # Auto-suggest output name
            self.suggest_output_name()
            
    def browse_output_bin(self):
        filename = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if filename:
            self.output_bin.set(filename)
            self.log_pack(f"Output will be saved as: {filename}")
    
    def suggest_output_name(self):
        dds = self.dds_file.get()
        if dds:
            base = os.path.splitext(dds)[0]
            self.output_bin.set(base + ".bin")
    
    def log_extract(self, message):
        if hasattr(self, 'extract_log'):
            self.extract_log.insert(END, message + "\n")
            self.extract_log.see(END)
            self.root.update()
    
    def log_pack(self, message):
        if hasattr(self, 'pack_log'):
            self.pack_log.insert(END, message + "\n")
            self.pack_log.see(END)
            self.root.update()
    
    # Extraction function
    def start_extraction(self):
        if not self.input_xpc2.get():
            self.log_extract("Error: Select an XPC2 file!")
            return
        if not self.output_dir_extract.get():
            self.log_extract("Error: Select an output directory!")
            return
            
        thread = threading.Thread(target=self.extract_xpc2)
        thread.daemon = True
        thread.start()
    
    def extract_xpc2(self):
        try:
            self.extract_progress.start()
            self.extract_status.config(text="Extracting...", fg="blue")
            
            input_path = self.input_xpc2.get()
            output_dir = self.output_dir_extract.get()
            
            with open(input_path, "rb") as f:
                data = f.read()
            
            self.log_extract(f"Loaded file: {len(data)} bytes")
            
            # Check magic header
            magic = data[0:4]
            if magic != b'XPC2':
                self.log_extract(f"ERROR: Invalid magic header! Expected 'XPC2', got {magic}")
                self.extract_status.config(text="Error: Invalid file format", fg="red")
                self.extract_progress.stop()
                return
            
            self.log_extract(f"Magic header: XPC2 - OK")
            
            # Skip 28 bytes of padding
            # After magic (4) + 28 padding = 32 bytes offset
            offset = 32
            
            # Read name position (4 bytes)
            name_pos = struct.unpack("<I", data[offset:offset+4])[0]
            self.log_extract(f"Name position: 0x{name_pos:08X}")
            
            # Read DDS start position (4 bytes)
            dds_pos = struct.unpack("<I", data[offset+4:offset+8])[0]
            self.log_extract(f"DDS data position: 0x{dds_pos:08X}")
            
            # Extract name (read until null terminator)
            name = b""
            pos = name_pos
            while pos < len(data) and data[pos:pos+1] != b'\x00':
                name += data[pos:pos+1]
                pos += 1
            
            try:
                name_str = name.decode('ascii')
            except:
                name_str = name.hex()
            
            self.log_extract(f"Extracted name: {name_str}")
            
            # Extract DDS data
            dds_data = data[dds_pos:]
            dds_path = os.path.join(output_dir, name_str)
            with open(dds_path, "wb") as f:
                f.write(dds_data)
            
            self.log_extract(f"Saved DDS file: {dds_path}")
            
            # Save header data as .dat
            header_data = data[0:dds_pos]
            dat_path = os.path.join(output_dir, os.path.splitext(name_str)[0] + ".dat")
            with open(dat_path, "wb") as f:
                f.write(header_data)
            
            self.log_extract(f"Saved DAT file: {dat_path}")
            self.log_extract(f"\nExtraction completed successfully!")
            
            self.extract_status.config(text="Extraction completed!", fg="green")
            
        except Exception as e:
            self.log_extract(f"Error: {e}")
            import traceback
            self.log_extract(traceback.format_exc())
            self.extract_status.config(text="Error during extraction!", fg="red")
        finally:
            self.extract_progress.stop()
    
    # Packing function - SIMPLE CONCATENATION
    def start_packing(self):
        if not self.dds_file.get():
            self.log_pack("Error: Select a DDS file!")
            return
        if not self.dat_file.get():
            self.log_pack("Error: Select a DAT file!")
            return
        if not self.output_bin.get():
            self.log_pack("Error: Select output file!")
            return
            
        thread = threading.Thread(target=self.pack_xpc2)
        thread.daemon = True
        thread.start()
    
    def pack_xpc2(self):
        try:
            self.pack_progress.start()
            self.pack_status.config(text="Packing...", fg="blue")
            
            dds_path = self.dds_file.get()
            dat_path = self.dat_file.get()
            output_path = self.output_bin.get()
            
            # Read files
            with open(dat_path, "rb") as f:
                dat_data = f.read()
            
            with open(dds_path, "rb") as f:
                dds_data = f.read()
            
            self.log_pack(f"Loaded DAT file: {len(dat_data)} bytes")
            self.log_pack(f"Loaded DDS file: {len(dds_data)} bytes")
            
            # Simple concatenation: DAT + DDS = BIN
            with open(output_path, "wb") as f:
                f.write(dat_data)
                f.write(dds_data)
            
            total_size = len(dat_data) + len(dds_data)
            self.log_pack(f"Saved BIN file: {output_path}")
            self.log_pack(f"Total file size: {total_size} bytes")
            self.log_pack(f"\nPacking completed successfully!")
            
            self.pack_status.config(text="Packing completed!", fg="green")
            
        except Exception as e:
            self.log_pack(f"Error: {e}")
            import traceback
            self.log_pack(traceback.format_exc())
            self.pack_status.config(text="Error during packing!", fg="red")
        finally:
            self.pack_progress.stop()

def main():
    root = Tk()
    app = XPC2Tool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
