import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import shutil

# Matplotlib headless backend setup
import matplotlib
matplotlib.use('Agg')

DB_PATH = '/workspace/scratch/vori_biometrics.db'
OUT_DIR = '/workspace/out/'
SCRATCH_DIR = '/workspace/scratch/'

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            child_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            elapsed_sec REAL,
            gaze_x REAL,
            gaze_y REAL,
            alpha_power REAL,
            tbr REAL,
            overload_status TEXT,
            visual_cue_opacity REAL,
            visual_mode TEXT
        )
    ''')
    conn.commit()
    return conn

def simulate_and_store_experiment():
    conn = init_db(DB_PATH)
    cursor = conn.cursor()
    
    session_id = "SES_20260919_PILOT_01"
    child_id = "CHILD_ADHD_04"
    visual_mode = "Peripheral Fractal Ring (D=1.35)"
    
    duration_sec = 180  # 3 minutes simulation (1Hz sampling)
    np.random.seed(42)
    
    print(f"[*] Starting EEG + Gaze experiment data simulation ({duration_sec}s)...")
    
    records = []
    
    for t in range(duration_sec):
        # 1. Baseline Phase (0s - 50s): Normal focus
        if t < 50:
            alpha_power = 0.55 + np.random.normal(0, 0.03)
            tbr = 2.1 + np.random.normal(0, 0.15)
            gaze_x = np.random.normal(0.0, 0.08)
            gaze_y = np.random.normal(0.0, 0.05)
            overload_status = "NORMAL"
            opacity = 0.0
            
        # 2. Overload Onset Phase (50s - 100s): Focus drift & Alpha drop
        elif 50 <= t < 100:
            progress = (t - 50) / 50.0
            alpha_power = 0.55 - (progress * 0.35) + np.random.normal(0, 0.04) # drops below 0.35
            tbr = 2.1 + (progress * 2.4) + np.random.normal(0, 0.25)          # spikes above 3.5
            gaze_x = np.random.normal(0.35 * np.sin(t*0.2), 0.25)              # erratic gaze shift
            gaze_y = np.random.normal(0.25 * np.cos(t*0.2), 0.20)
            
            if alpha_power < 0.35:
                overload_status = "SENSORY_OVERLOAD"
                # Visual cue fades in smoothly to calm down
                opacity = min(1.0, (0.35 - alpha_power) * 3.2)
            else:
                overload_status = "FOCUS_DRIFT"
                opacity = 0.0
                
        # 3. De-escalation & Recovery Phase (100s - 180s): Autonomic reset via peripheral cue
        else:
            progress = (t - 100) / 80.0
            alpha_power = 0.20 + (progress * 0.32) + np.random.normal(0, 0.03) # recovers
            tbr = 4.5 - (progress * 2.2) + np.random.normal(0, 0.2)            # lowers back
            gaze_x = np.random.normal(0.0, 0.10)                                # re-centers
            gaze_y = np.random.normal(0.0, 0.08)
            
            if alpha_power < 0.35:
                overload_status = "DE_ESCALATING"
                opacity = max(0.0, (0.35 - alpha_power) * 2.8)
            else:
                overload_status = "RECOVERED_FOCUS"
                opacity = 0.0
                
        # Clamp values
        alpha_power = max(0.05, min(1.0, alpha_power))
        tbr = max(1.0, min(8.0, tbr))
        opacity = max(0.0, min(1.0, opacity))
        
        record = (
            session_id, child_id, float(t),
            float(gaze_x), float(gaze_y),
            float(alpha_power), float(tbr),
            overload_status, float(opacity), visual_mode
        )
        records.append(record)

    # Insert into SQLite Database
    cursor.executemany('''
        INSERT INTO experiment_sessions (
            session_id, child_id, elapsed_sec, gaze_x, gaze_y,
            alpha_power, tbr, overload_status, visual_cue_opacity, visual_mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    print(f"[+] Successfully accumulated {len(records)} records in SQLite DB ({DB_PATH}).")
    
    # 4. Generate Analytics Visualization Chart
    df = pd.read_sql_query("SELECT * FROM experiment_sessions WHERE session_id=?", conn, params=[session_id])
    conn.close()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"Vori Real-Time Experiment Data Log ({child_id} / {session_id})", fontsize=14, fontweight='bold')
    
    # Subplot 1: EEG Alpha Power, TBR, and Visual Cue Intervention
    ax1.plot(df['elapsed_sec'], df['alpha_power'], color='#00f0ff', linewidth=2, label='Alpha Power (Gating)')
    ax1.plot(df['elapsed_sec'], df['tbr'], color='#ffaa00', linewidth=1.8, linestyle='--', label='TBR (Focus Drift)')
    ax1.axhline(0.35, color='#ff3366', linestyle=':', label='Overload Threshold (0.35)')
    
    # Shade Visual Cue Active Period
    ax1_twin = ax1.twinx()
    ax1_twin.fill_between(df['elapsed_sec'], 0, df['visual_cue_opacity'], color='#00a896', alpha=0.25, label='Visual Cue Opacity')
    ax1_twin.set_ylabel('Visual Cue Opacity (0-1)', color='#00a896')
    ax1_twin.set_ylim(0, 1.2)
    
    ax1.set_ylabel('EEG Metrics (uV^2/Hz / Ratio)')
    ax1.set_title('Real-Time EEG Biomarkers & Peripheral Fractal Cue Intervention')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left', fontsize=9)
    
    # Subplot 2: Eye Tracking Gaze Coordinates (Gaze Drift)
    ax2.plot(df['elapsed_sec'], df['gaze_x'], color='#3182ce', linewidth=1.5, label='Gaze X (Horizontal Drift)')
    ax2.plot(df['elapsed_sec'], df['gaze_y'], color='#805ad5', linewidth=1.5, label='Gaze Y (Vertical Drift)')
    ax2.axhline(0.0, color='gray', linestyle='-', alpha=0.3)
    ax2.set_xlabel('Elapsed Time (Seconds)')
    ax2.set_ylabel('Gaze Position (Normalized -1 to +1)')
    ax2.set_title('1-Second Interval Eye Gaze Tracking Vector')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper left', fontsize=9)
    
    plt.tight_layout()
    chart_path = os.path.join(SCRATCH_DIR, 'gaze_eeg_timeseries.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[+] Saved visualization chart to {chart_path}")
    
    # Copy script and chart to output folder
    shutil.copy('/workspace/scratch/experiment_data_simulator.py', os.path.join(OUT_DIR, 'experiment_data_simulator.py'))
    shutil.copy(chart_path, os.path.join(OUT_DIR, 'gaze_eeg_timeseries.png'))
    shutil.copy(DB_PATH, os.path.join(OUT_DIR, 'vori_biometrics.db'))
    print("[+] Published artifacts to /workspace/out/")

if __name__ == '__main__':
    simulate_and_store_experiment()
