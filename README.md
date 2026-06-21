#  Cipher Drive

### Secure USB Encryption & Device Protection System

Cipher Drive is a Python-based security solution that automatically detects USB storage devices and protects sensitive data using **AES-256-GCM encryption**. Designed for individuals and organizations that rely on portable storage, Cipher Drive ensures that files remain confidential even if a USB device is lost, stolen, or accessed without authorization.

---

##  Key Features

###  Automatic USB Detection

* Detects connected USB drives in real time.
* Monitors device insertion and removal events.

###  Strong Encryption

* AES-256-GCM authenticated encryption.
* Provides both confidentiality and integrity protection.
* Prevents unauthorized access to stored files.

###  Secure Key Management

* Password-based key generation using PBKDF2-HMAC-SHA256.
* Configurable iteration count for enhanced security.
* Protection against brute-force attacks.

###  Multiple Interfaces

* Command Line Interface (CLI)
* User-Friendly Graphical Interface (GUI)

###  Monitoring & Logging

* Real-time status updates.
* Encryption and decryption activity logs.
* Device event tracking.

###  Backup & Recovery

* Secure backup support.
* Data restoration capabilities.
* Integrity verification through SHA-256 hashing.

###  Cross-Platform Compatibility

* Windows
* Linux
* macOS

---

##  System Architecture

```text
USB Device
     │
     ▼
USB Detection Module
     │
     ▼
File Management Layer
     │
     ▼
Encryption Engine
(AES-256-GCM)
     │
     ▼
Secure Storage
```

---

##  Project Structure

```text
cipher-drive/
│
├── main.py                # CLI application
├── gui_main.py            # Graphical interface
├── crypto_engine.py       # Encryption/Decryption logic
├── usb_manager.py         # USB device detection
├── file_manager.py        # File operations
├── config.py              # Configuration settings
├── requirements.txt       # Project dependencies
└── README.md              # Documentation
```

---

##  Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/cipher-drive.git
cd cipher-drive
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Running the Application

### CLI Version

```bash
python main.py
```

### GUI Version

```bash
python gui_main.py
```

---

##  How It Works

1. Launch Cipher Drive.
2. Create a secure master password.
3. Insert a USB storage device.
4. The system automatically detects the device.
5. Select **Encrypt** or **Decrypt**.
6. Files are processed using AES-256-GCM encryption.
7. Secure logs and integrity checks are generated.

---

##  Security Specifications

| Component            | Technology                 |
| -------------------- | -------------------------- |
| Encryption Algorithm | AES-256-GCM                |
| Key Derivation       | PBKDF2-HMAC-SHA256         |
| Authentication       | GCM Authentication Tag     |
| Hashing              | SHA-256                    |
| Password Protection  | PBKDF2                     |
| Data Integrity       | Cryptographic Verification |

---

##  Dependencies

```text
pycryptodome
psutil
pyusb
watchdog
cryptography
python-dotenv
colorama
```

---

##  System Requirements

| Requirement      | Minimum               |
| ---------------- | --------------------- |
| Python           | 3.6+                  |
| RAM              | 512 MB                |
| Storage          | 50 MB                 |
| Operating System | Windows, Linux, macOS |

---

##  Applications

* Secure portable storage
* Corporate data protection
* Academic and research file security
* Personal document encryption
* USB device management

---

##  Future Enhancements

* Multi-user authentication
* Biometric verification
* Cloud backup integration
* Automatic scheduled encryption
* Role-based access control
* Security analytics dashboard

---

##  Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

##  License

This project is licensed under the MIT License.

---

##  Author

**Mateeba Khalid**

Cybersecurity & Software Development Enthusiast

---

##  Support

If you find this project useful, consider giving it a star on GitHub.

**Secure your portable data. Protect your privacy.**
