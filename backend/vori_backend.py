import asyncio
import json
import time
import numpy as np
import websockets

from asr_filter import ASRFilter
from feature_extractor import FeatureExtractor
from db_manager import DBManager

FS = 128
WINDOW_SIZE = 128

asr = ASRFilter(fs=FS)
extractor = FeatureExtractor(fs=FS, window_size=WINDOW_SIZE)
db = DBManager()

CONNECTED_CLIENTS = set()
raw_buffer = []

def simulate_eeg_sample(t):
    """Simulates real-time raw EEG stream with synthetic alpha/theta waves."""
    theta = 0.7 * np.sin(2 * np.pi * 6.5 * t)
    alpha = (0.6 if int(t) % 12 < 8 else 0.15) * np.sin(2 * np.pi * 10.0 * t)
    beta = 0.3 * np.sin(2 * np.pi * 18.0 * t)
    noise = np.random.normal(0, 0.15)
    return theta + alpha + beta + noise

async def broadcast_loop():
    global raw_buffer
    print("Vori Real-Time Backend Processing Started...")
    while True:
        current_time = time.time()
        new_batch = [simulate_eeg_sample(current_time + i/FS) for i in range(4)]
        raw_buffer.extend(new_batch)

        if len(raw_buffer) >= WINDOW_SIZE + 31:
            window_signal = np.array(raw_buffer[-(WINDOW_SIZE + 31):])
            raw_buffer = raw_buffer[-int(WINDOW_SIZE // 2):]

            cleaned_signal = asr.clean_artifacts(window_signal)
            res = extractor.extract_all(cleaned_signal)
            res["timestamp"] = current_time

            db.log_features(current_time, res)

            if CONNECTED_CLIENTS:
                msg = json.dumps(res)
                await asyncio.gather(*[client.send(msg) for client in CONNECTED_CLIENTS])

        await asyncio.sleep(4 / FS)

async def ws_handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        print("Client disconnected")

async def main():
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765)
    print("WebSocket Server active on ws://0.0.0.0:8765")
    await asyncio.gather(server.wait_closed(), broadcast_loop())

if __name__ == "__main__":
    asyncio.run(main())
