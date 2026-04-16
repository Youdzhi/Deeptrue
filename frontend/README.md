# DeepTrue Mobile App

React Native Expo application for fact-checking videos.

## Getting Started

### Prerequisites

- Node.js (v14 or later) - Download from https://nodejs.org/
- npm (comes with Node.js)
- Expo Go app on your phone (iOS/Android)

### Quick Start

1. **Install dependencies** (first time only):
```bash
cd frontend
npm install
```

2. **Start the Expo server:**
```bash
npm start
```

3. **Scan QR code:**
   - **iPhone**: Open Camera app → Point at QR code → Tap notification
   - **Android**: Open Expo Go app → Tap "Scan QR code" → Scan terminal QR code

4. **Or use simulator:**
   - Press `i` for iOS simulator (requires Xcode)
   - Press `a` for Android emulator (requires Android Studio)

### For Physical Device Setup

**IMPORTANT:** If using a physical device, you need to configure the API URL:

1. Find your computer's IP address:
   - Windows: `ipconfig` in Command Prompt
   - Mac/Linux: `ifconfig` in Terminal
   
2. Update `frontend/config.js`:
   ```javascript
   export const API_BASE_URL = __DEV__ 
     ? 'http://YOUR_IP_ADDRESS:8000'  // Replace with your IP
     : 'https://your-production-api.com';
   ```

3. Make sure Django backend is running and accessible:
   ```bash
   cd backend
   python manage.py runserver 0.0.0.0:8000
   ```

### Common Issues

See `START_GUIDE.md` for detailed troubleshooting of:
- Terminal errors
- Connection issues
- QR code scanning problems
- API connection errors

## Project Structure

```
frontend/
├── screens/
│   ├── HomeScreen.js      # Main landing screen
│   └── InfoScreen.js      # Information/How it works screen
├── App.js                 # Main app component with navigation
├── app.json               # Expo configuration
└── package.json          # Dependencies
```

## Features

- **Home Screen**: Landing page with "Start fact-checking" and "How does this work?" buttons
- **Fact Check Screen**: 
  - Input field for TikTok URL
  - Loading screen during video analysis
  - Results display with:
    - Average AI generation percentage
    - Total frames analyzed
    - Detailed LLM explanation
    - Individual frame analysis
    - Frame-by-frame AI percentages
- **Info Screen**: Detailed information about how the app works
- Dark theme with modern UI design

## API Configuration

Before running the app, configure the Django backend URL:

1. **For iOS Simulator**: Already configured to use `http://localhost:8000`
2. **For Android Emulator**: Already configured to use `http://10.0.2.2:8000`
3. **For Physical Device**: 
   - Find your computer's IP address (e.g., `192.168.1.100`)
   - Update `frontend/config.js` with: `http://YOUR_IP_ADDRESS:8000`
   - Make sure your phone and computer are on the same WiFi network

## Backend Setup

Make sure your Django backend is running:
```bash
cd backend
python manage.py runserver
```

The backend should be accessible at `http://localhost:8000/check`

## Development

The app uses React Navigation for screen management and follows the design specifications with:
- Dark grey background (#1a1a1a)
- Blue accent color (#0066ff)
- Dark blue info containers (#003366)
- Clean, modern typography

