# Network Connection Troubleshooting

## Issue: "Network request failed" from mobile app

If you're getting "Network request failed" errors, follow these steps:

### Step 1: Install CORS Headers

```bash
cd backend
pip install django-cors-headers
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Run Django Server on All Interfaces

**IMPORTANT:** Django must listen on `0.0.0.0`, not just `127.0.0.1`:

```bash
python manage.py runserver 0.0.0.0:8000
```

This allows connections from your phone on the same network.

### Step 3: Verify Your IP Address

1. **Find your computer's IP:**
   - **Windows**: Open Command Prompt → `ipconfig` → Look for "IPv4 Address"
   - **Mac/Linux**: Open Terminal → `ifconfig` or `ip addr` → Look for "inet"

2. **Update frontend/config.js:**
   ```javascript
   // For Android (if using physical device or specific IP)
   if (Platform.OS === 'android') {
     return 'http://YOUR_IP:8000'; // Replace YOUR_IP with actual IP like 192.168.11.30
   }
   ```

### Step 4: Check Firewall

**Windows:**
1. Open Windows Defender Firewall
2. Allow Python through firewall
3. Or temporarily disable firewall to test

**Mac:**
1. System Settings → Network → Firewall
2. Allow Python or temporarily disable

### Step 5: Verify Network Connection

1. **Same WiFi Network:**
   - Phone and computer MUST be on the same WiFi network
   - Mobile data won't work (unless using tunnel mode)

2. **Test Connection:**
   ```bash
   # On your computer, test if server is accessible
   curl http://YOUR_IP:8000/check -X POST -H "Content-Type: application/json" -d '{"video_url":"test"}'
   ```

### Step 6: Check Django Server Logs

When you make a request from the app, check the Django terminal. You should see:
```
[timestamp] "POST /check HTTP/1.1" 200 ...
```

If you see nothing, the request isn't reaching Django (network/firewall issue).

### Step 7: Use Tunnel Mode (Alternative)

If network issues persist, use Expo tunnel:

```bash
cd frontend
npx expo start --tunnel
```

This uses Expo's servers to tunnel connections (slower but works through firewalls).

### Step 8: Debug in App

The app shows "Connecting to: http://..." at the top. Verify this matches:
1. Your computer's actual IP
2. The port Django is running on (8000)
3. The protocol (http, not https)

### Common Issues:

| Problem | Solution |
|---------|----------|
| Can't connect | Check Django is running on `0.0.0.0:8000` |
| Connection refused | Firewall blocking port 8000 |
| Timeout | Wrong IP address in config.js |
| CORS error | Install and configure django-cors-headers |
| 404 error | Check URL path is `/check` |

### Quick Test Command

Test your Django server is accessible:

```bash
# From your phone's browser (if possible), visit:
http://YOUR_IP:8000/check

# Or from computer:
curl -X POST http://YOUR_IP:8000/check \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://vt.tiktok.com/ZSyMQY6M3/"}'
```

If curl works but app doesn't, it's likely a CORS or React Native networking issue.

### Still Not Working?

1. Check Django logs in terminal for errors
2. Verify `ALLOWED_HOSTS = ['*']` in settings.py
3. Try restarting both Django server and Expo
4. Clear Expo cache: `npx expo start --clear`
5. Check phone and computer are on same WiFi (not different networks/VLANs)

