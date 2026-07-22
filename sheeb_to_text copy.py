from functools import partial

import sounddevice as sd
import vosk
import json
import queue
from pythonosc import udp_client

# Config
V_MODEL = "vosk-model-en-us-0.22-lgraph"
# DEST as Destination (where you are sending to)
# could also broadcast, but tailscale doesn't have that capability
DEST_IP = "100.90.76.76"
DEST_PORT = 8000
SAMPLE_RATE = 16000

# Setup
model = vosk.Model(V_MODEL)
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
osc_client = udp_client.SimpleUDPClient(DEST_IP, DEST_PORT)

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(bytes(indata))

# Main Function
def main():
    print(f"Starting speech recognition, sending OSC to {DEST_IP}:{DEST_PORT}")
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16', channels=1, callback=audio_callback):
        #if this doesn't detect the mic, use the "device=x" parameter with the index from the device from check_mic.py
        print("Listening...")
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    osc_client.send_message("/speech/full", text)
                    print("Final:", text)
            else:
                # for sending partial recognitions
                partial = json.loads(recognizer.PartialResult()).get("partial", "")
                if partial:
                    osc_client.send_message("/speech/partial", partial)
                    print("Partial:", partial)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping speech recognition")