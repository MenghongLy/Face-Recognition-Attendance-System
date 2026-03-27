# 🎓 Face Recognition Attendance System

## 📌 Overview

This project is a **Face Recognition Attendance System** built using Python.
It uses a webcam to detect and recognize student faces, then automatically records attendance into an Excel file with time and status (On Time / Late).

---

## 🚀 Features

* Detect faces in real-time using webcam
* Recognize students from stored images
* Automatically mark attendance
* Save data into Excel file
* Record time of attendance
* Mark students as **On Time** or **Late**

---

## 🛠️ Technologies Used

* Python
* OpenCV
* face_recognition
* NumPy
* Pandas
* OpenPyXL

---

## 📁 Project Structure

```
FaceAttendanceSystem/
│
├── students/
│     ├── hong.jpg
│     ├── dara.jpg
│     └── lina.jpg
│
├── main.py
├── encoder.py
├── attendance.py
├── requirements.txt
└── attendance.xlsx
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/FaceAttendanceSystem.git
cd FaceAttendanceSystem
```

---

### 2. Install Python

Make sure you install **Python 3.10** (important for compatibility).

---

### 3. Create virtual environment

```
py -3.10 -m venv venv
venv\Scripts\activate
```

---

### 4. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶️ How to Run

```
python main.py
```

* The webcam will open
* When a known face is detected → attendance is recorded
* Data will be saved in `attendance.xlsx`

---

## 📊 Output Example

| Name | Time  | Status  |
| ---- | ----- | ------- |
| Hong | 07:10 | On Time |
| Dara | 07:45 | Late    |

---

## ⏰ Late Rule

* Before 7:30 → On Time
* After 7:30 → Late

(You can modify this in `attendance.py`)

---

## ⚠️ Notes

* Use clear images of students (front face)
* Only one person per image
* Close Excel file before running the program
* Python 3.10 is required (dlib does not support newer versions well)

---

## 💡 Future Improvements

* Add GUI (Tkinter / PyQt)
* Add student ID system
* Store data in database instead of Excel
* Improve accuracy with multiple images per student
* Deploy as web application

---

## 👤 Author

* MengHong

---

## 📜 License

This project is for educational purposes.
