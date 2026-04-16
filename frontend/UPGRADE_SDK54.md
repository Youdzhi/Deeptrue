# Upgrading to Expo SDK 54

This guide will help you upgrade your DeepTrue app to Expo SDK 54.

## Step 1: Update Dependencies

The `package.json` has been updated with SDK 54 compatible versions. Now run:

```bash
cd frontend
npm install
```

This will install Expo SDK 54 and all compatible dependencies.

## Step 2: Fix Dependencies (Recommended)

After installation, run Expo's dependency fixer to ensure all versions are compatible:

```bash
npx expo install --fix
```

This command automatically resolves any version conflicts.

## Step 3: Clear Cache (Recommended)

Clear the Metro bundler cache to avoid any caching issues:

```bash
npx expo start --clear
```

Or delete cache manually:
```bash
# Windows
rmdir /s /q node_modules\.cache
# Mac/Linux
rm -rf node_modules/.cache
```

## Step 4: Test Your App

Start the development server:

```bash
npm start
```

Then test on your device or simulator to ensure everything works correctly.

## What Changed in SDK 54

### Key Updates:
- **React Native 0.76.5** - Latest React Native version
- **React 18.3.1** - Updated React version
- **Precompiled React Native for iOS** - Faster build times
- **iOS 26 Liquid Glass Icons** - New icon support

### Breaking Changes to Watch:
- Some deprecated APIs may have been removed
- Check React Navigation documentation for any navigation changes
- Review your custom native modules if you have any

## Troubleshooting

### If you encounter version conflicts:
```bash
# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Fix versions
npx expo install --fix
```

### If Metro bundler fails:
```bash
npx expo start --clear --reset-cache
```

### If you see "Unable to resolve module" errors:
1. Clear Metro cache (see above)
2. Restart Metro bundler
3. If using physical device, restart Expo Go app

## Dependencies Updated

- `expo`: ~49.0.0 → ~54.0.0
- `react`: 18.2.0 → 18.3.1
- `react-native`: 0.72.6 → 0.76.5
- `expo-status-bar`: ~1.6.0 → ~2.0.0
- `expo-constants`: ~14.4.2 → ~17.0.3
- `@react-navigation/native`: ^6.1.9 → ^6.1.18
- `@react-navigation/native-stack`: ^6.9.17 → ^6.11.0
- `react-native-screens`: ~3.22.0 → ~4.4.0
- `react-native-safe-area-context`: 4.7.4 → 4.12.0

## Next Steps

1. ✅ Update `package.json` (Done)
2. ⏳ Run `npm install`
3. ⏳ Run `npx expo install --fix`
4. ⏳ Test the app
5. ⏳ Update any custom code if needed

## References

- [Expo SDK 54 Release Notes](https://expo.dev/changelog/sdk-54)
- [Upgrade Guide](https://docs.expo.dev/bare/upgrade/)
- [React Native 0.76 Changes](https://reactnative.dev/blog/2024/09/05/version-0.76)

