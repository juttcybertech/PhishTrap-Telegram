# PhishTrap Telegram

![PhishTrap Telegram Screenshot](https://i.imgur.com/your-screenshot-url.png)

**Created by: [Jutt Cyber Tech](https://github.com/juttcybertech)**

A powerful Telegram bot for educational phishing simulation and data collection. This tool is designed to help raise awareness about phishing attacks by demonstrating what information can be gathered.

---

### ⚠️ Disclaimer

This tool is intended for **educational purposes and authorized security testing only**. The creator is not responsible for any illegal or malicious use of this program. Always have explicit permission before using this tool on any system or network.

---

### ✨ Features

-   **Password Protected**: The bot interface is protected by a password to prevent unauthorized access.
-   **Comprehensive Data Collection**: Gathers device, network, and location information from the client.
-   **Real-time Notifications**: Sends all collected data and webcam pictures directly to your private Telegram chat.
-   **Webcam Capture**: Captures webcam images from the client.
-   **Easy-to-Use Interface**: All actions are handled through a simple inline keyboard menu in Telegram.
-   **Data Persistence**: Saves all client information and images in a structured `data` directory.

---

### ⚙️ Installation

1.  **Clone the repository:**
    *(Assuming your repository is named PhishTrap-Telegram)*
    ```sh
    git clone https://github.com/juttcybertech/PhishTrap-Telegram.git
    cd PhishTrap-Telegram
    ```

2.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

---

### 🛠️ Configuration

Before running the bot, you need to set up your environment variables.

1.  Create a file named `.env` in the root directory of the project.
2.  Add the following content to the `.env` file, replacing the placeholder values with your own:

    ```env
    # Your Telegram bot token from BotFather
    BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

    # The chat ID of the user or group where the bot will send notifications
    CHAT_ID="123456789"

    # The password to access the bot's control panel
    PASSWORD="your-secret-password"

    # The public URL where the Flask server will be accessible (e.g., using ngrok)
    SERVER_URL="https://your-ngrok-url.io"
    ```

---

### 🚀 Usage

1.  **Run the main bot script:**
    ```sh
    python a.py
    ```
2.  Open Telegram and send the `/start` command to your bot to begin.