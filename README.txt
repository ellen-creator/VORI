========================================================================
VORI NEURO-INTERVENTIONAL EYEWEAR - PROJECT ARCHITECTURE & SETUP
========================================================================

Welcome to the Vori project repository! This repository contains the complete 
end-to-end full-stack pipeline for Vori: Real-Time EEG Processing, 
WebXR 3D Biofeedback Visualizer, SQLite Analytics, and Report Generator.

------------------------------------------------------------------------
PROJECT DIRECTORY STRUCTURE FOR TEAM COLLABORATION
------------------------------------------------------------------------
vori-project/
├── backend/       # Real-time EEG &amp; Eye-tracking Signal Processing (WebSocket Server)
├── frontend/      # WebXR 3D Peripheral Visual Simulator (Child Eyewear UI)
├── landing/       # Official Landing Page &amp; Waitlist Collection (GitHub Pages)
├── mobile_app/    # Parent &amp; Clinician Dashboard Mobile App (Future Release)
└── reporting/     # Automated Clinical PDF Report Generator &amp; Biometrics DB

```
└── README.txt                    # Project setup & collaboration guide

------------------------------------------------------------------------
SETUP & RUN INSTRUCTIONS
------------------------------------------------------------------------

1. BACKEND SETUP (Python):
   Install dependencies:
     pip install -r requirements.txt
   
   Run the backend server:
     python vori_backend.py
   
   * Server runs WebSocket at: ws://0.0.0.0:8765

2. FRONTEND SETUP (Web / Meta Quest VR):
   - Rename `vori_frontend.txt` to `index.html`.
   - Double-click `index.html` to open directly in Chrome/Edge/Safari.
   - For standalone testing without backend, click "Test Cue (Force Fade-in): ON" 
     or toggle "Auto EEG Simulation: ON".
   - For Meta Quest VR: Serve index.html via local web server (e.g. `python -m http.server 8000`) 
     and open `http://YOUR_PC_IP:8000` in Meta Quest Browser, then click "Enter VR".

3. REPORT GENERATOR:
   Run the report builder to generate the clinical weekly progress report PDF:
     python build_report.py
   Outputs: `vori_weekly_progress_report.pdf`
