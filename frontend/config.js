import Constants from 'expo-constants';
import { Platform } from 'react-native';

/**
 * Automatically detects the computer's IP address from Expo connection info
 * This reads the IP from the Metro bundler connection when you scan the QR code
 */
const getComputerIP = () => {
  if (!__DEV__) {
    // Production - use your production API URL
    return 'https://your-production-api.com';
  }

  // For simulators/emulators
  if (Platform.OS === 'android') {
    // Android emulator uses special IP
    return 'http://192.168.11.30:8000';
  }
  
  if (Platform.OS === 'ios') {
    // iOS simulator can use localhost
    return 'http://localhost:8000';
  }

  // For physical devices, try multiple methods to get IP from Expo
  
  // Method 1: Try Constants.expoConfig.extra.debuggerHost (SDK 54)
  try {
    const debuggerHost = Constants.expoConfig?.extra?.debuggerHost;
    if (debuggerHost) {
      const ip = debuggerHost.split(':')[0];
      if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
        console.log('Detected IP from expoConfig:', ip);
        return `http://${ip}:8000`;
      }
    }
  } catch (e) {
    console.warn('Method 1 failed:', e);
  }

  // Method 2: Try Constants.debuggerHost (older SDKs)
  try {
    if (Constants.debuggerHost) {
      const ip = Constants.debuggerHost.split(':')[0];
      if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
        console.log('Detected IP from debuggerHost:', ip);
        return `http://${ip}:8000`;
      }
    }
  } catch (e) {
    console.warn('Method 2 failed:', e);
  }

  // Method 3: Try manifest.debuggerHost (legacy)
  try {
    const manifest = Constants.manifest || Constants.expoConfig;
    if (manifest?.debuggerHost) {
      const ip = manifest.debuggerHost.split(':')[0];
      if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
        console.log('Detected IP from manifest:', ip);
        return `http://${ip}:8000`;
      }
    }
  } catch (e) {
    console.warn('Method 3 failed:', e);
  }

  // Method 4: Try to extract from connection URL
  // When Expo starts, it shows: "Metro waiting on exp://192.168.x.x:8081"
  // We can't directly read this, but we can log hints for manual setup
  console.warn('Could not auto-detect IP. Please check Expo terminal for IP address.');
  console.warn('Look for a line like: "Metro waiting on exp://192.168.x.x:8081"');
  console.warn('Then update config.js with: export const API_BASE_URL = "http://YOUR_IP:8000"');
  
  return null; // Will prompt user for manual setup
};

// Export the detected IP or null (for manual configuration)
export const API_BASE_URL = getComputerIP();

// MANUAL OVERRIDE: If auto-detection fails, uncomment and set your IP here:
// Look at your Expo terminal output when you run "npm start"
// Find the IP address shown (e.g., "exp://192.168.1.100:8081")
// Use that IP below:
// export const API_BASE_URL = 'http://192.168.1.100:8000'; // Replace with YOUR IP from Expo terminal

