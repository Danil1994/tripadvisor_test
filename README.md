# 🏨 Mobile Test Automation for Tripadvisor

This project is a mobile test automation system for **Tripadvisor** using **Python, Appium, and an Android emulator**.  
The test automates the process of **searching for a hotel, collecting prices from different providers, and saving the 
data** as JSON with screenshots.  

## 🚀 Technologies Used
- **Python** - Core programming language
- **Appium** - Mobile automation framework
- **Android Emulator (Genymotion or AVD)** - Device for testing
- **unittest** - Test framework
- **Selenium WebDriver** - Handling UI elements in Appium
- **Dotenv** - Loading environment variables
- **JSON** - Saving extracted data  

## 📌 Test Scenario
The test follows these steps:
1. **Launch the Tripadvisor mobile app**  
2. **Search for the hotel** `"The Grosvenor Hotel"`  
3. **Pick 5 different dates** (specified in `.env` or auto-generated)  
4. **Ensure dates are selected from the beginning** (scroll to the top)  
5. **Extract prices from different providers**  
6. **Take and save a screenshot for each price**  
7. **Store the results in `{curent day.month_houns.minute}_data.json`**  

### 📂 **JSON Output Format**
```json
{
    "The Grosvenor Hotel": {
        "15.03": {
            "Booking.com": {
                "price": "$92",
                "screenshot": "screenshots\\15.03_09.44_Booking.com_26.03_The_Grosvenor_Hotel.png"
            },
            "Agoda.com": {
                "price": "$94",
                "screenshot": "screenshots\\15.03_09.44_Agoda.com_26.03_The_Grosvenor_Hotel.png"
            }
        },
        "17.03": {
            "Vio.com": {
                "price": "$91",
                "screenshot": "screenshots\\15.03_09.44_Vio.com_30.03_The_Grosvenor_Hotel.png"
            }
        }
    }
}
```

# 🔧 Installation Guide
1️⃣ Install Python and Dependencies
* Make sure you have Python 3.9+ installed.

* Clone this repositories
 
```commandline
git clone https://github.com/Danil1994/tripadvisor_test.git
```

* Open the project and create virtual env

* Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

2️⃣ Install and Start Appium
* Download and install Appium: [Appium.io](https://appium.io/docs/en/latest/)
* Start Appium Server:
```bash
appium
```
3️⃣ Set up Android Emulator (or real device)
* Use Genymotion or AVD (Android Virtual Device)
* Ensure adb devices shows your device connected:
```bash
adb devices
```
4️⃣ Configure .env file (optional)
* Create a .env file in the root directory and specify:

```ini

HOTEL_NAME=The Grosvenor Hotel
DATES=15.03,16.03,17.03,20.03,22.03
DEVICE_NAME=Android
APP_PACKAGE=com.google.android.apps.nexuslauncher
APP_ACTIVITY=com.google.android.apps.nexuslauncher.NexusLauncherActivity
```
📌 If not provided, default values will be used.

5️⃣ Run the Test

  **Important.** 
  
  The device or emulator must be on the main page of the phone. 
  
  After testing, the program will return the device to the home screen.
```bash
python main_app/test_runner/runner.py
```


🔍 Key Features
* ✅ Smart date validation (ensures dates are valid and future)
* ✅ Wait functions for page loading (avoiding flakiness)
* ✅ Auto-scroll to top before selecting dates
* ✅ Multiple back-button presses to fully exit the app
* ✅ Handling different Android resolutions & emulators

🚀 Future Improvements
* 🔹 Better logging - Add structured logs for debugging
* 🔹 Parallel execution - Run multiple test instances
* 🔹 Enhance error handling - Detect and retry failed actions
* 🔹 CI/CD integration - Run tests in a cloud environment
* 🔹 Deeper UI validation - Verify more app elements