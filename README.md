# ✋ Hand Gesture-Based Volume Control System

A **Flask-based Computer Vision application** that allows users to control system volume using **hand gestures** detected in real-time via a webcam.  
This project was developed as part of the **Infosys Springboard Virtual Internship 6.0** by *Pavan Kumar Pamu*.

---

## 🚀 Project Overview

This project detects hand gestures such as **open**, **closed**, or **pinching** using **Mediapipe** and **OpenCV**, and maps them to corresponding volume levels.  
The system volume changes smoothly in real-time, and the web interface built with **Flask** displays:
- A live webcam feed  
- Current gesture type  
- Whether a hand is detected  
- The real-time system volume percentage  
- A volume history graph  

---

## 🧠 Technologies Used

| Category | Tools / Libraries |
|-----------|------------------|
| **Backend Framework** | Flask |
| **Computer Vision** | OpenCV |
| **Hand Detection & Tracking** | Mediapipe |
| **System Volume Control** | PyAutoGUI, Pycaw |
| **Frontend** | HTML, CSS, Chart.js |
| **Language** | Python |

---

## 🧩 Features

- 🖐️ Real-time hand detection using Mediapipe landmarks  
- 🔊 Volume adjustment with pinch gestures  
- 📉 Dynamic volume chart visualization  
- 🧭 Smooth and lag-free performance  
- 🌐 Flask-based web interface with responsive dashboard design  
- 💻 System volume synchronization with Pycaw  

---

## 🧾 Project Documentation

- 📘 [Project Completion Report (PDF)](Project%20Documentation/HandGestureVolumeControl_Report.pdf)  
- 📊 [PowerPoint Presentation (PPTX)](Presentation/HandGestureVolumeControl_Presentation.pptx)

---

## 🎬 Demo Video

🎥 [Watch the Project Demo](Demo%20Video/HandGestureVolumeControl_Demo.mp4)

> *(The video demonstrates the live hand detection and real-time system volume synchronization.)*

---

## 📸 Screenshots

| Live Dashboard | Gesture Detection | Volume Chart |
|----------------|------------------|---------------|
| ![Dashboard](screenshots/dashboard.png) | ![Hand Detected](screenshots/hand_detected.png) | ![Volume Chart](screenshots/volume_chart.png) |

---

## 🧱 Project Structure

Volume-Control-With-Hand-Gestures-Using-Webcam/
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
├── Project Documentation/
│   └── HandGestureVolumeControl_Report.pdf
├── Presentation/
│   └── HandGestureVolumeControl_Presentation.pptx
├── Demo Video/
│   └── HandGestureVolumeControl_Demo.mp4
└── screenshots/
    ├── dashboard.png
    ├── hand_detected.png
    └── volume_chart.png
