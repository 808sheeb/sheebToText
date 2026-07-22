from pythonosc import udp_client
import time

OSC_IP = "100.90.76.76" # this is either a broadcast IP (tailscale doesn't support that i think)
                        # or the IP which you are SENDING TO

OSC_PORT = 8000

client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

for i in range(5):
    client.send_message("/speech/text", f"test message {i}")
    print(f"Sent test message {i}")
    time.sleep(1)
