# gui_main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import sys
import logging
from datetime import datetime
import platform

# Import your existing modules
from config import Config
from crypto_engine import CryptoEngine
from file_manager import FileManager

# Try to import USB manager (Windows specific)
try:
    from usb_manager_windows import USBManager
except:
    # Fallback to simple USB detection
    import psutil
    class USBManager:
        def __init__(self):
            self.monitoring = False
            self.callback = None
            self.known_drives = set()
        
        def get_usb_drives(self):
            drives = []
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts.lower():
                    drives.append(partition.device)
            return drives
        
        def detect_new_device(self, callback):
            self.callback = callback
            self.monitoring = True
            self.known_drives = set(self.get_usb_drives())
            threading.Thread(target=self._monitor, daemon=True).start()
        
        def _monitor(self):
            import time
            while self.monitoring:
                current = set(self.get_usb_drives())
                new = current - self.known_drives
                if new:
                    for drive in new:
                        if self.callback:
                            self.callback({'device': drive, 'mountpoint': drive})
                self.known_drives = current
                time.sleep(2)
        
        def stop_monitoring(self):
            self.monitoring = False

class CipherDriveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher Drive - Secure USB Management")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Set icon and theme
        self.setup_theme()
        
        # Initialize components
        self.config = Config()
        self.usb_manager = USBManager()
        self.crypto_engine = None
        self.file_manager = None
        self.is_monitoring = False
        self.usb_detected = []
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
        
        # Setup master password
        self.setup_master_password()
        
        # Start USB monitoring
        self.start_usb_monitoring()
    
    def setup_theme(self):
        """Setup modern theme"""
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f48771',
            'secondary': '#252526',
            'hover': '#2d2d30'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Create custom style for ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Custom.TButton',
                    background=self.colors['accent'],
                    foreground='white',
                    borderwidth=0,
                    focuscolor='none',
                    padding=10)
        
        style.map('Custom.TButton',
                background=[('active', self.colors['hover'])])
        
        style.configure('Custom.TLabel',
                    background=self.colors['bg'],
                    foreground=self.colors['fg'])
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cipher_drive_gui.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CipherDriveGUI')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Paned window for split view
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - Controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        self.create_controls(left_frame)
        
        # Right panel - Status and Logs
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        self.create_status_panel(right_frame)
        
        # Bottom status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header with title and status"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title = ttk.Label(header_frame, 
                        text="Cipher Drive",
                        font=('Segoe UI', 24, 'bold'),
                        foreground=self.colors['accent'])
        title.pack(side=tk.LEFT)
        
        # Status indicator
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20, 
                                        bg=self.colors['bg'], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_indicator.create_oval(2, 2, 18, 18, fill='red', tags='status')
        
        self.status_label = ttk.Label(status_frame, 
                                    text="Disconnected",
                                    font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT)
        
        # Version
        version = ttk.Label(header_frame,
                        text="v2.0",
                        font=('Segoe UI', 10),
                        foreground='gray')
        version.pack(side=tk.RIGHT, padx=10)
    
    def create_controls(self, parent):
        """Create control panel"""
        # Control frame with scrollbar
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(control_frame,
                        text=" Controls",
                        font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 10))
        
        # USB Controls
        usb_group = ttk.LabelFrame(control_frame, text="USB Management", padding=10)
        usb_group.pack(fill=tk.X, pady=5)
        
        self.btn_monitor = ttk.Button(usb_group, 
                                    text=" Start Monitoring",
                                    command=self.toggle_monitoring,
                                    style='Custom.TButton')
        self.btn_monitor.pack(fill=tk.X, pady=2)
        
        self.btn_scan = ttk.Button(usb_group,
                                text=" Scan USB Devices",
                                command=self.scan_usb,
                                style='Custom.TButton')
        self.btn_scan.pack(fill=tk.X, pady=2)
        
        # USB Devices List
        devices_frame = ttk.LabelFrame(control_frame, text="Detected Devices", padding=10)
        devices_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create Treeview for devices
        self.device_tree = ttk.Treeview(devices_frame, 
                                        columns=('Device', 'Size', 'Status'),
                                        show='tree headings',
                                        height=5)
        
        self.device_tree.heading('Device', text='Device')
        self.device_tree.heading('Size', text='Size')
        self.device_tree.heading('Status', text='Status')
        
        self.device_tree.column('Device', width=100)
        self.device_tree.column('Size', width=80)
        self.device_tree.column('Status', width=100)
        
        self.device_tree.pack(fill=tk.BOTH, expand=True)
        
        # Device action buttons
        action_frame = ttk.Frame(devices_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.btn_encrypt = ttk.Button(action_frame,
                                    text=" Encrypt",
                                    command=self.encrypt_selected_device,
                                    style='Custom.TButton')
        self.btn_encrypt.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_decrypt = ttk.Button(action_frame,
                                    text=" Decrypt",
                                    command=self.decrypt_selected_device,
                                    style='Custom.TButton')
        self.btn_decrypt.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # File Operations
        file_group = ttk.LabelFrame(control_frame, text="File Operations", padding=10)
        file_group.pack(fill=tk.X, pady=5)
        
        self.btn_encrypt_dir = ttk.Button(file_group,
                                        text=" Encrypt Directory",
                                        command=self.encrypt_directory,
                                        style='Custom.TButton')
        self.btn_encrypt_dir.pack(fill=tk.X, pady=2)
        
        self.btn_decrypt_dir = ttk.Button(file_group,
                                        text=" Decrypt Directory",
                                        command=self.decrypt_directory,
                                        style='Custom.TButton')
        self.btn_decrypt_dir.pack(fill=tk.X, pady=2)
        
        self.btn_backup = ttk.Button(file_group,
                                    text=" Create Backup",
                                    command=self.create_backup,
                                    style='Custom.TButton')
        self.btn_backup.pack(fill=tk.X, pady=2)
    
    def create_status_panel(self, parent):
        """Create status and log panel"""
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Logs tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text=" Logs")
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                bg=self.colors['secondary'],
                                                fg=self.colors['fg'],
                                                font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear logs button
        clear_frame = ttk.Frame(log_frame)
        clear_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(clear_frame,
                text="Clear Logs",
                command=self.clear_logs,
                style='Custom.TButton').pack(side=tk.RIGHT)
        
        # USB Info tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Device Info")
        
        self.info_text = scrolledtext.ScrolledText(info_frame,
                                                bg=self.colors['secondary'],
                                                fg=self.colors['fg'],
                                                font=('Consolas', 10))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress tab
        progress_frame = ttk.Frame(notebook)
        notebook.add(progress_frame, text="Progress")
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                        mode='determinate',
                                        length=300)
        self.progress_bar.pack(pady=20)
        
        self.progress_label = ttk.Label(progress_frame,
                                    text="Ready",
                                    font=('Segoe UI', 10))
        self.progress_label.pack()
    
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        status_bar = ttk.Frame(parent)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.status_message = ttk.Label(status_bar,
                                    text="Ready",
                                    font=('Segoe UI', 9))
        self.status_message.pack(side=tk.LEFT)
        
        # System info
        sys_info = ttk.Label(status_bar,
                            text=f"Python {platform.python_version()} | {platform.system()}",
                            font=('Segoe UI', 8),
                            foreground='gray')
        sys_info.pack(side=tk.RIGHT)
    
    def setup_master_password(self):
        """Setup master password"""
        def on_ok():
            password = entry.get()
            confirm = confirm_entry.get()
            
            if not password:
                messagebox.showerror("Error", "Password cannot be empty!")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            
            try:
                self.crypto_engine = CryptoEngine(password)
                key_path = self.config.get_key_path()
                self.crypto_engine.generate_key_file(key_path)
                self.file_manager = FileManager(self.crypto_engine)
                messagebox.showinfo("Success", "Master key created successfully!")
                self.add_log(" Master key created successfully!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create master key: {e}")
        
        # Check if key exists
        if not os.path.exists(self.config.get_key_path()):
            # First time setup
            dialog = tk.Toplevel(self.root)
            dialog.title("First Time Setup")
            dialog.geometry("400x250")
            dialog.resizable(False, False)
            dialog.configure(bg=self.colors['bg'])
            
            # Center on parent
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text=" Create Master Password",
                    font=('Segoe UI', 14, 'bold')).pack(pady=10)
            
            ttk.Label(dialog, text="Enter master password:").pack(pady=5)
            entry = ttk.Entry(dialog, show='•', width=30)
            entry.pack(pady=5)
            
            ttk.Label(dialog, text="Confirm password:").pack(pady=5)
            confirm_entry = ttk.Entry(dialog, show='•', width=30)
            confirm_entry.pack(pady=5)
            
            ttk.Button(dialog, text="Create", command=on_ok,
                    style='Custom.TButton').pack(pady=10)
            
            dialog.bind('<Return>', lambda e: on_ok())
            
            # Wait for dialog
            self.root.wait_window(dialog)
        else:
            # Existing key - authentication
            def on_auth():
                password = entry.get()
                if not password:
                    messagebox.showerror("Error", "Password is required!")
                    return
                
                try:
                    self.crypto_engine = CryptoEngine(password)
                    key_path = self.config.get_key_path()
                    self.crypto_engine.load_key_file(key_path)
                    self.file_manager = FileManager(self.crypto_engine)
                    self.add_log(" Authentication successful!")
                    self.update_status(True)
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Authentication failed: {e}")
                    self.add_log(f"Authentication failed: {e}")
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Authentication")
            dialog.geometry("350x150")
            dialog.resizable(False, False)
            dialog.configure(bg=self.colors['bg'])
            
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text=" Enter Master Password",
                    font=('Segoe UI', 12, 'bold')).pack(pady=10)
            
            entry = ttk.Entry(dialog, show='•', width=30)
            entry.pack(pady=10)
            
            ttk.Button(dialog, text="Unlock", command=on_auth,
                    style='Custom.TButton').pack(pady=10)
            
            dialog.bind('<Return>', lambda e: on_auth())
            
            self.root.wait_window(dialog)
    
    def start_usb_monitoring(self):
        """Start USB monitoring"""
        try:
            self.usb_manager.detect_new_device(self.on_usb_detected)
            self.is_monitoring = True
            self.btn_monitor.config(text=" Stop Monitoring")
            self.update_status(True)
            self.add_log("USB monitoring started")
            self.status_message.config(text="Monitoring USB devices...")
        except Exception as e:
            self.add_log(f"Failed to start monitoring: {e}")
    
    def toggle_monitoring(self):
        """Toggle USB monitoring on/off"""
        if self.is_monitoring:
            self.usb_manager.stop_monitoring()
            self.is_monitoring = False
            self.btn_monitor.config(text="▶ Start Monitoring")
            self.update_status(False)
            self.add_log(" USB monitoring stopped")
            self.status_message.config(text="Monitoring stopped")
        else:
            self.start_usb_monitoring()
    
    def on_usb_detected(self, device):
        """Handle USB detection"""
        device_name = device.get('device', 'Unknown')
        mount_point = device.get('mountpoint', '')
        
        self.add_log(f" USB device detected: {device_name}")
        
        # Add to treeview
        self.device_tree.insert('', 'end', 
                            values=(device_name, 'Unknown', 'Detected'),
                            tags=('new',))
        
        # Show notification
        self.status_message.config(text=f" New USB detected: {device_name}")
        
        # Update status indicator
        self.root.after(0, lambda: self.status_indicator.itemconfig('status', fill='yellow'))
        
        # Show info
        info = f"USB Device Detected:\n"
        info += f"Device: {device_name}\n"
        info += f"Mount Point: {mount_point}\n"
        info += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        self.info_text.insert(tk.END, info + "\n" + "-"*40 + "\n")
        self.info_text.see(tk.END)
    
    def scan_usb(self):
        """Manually scan for USB devices"""
        self.add_log("🔍 Scanning for USB devices...")
        try:
            devices = self.usb_manager.get_usb_drives()
            if devices:
                for device in devices:
                    self.on_usb_detected({'device': device, 'mountpoint': device})
                self.add_log(f" Found {len(devices)} USB devices")
            else:
                self.add_log("No USB devices found")
                messagebox.showinfo("Scan Complete", "No USB devices found")
        except Exception as e:
            self.add_log(f" Scan failed: {e}")
    
    def get_selected_device(self):
        """Get selected device from treeview"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a device first")
            return None
        
        item = self.device_tree.item(selection[0])
        values = item['values']
        if not values:
            return None
        
        return {
            'device': values[0],
            'mountpoint': values[0]
        }
    
    def encrypt_selected_device(self):
        """Encrypt files on selected device"""
        device = self.get_selected_device()
        if not device:
            return
        
        if not messagebox.askyesno("Confirm", 
                                f"Encrypt all files on {device['device']}?"):
            return
        
        self.add_log(f" Encrypting files on {device['device']}...")
        self.status_message.config(text=f"Encrypting {device['device']}...")
        
        # Run in thread
        threading.Thread(target=self._encrypt_device, args=(device,), daemon=True).start()
    
    def _encrypt_device(self, device):
        """Background encryption"""
        try:
            results = self.file_manager.process_files(device['mountpoint'], auto_decrypt=False)
            self.root.after(0, lambda: self.on_encryption_complete(results, device))
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f" Encryption failed: {e}"))
    
    def on_encryption_complete(self, results, device):
        """Handle encryption completion"""
        self.add_log(f" Encryption complete on {device['device']}")
        self.add_log(f"   Processed: {len(results['processed'])} files")
        self.add_log(f"   Errors: {len(results['errors'])}")
        self.status_message.config(text=f"Encryption complete on {device['device']}")
        messagebox.showinfo("Complete", f"Encryption complete!\nProcessed: {len(results['processed'])} files")
    
    def decrypt_selected_device(self):
        """Decrypt files on selected device"""
        device = self.get_selected_device()
        if not device:
            return
        
        if not messagebox.askyesno("Confirm", 
                                f"Decrypt files on {device['device']}?"):
            return
        
        self.add_log(f" Decrypting files on {device['device']}...")
        self.status_message.config(text=f"Decrypting {device['device']}...")
        
        threading.Thread(target=self._decrypt_device, args=(device,), daemon=True).start()
    
    def _decrypt_device(self, device):
        """Background decryption"""
        try:
            results = self.file_manager.process_files(device['mountpoint'], auto_decrypt=True)
            self.root.after(0, lambda: self.on_decryption_complete(results, device))
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f" Decryption failed: {e}"))
    
    def on_decryption_complete(self, results, device):
        """Handle decryption completion"""
        self.add_log(f" Decryption complete on {device['device']}")
        self.add_log(f"   Processed: {len(results['processed'])} files")
        self.add_log(f"   Errors: {len(results['errors'])}")
        self.status_message.config(text=f"Decryption complete on {device['device']}")
        messagebox.showinfo("Complete", f"Decryption complete!\nProcessed: {len(results['processed'])} files")
    
    def encrypt_directory(self):
        """Encrypt a directory"""
        directory = filedialog.askdirectory(title="Select directory to encrypt")
        if not directory:
            return
        
        if not messagebox.askyesno("Confirm", f"Encrypt all files in {directory}?"):
            return
        
        self.add_log(f" Encrypting directory: {directory}")
        self.status_message.config(text=f"Encrypting {directory}...")
        
        threading.Thread(target=self._encrypt_directory, args=(directory,), daemon=True).start()
    
    def _encrypt_directory(self, directory):
        """Background directory encryption"""
        try:
            results = self.file_manager.process_files(directory, auto_decrypt=False)
            self.root.after(0, lambda: self.on_directory_encryption_complete(results, directory))
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f" Encryption failed: {e}"))
    
    def on_directory_encryption_complete(self, results, directory):
        """Handle directory encryption completion"""
        self.add_log(f" Encryption complete on {directory}")
        self.add_log(f"   Processed: {len(results['processed'])} files")
        self.add_log(f"   Errors: {len(results['errors'])}")
        self.status_message.config(text=f"Encryption complete on {directory}")
        messagebox.showinfo("Complete", f"Encryption complete!\nProcessed: {len(results['processed'])} files")
    
    def decrypt_directory(self):
        """Decrypt a directory"""
        directory = filedialog.askdirectory(title="Select directory to decrypt")
        if not directory:
            return
        
        if not messagebox.askyesno("Confirm", f"Decrypt files in {directory}?"):
            return
        
        self.add_log(f" Decrypting directory: {directory}")
        self.status_message.config(text=f"Decrypting {directory}...")
        
        threading.Thread(target=self._decrypt_directory, args=(directory,), daemon=True).start()
    
    def _decrypt_directory(self, directory):
        """Background directory decryption"""
        try:
            results = self.file_manager.process_files(directory, auto_decrypt=True)
            self.root.after(0, lambda: self.on_directory_decryption_complete(results, directory))
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f" Decryption failed: {e}"))
    
    def on_directory_decryption_complete(self, results, directory):
        """Handle directory decryption completion"""
        self.add_log(f"Decryption complete on {directory}")
        self.add_log(f"   Processed: {len(results['processed'])} files")
        self.add_log(f"   Errors: {len(results['errors'])}")
        self.status_message.config(text=f"Decryption complete on {directory}")
        messagebox.showinfo("Complete", f"Decryption complete!\nProcessed: {len(results['processed'])} files")
    
    def create_backup(self):
        """Create encrypted backup"""
        source = filedialog.askdirectory(title="Select source directory")
        if not source:
            return
        
        backup_dir = filedialog.askdirectory(title="Select backup destination")
        if not backup_dir:
            return
        
        if not messagebox.askyesno("Confirm", f"Create encrypted backup from {source}?"):
            return
        
        self.add_log(f"Creating backup from {source} to {backup_dir}")
        self.status_message.config(text=f"Creating backup...")
        
        threading.Thread(target=self._create_backup, args=(source, backup_dir), daemon=True).start()
    
    def _create_backup(self, source, backup_dir):
        """Background backup creation"""
        try:
            backup_path = self.file_manager.create_secure_backup(source, backup_dir)
            self.root.after(0, lambda: self.on_backup_complete(backup_path))
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f" Backup failed: {e}"))
    
    def on_backup_complete(self, backup_path):
        """Handle backup completion"""
        self.add_log(f" Backup created successfully: {backup_path}")
        self.status_message.config(text=f"Backup complete: {backup_path}")
        messagebox.showinfo("Complete", f"Backup created successfully!\nLocation: {backup_path}")
    
    def add_log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.logger.info(message)
    
    def clear_logs(self):
        """Clear log text"""
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.log_text.delete(1.0, tk.END)
            self.add_log("Logs cleared")
    
    def update_status(self, connected):
        """Update status indicator"""
        color = '#4ec9b0' if connected else '#f48771'
        status = 'Connected' if connected else 'Disconnected'
        self.status_indicator.itemconfig('status', fill=color)
        self.status_label.config(text=status)
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_monitoring:
            self.usb_manager.stop_monitoring()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = CipherDriveGUI(root)
    app.run()

if __name__ == "__main__":
    main()