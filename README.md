## 🛡️ GradePulse: Automated Academic Monitoring System

**GradePulse** is a cloud-native automation tool designed to monitor the **Thapar University Webkiosk** portal for academic result updates. It leverages **Python (Selenium)** for scraping and **GitHub Actions** for CI/CD scheduling to provide real-time alerts via **Telegram**. 

## 🚀 How It Works
1.  **Scheduled Checks:** Runs automatically every 30 minutes via GitHub Actions cron jobs.
2.  **Headless Navigation:** Logs into the university portal using a headless Chrome browser.
3.  **Diff Engine:** Compares current grades against a persistent memory file (`grades_data.txt`) to detect changes.
4.  **Instant Alerts:** Dispatches a notification to your Telegram device immediately upon detecting a new result.

## ⚡Tech Stack
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-Automation-43B02A?logo=selenium&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=github-actions&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram&logoColor=white)

* **Core:** Python 3.9
* **Automation:** Selenium WebDriver
* **Cloud Infrastructure:** GitHub Actions (Ubuntu Runners)
* **Notifications:** Telegram Bot API

## 🔑 Configuration (Secrets)  
This system requires the following repository secrets to function:
* `USER_ID`: Webkiosk Roll Number
* `PASSWORD`: Webkiosk Password
* `BOT_TOKEN`: Telegram Bot API Token
* `CHAT_ID`: Your Telegram User ID

## ⚠️ Disclaimer
This project is intended for **educational purposes only**. The script automates access to personal academic data and is designed to be used responsibly.

* The developer is not responsible for any misuse of this tool.
* **Compliance:** Users must ensure they comply with their institution's IT usage policies and terms of service before using this software.
* **Server Load:** The automation frequency (every 30 mins) is designed to be respectful of university server resources. Do not increase the polling frequency to avoid potential IP bans or server strain.
* Use this tool at your own risk.

## 📄 License
This project is licensed under the [MIT License](LICENSE).
