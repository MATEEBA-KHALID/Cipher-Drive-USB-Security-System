
# usb_manager_windows.py
import psutil
import time
import threading
import os
import logging
import platform
from datetime import datetime

class USBManager:
    def __init__(self):
        self.usb_devices = {}
        self.monitoring = False
        self.monitor_thread = None
        self.callback = None
        self.known_devices = set()
        self.setup_logging()
        self.update_known_devices()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('USBManager')
    
    def get_usb_devices(self):
        """Get list of connected USB devices (Windows compatible)"""
        devices = []
        try:
            # Method 1: Using psutil
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts.lower():
                    device_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts
                    }
                    
                    # Get disk usage
                    try:
                        if os.path.exists(partition.mountpoint):
                            usage = psutil.disk_usage(partition.mountpoint)
                            device_info['total'] = usage.total
                            device_info['used'] = usage.used
                            device_info['free'] = usage.free
                            device_info['percent'] = usage.percent
                    except:
                        pass
                    
                    devices.append(device_info)
            
            # Method 2: Windows API (more accurate)
            try:
                import string
                from ctypes import windll
                
                for letter in string.ascii_uppercase:
                    drive_path = letter + ':\\'
                    if os.path.exists(drive_path):
                        drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                        # DRIVE_REMOVABLE = 2
                        if drive_type == 2:
                            # Check if already added via psutil
                            if not any(d['device'] == drive_path for d in devices):
                                device_info = {
                                    'device': drive_path,
                                    'mountpoint': drive_path,
                                    'fstype': 'Unknown',
                                    'opts': 'removable'
                                }
                                
                                # Get disk usage
                                try:
                                    usage = psutil.disk_usage(drive_path)
                                    device_info['total'] = usage.total
                                    device_info['used'] = usage.used
                                    device_info['free'] = usage.free
                                    device_info['percent'] = usage.percent
                                except:
                                    pass
                                
                                devices.append(device_info)
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error detecting USB devices: {e}")
        
        return devices
    
    def update_known_devices(self):
        """Update the list of known devices"""
        devices = self.get_usb_devices()
        self.known_devices = {d['device'] for d in devices}
        return self.known_devices
    
    def detect_new_device(self, callback):
        """Monitor for new USB devices"""
        self.callback = callback
        self.monitoring = True
        
        # Update known devices
        self.update_known_devices()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("USB monitoring started on Windows")
    
    def _monitor_loop(self):
        """Monitor loop for USB detection"""
        while self.monitoring:
            try:
                current_devices = self.get_usb_devices()
                current_device_ids = {d['device'] for d in current_devices}
                
                # Check for new devices
                new_devices = [
                    d for d in current_devices 
                    if d['device'] not in self.known_devices
                ]
                
                if new_devices:
                    for device in new_devices:
                        self.logger.info(f"New USB device detected: {device['device']}")
                        if self.callback:
                            self.callback(device)
                
                # Update known devices
                self.known_devices = current_device_ids
                
                # Sleep before checking again
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    def stop_monitoring(self):
        """Stop USB monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("USB monitoring stopped")
    
    def mount_device(self, device_path):
        """Mount a USB device (Windows)"""
        # On Windows, drives are already mounted
        return device_path
    
    def unmount_device(self, mount_point):
        """Unmount a USB device (Windows)"""
        # On Windows, we don't unmount
        return True