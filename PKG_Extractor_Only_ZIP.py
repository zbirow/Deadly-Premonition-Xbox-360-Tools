import os
import struct
import zlib
from tkinter import Tk, Label, Button, Entry, filedialog, Text, Scrollbar, END, Frame, StringVar
from tkinter import ttk
import threading

class PKGExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("PKG Extractor")
        self.root.geometry("700x500")
        
        # Variables
        self.input_file = StringVar()
        self.output_dir = StringVar()
        
        # GUI Elements
        main_frame = Frame(root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Input file
        Label(main_frame, text="PKG File:").grid(row=0, column=0, sticky="w", pady=5)
        Entry(main_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=5)
        Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output directory
        Label(main_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5)
        Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Extract button
        Button(main_frame, text="Extract All", command=self.start_extraction, 
               bg="green", fg="white", padx=20, pady=5).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=600, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Status
        self.status_label = Label(main_frame, text="Ready", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Log area
        Label(main_frame, text="Log:").grid(row=5, column=0, sticky="w", pady=5)
        
        log_frame = Frame(main_frame)
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")
        
        self.log_text = Text(log_frame, height=15, wrap="word")
        scrollbar = Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Grid weights
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PKG files", "*.pkg"), ("All files", "*.*")])
        if filename:
            self.input_file.set(filename)
            self.log(f"Selected file: {filename}")
            
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            self.log(f"Selected output directory: {directory}")
    
    def log(self, message):
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.root.update()
    
    def start_extraction(self):
        if not self.input_file.get():
            self.log("Error: Select a PKG file!")
            return
        if not self.output_dir.get():
            self.log("Error: Select an output directory!")
            return
            
        # Run in separate thread
        thread = threading.Thread(target=self.extract_all)
        thread.daemon = True
        thread.start()
    
    def extract_all(self):
        try:
            input_path = self.input_file.get()
            output_base = self.output_dir.get()
            
            # Signature to find (58 5A 50 31)
            signature = bytes([0x58, 0x5A, 0x50, 0x31])
            
            with open(input_path, "rb") as f:
                data = f.read()
            
            self.log(f"Loaded file: {len(data)} bytes")
            
            # Find all signature occurrences
            positions = []
            pos = 0
            while True:
                pos = data.find(signature, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
            
            self.log(f"Found {len(positions)} occurrences of signature 58 5A 50 31")
            
            if not positions:
                self.log("No archives found to extract.")
                self.status_label.config(text="Finished - nothing found", fg="orange")
                return
            
            # Configure progress bar
            self.progress["maximum"] = len(positions)
            
            # Process each found archive
            for idx, start_pos in enumerate(positions):
                try:
                    self.status_label.config(text=f"Processing {idx+1}/{len(positions)}...", fg="blue")
                    self.progress["value"] = idx + 1
                    
                    # Check if we have enough data
                    if start_pos + 20 > len(data):
                        self.log(f"  Skipping {idx+1}: not enough data")
                        continue
                    
                    # Structure:
                    # 4 bytes: signature (58 5A 50 31)
                    # 4 bytes: unknown1 (skip)
                    # 4 bytes: compressed size
                    # 4 bytes: uncompressed size
                    # then: ZIP data (starting with 78 DA)
                    
                    unknown1 = struct.unpack("<I", data[start_pos+4:start_pos+8])[0]
                    compressed_size = struct.unpack("<I", data[start_pos+8:start_pos+12])[0]
                    uncompressed_size = struct.unpack("<I", data[start_pos+12:start_pos+16])[0]
                    
                    # Check ZIP header (78 DA or 78 9C)
                    zip_header = data[start_pos+16:start_pos+18]
                    
                    self.log(f"\n--- Archive {idx+1} ---")
                    self.log(f"  Position: 0x{start_pos:08X}")
                    self.log(f"  Unknown1: 0x{unknown1:08X}")
                    self.log(f"  Compressed size: {compressed_size} bytes")
                    self.log(f"  Uncompressed size: {uncompressed_size} bytes")
                    self.log(f"  ZIP header: {zip_header.hex().upper()}")
                    
                    # Check if it's a valid ZIP header
                    if zip_header not in [b'\x78\xDA', b'\x78\x9C', b'\x78\x01']:
                        self.log(f"  Warning: unusual ZIP header")
                    
                    # Get ZIP data
                    zip_start = start_pos + 16
                    zip_end = zip_start + compressed_size
                    
                    if zip_end > len(data):
                        self.log(f"  Error: ZIP data exceeds file bounds")
                        continue
                    
                    zip_data = data[zip_start:zip_end]
                    
                    # Decompress data
                    try:
                        # zlib decompression
                        decompressed_data = zlib.decompress(zip_data)
                        
                        # Save decompressed data directly in output directory
                        output_filename = f"extracted_{idx+1:03d}.bin"
                        output_path = os.path.join(output_base, output_filename)
                        
                        # If it looks like a ZIP file, save with .zip extension
                        if decompressed_data.startswith(b'PK'):
                            output_filename = f"extracted_{idx+1:03d}.zip"
                            output_path = os.path.join(output_base, output_filename)
                        
                        with open(output_path, "wb") as out_f:
                            out_f.write(decompressed_data)
                        
                        self.log(f"  Saved: {output_filename}")
                        
                        # Check if size matches
                        if len(decompressed_data) != uncompressed_size:
                            self.log(f"  WARNING: Decompressed size ({len(decompressed_data)}) "
                                    f"differs from declared ({uncompressed_size})")
                            diff = len(decompressed_data) - uncompressed_size
                            self.log(f"  Difference: {diff} bytes")
                        else:
                            self.log(f"  Size matches")
                            
                    except zlib.error as e:
                        self.log(f"  Decompression failed: {e}")
                        
                        # Try as regular ZIP
                        import zipfile
                        from io import BytesIO
                        
                        try:
                            with zipfile.ZipFile(BytesIO(zip_data)) as zip_ref:
                                # Extract all contents to output directory
                                zip_ref.extractall(output_base)
                                self.log(f"  Extracted as regular ZIP to: {output_base}")
                        except:
                            self.log(f"  Not a valid ZIP file")
                    
                except Exception as e:
                    self.log(f"  Error processing archive {idx+1}: {e}")
                    import traceback
                    self.log(traceback.format_exc())
            
            self.progress["value"] = 0
            self.status_label.config(text="Finished successfully!", fg="green")
            self.log(f"\nExtraction completed. Files saved to: {output_base}")
            
        except Exception as e:
            self.log(f"Critical error: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.status_label.config(text="Error!", fg="red")

def main():
    root = Tk()
    app = PKGExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
