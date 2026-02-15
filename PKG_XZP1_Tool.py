import os
import struct
import zlib
import json
from tkinter import Tk, Label, Button, Entry, filedialog, Text, Scrollbar, END, Frame, StringVar, messagebox
from tkinter import ttk
import threading

class PKGTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PKG Tool - XZP1 Extractor & Packer")
        self.root.geometry("900x700")
        
        # Variables
        self.input_file = StringVar()
        self.output_dir = StringVar()
        self.pack_dir = StringVar()
        self.output_pkg = StringVar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Extract tab
        self.extract_frame = Frame(self.notebook)
        self.notebook.add(self.extract_frame, text="Extract PKG")
        self.setup_extract_tab()
        
        # Pack tab
        self.pack_frame = Frame(self.notebook)
        self.notebook.add(self.pack_frame, text="Pack to PKG")
        self.setup_pack_tab()
        
    def setup_extract_tab(self):
        frame = self.extract_frame
        
        # Input PKG file
        Label(frame, text="PKG File:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.input_file, width=60).grid(row=0, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output directory
        Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.output_dir, width=60).grid(row=1, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Extract button
        Button(frame, text="Extract Blocks", command=self.start_extraction, 
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
        
        self.extract_log = Text(log_frame, height=25, wrap="word")
        scrollbar = Scrollbar(log_frame, orient="vertical", command=self.extract_log.yview)
        self.extract_log.configure(yscrollcommand=scrollbar.set)
        
        self.extract_log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Grid weights
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_columnconfigure(1, weight=1)
    
    def setup_pack_tab(self):
        frame = self.pack_frame
        
        # Directory with blocks
        Label(frame, text="Blocks Directory:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.pack_dir, width=60).grid(row=0, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_pack_dir).grid(row=0, column=2)
        
        # Output PKG file
        Label(frame, text="Output PKG:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        Entry(frame, textvariable=self.output_pkg, width=60).grid(row=1, column=1, padx=5)
        Button(frame, text="Browse", command=self.browse_output_pkg).grid(row=1, column=2)
        
        # Pack button
        Button(frame, text="Pack to PKG", command=self.start_packing, 
               bg="blue", fg="white", padx=20, pady=5).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.pack_progress = ttk.Progressbar(frame, orient="horizontal", length=600, mode="indeterminate")
        self.pack_progress.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew", padx=5)
        
        # Status
        self.pack_status = Label(frame, text="Ready", fg="blue")
        self.pack_status.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Log area
        Label(frame, text="Log:").grid(row=5, column=0, sticky="w", pady=5, padx=5)
        
        log_frame = Frame(frame)
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5)
        
        self.pack_log = Text(log_frame, height=25, wrap="word")
        scrollbar = Scrollbar(log_frame, orient="vertical", command=self.pack_log.yview)
        self.pack_log.configure(yscrollcommand=scrollbar.set)
        
        self.pack_log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Info
        info_text = "Directory should contain: zip1.bin (decompressed), zip2.bin, ... and data1.dat, data2.dat, ..."
        Label(frame, text=info_text, fg="gray").grid(row=7, column=0, columnspan=3, pady=10)
        
        # Grid weights
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_columnconfigure(1, weight=1)
    
    # Extract tab functions
    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PKG files", "*.pkg"), ("All files", "*.*")])
        if filename:
            self.input_file.set(filename)
            self.log_extract(f"Selected file: {filename}")
    
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            self.log_extract(f"Selected output directory: {directory}")
    
    # Pack tab functions
    def browse_pack_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.pack_dir.set(directory)
            self.log_pack(f"Selected blocks directory: {directory}")
            self.suggest_output_name()
    
    def browse_output_pkg(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pkg", filetypes=[("PKG files", "*.pkg"), ("All files", "*.*")])
        if filename:
            self.output_pkg.set(filename)
            self.log_pack(f"Output will be saved as: {filename}")
    
    def suggest_output_name(self):
        if self.pack_dir.get():
            base = os.path.basename(self.pack_dir.get())
            self.output_pkg.set(os.path.join(self.pack_dir.get(), base + "_rebuilt.pkg"))
    
    def log_extract(self, message):
        self.extract_log.insert(END, message + "\n")
        self.extract_log.see(END)
        self.root.update()
    
    def log_pack(self, message):
        self.pack_log.insert(END, message + "\n")
        self.pack_log.see(END)
        self.root.update()
    
    # EXTRACTION
    def start_extraction(self):
        if not self.input_file.get():
            self.log_extract("Error: Select a PKG file!")
            return
        if not self.output_dir.get():
            self.log_extract("Error: Select an output directory!")
            return
        
        thread = threading.Thread(target=self.extract_blocks)
        thread.daemon = True
        thread.start()
    
    def extract_blocks(self):
        try:
            self.extract_progress.start()
            self.extract_status.config(text="Extracting...", fg="blue")
            
            input_path = self.input_file.get()
            output_base = self.output_dir.get()
            
            # Signature XZP1
            signature = bytes([0x58, 0x5A, 0x50, 0x31])
            
            with open(input_path, "rb") as f:
                data = f.read()
            
            self.log_extract(f"Loaded file: {len(data)} bytes")
            
            # Find all XZP1 blocks
            zip_blocks = []
            pos = 0
            while pos < len(data):
                pos = data.find(signature, pos)
                if pos == -1:
                    break
                
                if pos + 16 <= len(data):
                    next_offset = struct.unpack("<I", data[pos+4:pos+8])[0]
                    comp_size = struct.unpack("<I", data[pos+8:pos+12])[0]
                    uncomp_size = struct.unpack("<I", data[pos+12:pos+16])[0]
                    
                    # Sprawdź czy to faktycznie ZIP (nagłówek zlib)
                    if pos + 16 + 2 <= len(data):
                        zip_header = data[pos+16:pos+18]
                        if zip_header in [b'\x78\xDA', b'\x78\x9C', b'\x78\x01']:
                            zip_blocks.append({
                                'start': pos,
                                'next': pos + next_offset,
                                'comp_size': comp_size,
                                'uncomp_size': uncomp_size,
                                'data_start': pos + 16,
                                'data_end': pos + 16 + comp_size,
                                'header': zip_header
                            })
                        else:
                            self.log_extract(f"Warning: XZP1 at 0x{pos:08X} doesn't have ZIP header ({zip_header.hex()})")
                
                pos += 1
            
            zip_blocks.sort(key=lambda x: x['start'])
            
            self.log_extract(f"Found {len(zip_blocks)} ZIP blocks")
            
            # Save block info - ONLY FOR ORDER, NOT SIZES!
            block_order = []
            
            # Extract all blocks
            last_end = 0
            zip_counter = 0
            data_counter = 0
            
            for i, block in enumerate(zip_blocks):
                start = block['start']
                next_pos = block['next']
                
                # Data before this ZIP
                if start > last_end:
                    data_counter += 1
                    data_block = data[last_end:start]
                    data_file = f"data{data_counter}.dat"
                    data_path = os.path.join(output_base, data_file)
                    
                    with open(data_path, "wb") as f:
                        f.write(data_block)
                    
                    block_order.append({
                        'type': 'data',
                        'file': data_file
                    })
                    
                    self.log_extract(f"\nData block {data_counter}:")
                    self.log_extract(f"  Range: 0x{last_end:08X} - 0x{start:08X}")
                    self.log_extract(f"  Size: {len(data_block)} bytes")
                    self.log_extract(f"  → {data_file}")
                
                # ZIP block - DECOMPRESS IT!
                zip_counter += 1
                compressed_data = data[block['data_start']:block['data_end']]
                
                try:
                    # Decompress the ZIP data
                    decompressed_data = zlib.decompress(compressed_data)
                    
                    # Save decompressed data as .bin
                    zip_file = f"zip{zip_counter}.bin"
                    zip_path = os.path.join(output_base, zip_file)
                    
                    with open(zip_path, "wb") as f:
                        f.write(decompressed_data)
                    
                    block_order.append({
                        'type': 'zip',
                        'file': zip_file
                    })
                    
                    self.log_extract(f"\nZIP block {zip_counter}:")
                    self.log_extract(f"  Position: 0x{block['start']:08X}")
                    self.log_extract(f"  Next: 0x{block['next']:08X}")
                    self.log_extract(f"  Compressed: {block['comp_size']} bytes")
                    self.log_extract(f"  Uncompressed: {len(decompressed_data)} bytes")
                    self.log_extract(f"  Header: {block['header'].hex()}")
                    self.log_extract(f"  → {zip_file} (DECOMPRESSED)")
                    
                except zlib.error as e:
                    self.log_extract(f"  ERROR: Failed to decompress ZIP at 0x{block['start']:08X}: {e}")
                    # Save compressed data as fallback
                    zip_file = f"zip{zip_counter}_compressed.bin"
                    zip_path = os.path.join(output_base, zip_file)
                    
                    with open(zip_path, "wb") as f:
                        f.write(compressed_data)
                    
                    block_order.append({
                        'type': 'zip',
                        'file': zip_file
                    })
                    
                    self.log_extract(f"  → Saved compressed data as {zip_file}")
                
                last_end = max(last_end, block['data_end'], block['next'])
            
            # Data after last ZIP
            if last_end < len(data):
                data_counter += 1
                data_block = data[last_end:]
                data_file = f"data{data_counter}.dat"
                data_path = os.path.join(output_base, data_file)
                
                with open(data_path, "wb") as f:
                    f.write(data_block)
                
                block_order.append({
                    'type': 'data',
                    'file': data_file
                })
                
                self.log_extract(f"\nData block {data_counter}:")
                self.log_extract(f"  Range: 0x{last_end:08X} - 0x{len(data):08X}")
                self.log_extract(f"  Size: {len(data_block)} bytes")
                self.log_extract(f"  → {data_file}")
            
            # Save ONLY the block order for reconstruction
            order_path = os.path.join(output_base, "block_order.json")
            with open(order_path, "w") as f:
                json.dump(block_order, f, indent=2)
            
            self.log_extract(f"\n=== EXTRACTION SUMMARY ===")
            self.log_extract(f"ZIP blocks (decompressed): {zip_counter}")
            self.log_extract(f"Data blocks: {data_counter}")
            self.log_extract(f"Block order saved: block_order.json")
            self.log_extract(f"Output directory: {output_base}")
            
            self.extract_status.config(text=f"Extracted {zip_counter} ZIP, {data_counter} data", fg="green")
            
        except Exception as e:
            self.log_extract(f"Error: {e}")
            import traceback
            self.log_extract(traceback.format_exc())
            self.extract_status.config(text="Error!", fg="red")
        finally:
            self.extract_progress.stop()
    
    # PACKING
    def start_packing(self):
        if not self.pack_dir.get():
            self.log_pack("Error: Select blocks directory!")
            return
        if not self.output_pkg.get():
            self.log_pack("Error: Select output PKG file!")
            return
        
        thread = threading.Thread(target=self.pack_pkg)
        thread.daemon = True
        thread.start()
    
    def pack_pkg(self):
        try:
            self.pack_progress.start()
            self.pack_status.config(text="Packing...", fg="blue")
            
            blocks_dir = self.pack_dir.get()
            output_path = self.output_pkg.get()
            
            # Load ONLY the block order
            order_path = os.path.join(blocks_dir, "block_order.json")
            if not os.path.exists(order_path):
                self.log_pack("Error: block_order.json not found!")
                self.log_pack("This file is required for correct block ordering.")
                self.pack_status.config(text="Error: No block_order.json", fg="red")
                self.pack_progress.stop()
                return
            
            with open(order_path, "r") as f:
                block_order = json.load(f)
            
            self.log_pack(f"Loaded block order with {len(block_order)} blocks")
            
            # Build the PKG file using CURRENT file sizes
            with open(output_path, "wb") as out_f:
                current_pos = 0
                zip_counter = 0
                data_counter = 0
                
                for block in block_order:
                    block_file = block['file']
                    block_path = os.path.join(blocks_dir, block_file)
                    
                    if not os.path.exists(block_path):
                        self.log_pack(f"Error: Block file not found: {block_file}")
                        continue
                    
                    with open(block_path, "rb") as f:
                        block_data = f.read()
                    
                    if block['type'] == 'zip':
                        zip_counter += 1
                        
                        # Compress the data (since we stored decompressed)
                        compressed = zlib.compress(block_data)
                        comp_size = len(compressed)
                        uncomp_size = len(block_data)
                        
                        # Calculate offset to next block
                        # Offset includes: 16-byte header + compressed data
                        header_size = 16
                        next_offset = header_size + comp_size
                        
                        # Write XZP1 header with CURRENT sizes
                        out_f.write(b'XZP1')  # 58 5A 50 31
                        out_f.write(struct.pack("<I", next_offset))
                        out_f.write(struct.pack("<I", comp_size))
                        out_f.write(struct.pack("<I", uncomp_size))
                        
                        # Write compressed data
                        out_f.write(compressed)
                        
                        self.log_pack(f"\nPacked ZIP block {zip_counter}:")
                        self.log_pack(f"  File: {block_file}")
                        self.log_pack(f"  Offset to next: 0x{next_offset:08X}")
                        self.log_pack(f"  Compressed: {comp_size} bytes (current)")
                        self.log_pack(f"  Uncompressed: {uncomp_size} bytes (current)")
                        self.log_pack(f"  Position: 0x{current_pos:08X}")
                        
                        current_pos += next_offset
                        
                    else:  # data block
                        data_counter += 1
                        
                        # Just write raw data
                        out_f.write(block_data)
                        
                        self.log_pack(f"\nPacked data block {data_counter}:")
                        self.log_pack(f"  File: {block_file}")
                        self.log_pack(f"  Size: {len(block_data)} bytes (current)")
                        self.log_pack(f"  Position: 0x{current_pos:08X}")
                        
                        current_pos += len(block_data)
            
            total_size = os.path.getsize(output_path)
            self.log_pack(f"\n=== PACKING SUMMARY ===")
            self.log_pack(f"Output file: {output_path}")
            self.log_pack(f"Total size: {total_size} bytes")
            self.log_pack(f"ZIP blocks packed: {zip_counter}")
            self.log_pack(f"Data blocks packed: {data_counter}")
            self.log_pack(f"Packing completed!")
            self.log_pack(f"NOTE: All offsets recalculated based on current file sizes")
            
            self.pack_status.config(text=f"Packed {zip_counter} ZIP, {data_counter} data", fg="green")
            
        except Exception as e:
            self.log_pack(f"Error: {e}")
            import traceback
            self.log_pack(traceback.format_exc())
            self.pack_status.config(text="Error!", fg="red")
        finally:
            self.pack_progress.stop()

def main():
    root = Tk()
    app = PKGTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
