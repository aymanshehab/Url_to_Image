# Bulk Image Downloader (Python/Tkinter)

A professional-grade, multi-threaded GUI application developed for **Ubuntu 24.4** and **Windows 10+** to automate image scraping from datasets. This tool is designed for Data Analysts who need to convert image URL lists (CSV/XLSX) into local directories for computer vision, machine learning datasets, or archival purposes.

## 🚀 Key Features
- **Multi-threaded Architecture:** The download engine runs on a background thread to keep the UI responsive and prevent freezing.
- **State Management:** Real-time **Pause** and **Resume** functionality using thread event signaling (`threading.Event`).
- **Smart Resume Logic:** Automatically detects and skips existing files to save bandwidth and time.
- **Filename Sanitization:** Automatically strips illegal characters from filenames to maintain Linux filesystem compatibility.
- **Real-time Logging:** Scrolled text widget provides immediate feedback on success, failure, and connection timeouts.

## 🛠️ Technical Specifications
- **Operating System:** Ubuntu 24.4 (LTS)
- **Language:** Python 3.12+
- **Key Libraries:**
  - `pandas`: For high-speed data frame parsing.
  - `requests`: For stream-based HTTP downloads.
  - `tkinter`: For the Native-look GUI (Clam theme).
  - `threading`: For asynchronous execution and non-blocking I/O.

## 📋 Installation & Prerequisites
Ensure your Ubuntu system is updated and the required Python packages are installed. 

### Install System Dependencies
```bash
sudo apt update
sudo apt install python3-tk
pip install pandas requests openpyxl
```

### Or, Install System Dependencies from the requirements file
```bash
sudo apt update
sudo apt install python3-tk
pip install -r requirements.txt
```

### Usage Instructions
- **Load Data:** Click **Browse** to select your .csv or .xlsx file.

- **Map Columns:** Enter the exact names of the columns containing the URLs and the Target Filenames.

- **Set Destination:** Choose the output folder (defaults to /images in the script directory).

- **Execute:** - Click Start Download to begin.

- Use Pause to temporarily halt the process.

- Use Resume to pick up exactly where the thread left off.


#### 👨‍💻 Author
Ayman Ali Shehab

Role: Data Analyst

GitHub: aymanali1

Contact: ayman21shehab@outlook.com

📄 License & Copyright
© 2025 Ayman Ali Shehab

This software is provided for professional portfolio and educational use. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, or distribute, subject to the inclusion of this copyright notice.