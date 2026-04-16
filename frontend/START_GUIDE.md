# How to Run DeepTrue Expo App

## Step-by-Step Setup & Running Instructions

### 1. Install Dependencies (First Time Only)

```bash
cd frontend
npm install
```

**If you see errors:**
- **"npm: command not found"** → Install Node.js from https://nodejs.org/
- **"Permission denied"** → Try `sudo npm install` (Mac/Linux) or run terminal as Administrator (Windows)

### 2. Start Expo Development Server

```bash
npm start
```

Or use:
```bash
npx expo start
```

**What you'll see:**
```
› Metro waiting on exp://192.168.x.x:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press r │ reload app
› Press m │ toggle menu
```

### 3. Scan QR Code

#### For iPhone:
1. Open the **Camera** app
2. Point it at the QR code in the terminal
3. Tap the notification that appears
4. The app opens in **Expo Go** (install from App Store if needed)

#### For Android:
1. Install **Expo Go** from Google Play Store
2. Open Expo Go app
3. Tap "Scan QR code"
4. Scan the QR code from terminal

### 4. For Physical Device (Important!)

**If you get connection errors**, you need to configure the API URL:

1. **Find your computer's IP address:**
   - **Windows**: Open Command Prompt, type `ipconfig`, look for "IPv4 Address"
   - **Mac/Linux**: Open Terminal, type `ifconfig` or `ip addr`, look for "inet"
   - Example: `192.168.1.100`

2. **Update `frontend/config.js`:**
   ```javascript
   export const API_BASE_URL = __DEV__ 
     ? 'http://192.168.1.100:8000'  // Use YOUR IP address
     : 'https://your-production-api.com';
   ```

3. **Make sure Django backend allows your device:**
   - Update `backend/deeptrue/settings.py`:
   ```python
   ALLOWED_HOSTS = ['*']  # Or add your specific IPs
   ```
   
4. **Restart Django server:**
   ```bash
   cd backend
   python manage.py runserver 0.0.0.0:8000
   ```
   The `0.0.0.0` allows connections from any network interface.

## Common Terminal Errors & Solutions

### Error: "expo: command not found"
**Solution:**
```bash
npm install -g expo-cli
# OR use npx instead:
npx expo start
```

### Error: "Metro bundler failed to start"
**Solution:**
```bash
# Clear cache and restart
npx expo start --clear
```

### Error: "Cannot connect to Metro bundler"
**Solutions:**
1. Make sure port 8081 is not in use:
   ```bash
   # Kill process on port 8081
   # Windows:
   netstat -ano | findstr :8081
   taskkill /PID <PID> /F
   
   # Mac/Linux:
   lsof -ti:8081 | xargs kill -9
   ```

2. Try different port:
   ```bash
   npx expo start --port 8082
   ```

### Error: "Unable to resolve module"
**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
# Then restart
npm start
```

### Error: "Network request failed" (in app)
**Solutions:**
1. **Check API URL in `config.js`** - Make sure it matches your setup
2. **Check Django is running:**
   ```bash
   cd backend
   python manage.py runserver
   ```
3. **For physical device:** Ensure phone and computer are on same WiFi
4. **Check firewall:** Allow Node.js and Python through firewall

### Error: "TypeError: Cannot read property 'xxx' of undefined"
**Solution:** Usually means API response format is different. Check:
1. Django server is running
2. API endpoint returns expected JSON format
3. Check terminal for Django errors

### Error: "Expo Go app not installed"
**Solution:**
- **iOS**: Install "Expo Go" from App Store
- **Android**: Install "Expo Go" from Google Play Store

### Error: "Port already in use"
**Solution:**
```bash
# Use tunnel mode (works through firewalls)
npx expo start --tunnel

# Or use different port
npx expo start --port 8082
```

## Running Commands

### Start with clear cache:
```bash
npx expo start --clear
```

### Start with tunnel (for difficult networks):
```bash
npx expo start --tunnel
```

### Start for specific platform:
```bash
npm run android  # Android only
npm run ios       # iOS only
npm run web       # Web browser
```

### Open in simulator directly:
```bash
# Press 'i' for iOS simulator (requires Xcode)
# Press 'a' for Android emulator (requires Android Studio)
```

## Troubleshooting Checklist

1. ✅ Node.js installed? (`node --version`)
2. ✅ Dependencies installed? (`npm install` completed)
3. ✅ Django backend running? (`python manage.py runserver`)
4. ✅ Phone and computer on same WiFi? (for physical device)
5. ✅ Expo Go app installed on phone?
6. ✅ API URL configured correctly in `config.js`?
7. ✅ No firewall blocking ports 8000 or 8081?

## Quick Start Script

Create `start.sh` (Mac/Linux) or `start.bat` (Windows):

**start.sh:**
```bash
#!/bin/bash
cd frontend
npm install
npm start
```

**start.bat:**
```batch
cd frontend
npm install
npm start
```

Then run: `./start.sh` or `start.bat`

## Still Having Issues?

1. Check Expo docs: https://docs.expo.dev/
2. Check terminal output for specific error messages
3. Make sure all dependencies are installed
4. Try `npx expo start --clear --reset-cache`

