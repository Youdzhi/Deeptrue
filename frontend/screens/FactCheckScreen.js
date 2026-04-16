import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import { API_BASE_URL } from '../config';
import Constants from 'expo-constants';

// Auto-detect API URL based on platform and connection
const getApiUrl = () => {
  if (!__DEV__) {
    return API_BASE_URL || 'https://your-production-api.com';
  }

  // For simulators/emulators
  if (Platform.OS === 'android') {
    return 'http://192.168.11.30:8000'; // Android emulator
  }
  
  if (Platform.OS === 'ios') {
    return 'http://localhost:8000'; // iOS simulator
  }

  // For physical device, try multiple methods to get computer IP
  if (API_BASE_URL) {
    return API_BASE_URL;
  }

  // Method 1: Try to extract from Expo debugger host
  try {
    const debuggerHost = Constants.expoConfig?.extra?.debuggerHost || 
                        Constants.debuggerHost ||
                        Constants.manifest?.debuggerHost;
    
    if (debuggerHost) {
      const ip = debuggerHost.split(':')[0];
      if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
        return `http://${ip}:8000`;
      }
    }
  } catch (e) {
    console.warn('Could not extract IP from debugger host:', e);
  }

  // Method 2: Try to get from Metro bundler connection
  // This happens when you scan QR code - Expo tells device the IP
  // We can't directly access it, so return null to prompt user
  return null;
};

export default function FactCheckScreen({ navigation }) {
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiUrl, setApiUrl] = useState(() => getApiUrl());

  // If API URL is not detected, try to get it from connection info
  useEffect(() => {
    if (!apiUrl && __DEV__) {
      // Try to detect from Expo connection
      const detectedUrl = getApiUrl();
      if (detectedUrl) {
        setApiUrl(detectedUrl);
      } else {
        // Show helpful error message
        setError('Could not detect computer IP. Please check your connection or set IP manually in config.js');
      }
    }
  }, []);

  const handleFactCheck = async () => {
    if (!videoUrl.trim()) {
      Alert.alert('Error', 'Please enter a TikTok URL');
      return;
    }

    if (!apiUrl) {
      Alert.alert(
        'Connection Error',
        'Could not detect your computer\'s IP address.\n\nPlease:\n1. Make sure phone and computer are on same WiFi\n2. Check frontend/config.js for manual IP setting\n3. Look for IP in Expo terminal output',
        [{ text: 'OK' }]
      );
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('Connecting to:', apiUrl);
      const response = await fetch(`${apiUrl}/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: videoUrl.trim(),
          userid: '1234567890',
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to check video');
      }

      setResults(data);
    } catch (err) {
      let errorMessage = 'An error occurred while checking the video';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.name === 'TypeError' && err.message.includes('Network request failed')) {
        errorMessage = `Network request failed. Please check:
        
1. Django server is running: python manage.py runserver 0.0.0.0:8000
2. Phone and computer are on same WiFi
3. IP address is correct: ${apiUrl}
4. Firewall allows connections on port 8000`;
      }
      
      setError(errorMessage);
      console.error('Fact check error:', err);
      console.error('API URL attempted:', apiUrl);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.header}>DeepTrue</Text>
          <View style={styles.loadingContent}>
            <ActivityIndicator size="large" color="#0066ff" />
            <Text style={styles.loadingText}>Analyzing video...</Text>
            <Text style={styles.loadingSubtext}>
              This may take a few moments
            </Text>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  if (results) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          <View style={styles.content}>
            <Text style={styles.header}>DeepTrue</Text>
            
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => {
                setResults(null);
                setVideoUrl('');
              }}
            >
              <Text style={styles.backButtonText}>Check Another Video</Text>
            </TouchableOpacity>

            {/* Results Summary */}
            <View style={styles.resultsContainer}>
              <Text style={styles.sectionTitle}>Analysis Results</Text>
              
              {/* Mean Percentage */}
              <View style={styles.statCard}>
                <Text style={styles.statLabel}>Average AI Generation</Text>
                <Text style={styles.statValue}>{results.mean_percentage.toFixed(2)}%</Text>
              </View>

              {/* Total Frames */}
              <View style={styles.statCard}>
                <Text style={styles.statLabel}>Total Frames Analyzed</Text>
                <Text style={styles.statValue}>{results.total_frames}</Text>
              </View>

              {/* API Calls Made */}
              <View style={styles.statCard}>
                <Text style={styles.statLabel}>Frames Checked</Text>
                <Text style={styles.statValue}>{results.frames_checked}</Text>
              </View>

              {/* LLM Explanation */}
              {results.llm_explanation && (
                <View style={styles.explanationContainer}>
                  <Text style={styles.sectionTitle}>Detailed Analysis</Text>
                  <Text style={styles.explanationText}>
                    {results.llm_explanation}
                  </Text>
                </View>
              )}

              {/* Individual Frames */}
              {results.individual_frames && results.individual_frames.length > 0 && (
                <View style={styles.framesContainer}>
                  <Text style={styles.sectionTitle}>Frame Analysis</Text>
                  {results.individual_frames.map((frame, index) => (
                    <View key={index} style={styles.frameCard}>
                      <Text style={styles.frameName}>{frame.frame_name}</Text>
                      <Text style={styles.framePercentage}>
                        AI: {frame.ai_generated_percentage}%
                      </Text>
                    </View>
                  ))}
                </View>
              )}

              {/* AI Generation Array Summary */}
              {results.ai_generated_array && (
                <View style={styles.arrayContainer}>
                  <Text style={styles.sectionTitle}>Frame-by-Frame Analysis</Text>
                  <Text style={styles.arraySummary}>
                    Array contains {results.ai_generated_array.length} values
                    {'\n'}
                    Range: {Math.min(...results.ai_generated_array)}% - {Math.max(...results.ai_generated_array)}%
                  </Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                    <View style={styles.arrayView}>
                      {results.ai_generated_array.slice(0, 20).map((value, index) => (
                        <View key={index} style={styles.arrayItem}>
                          <Text style={styles.arrayValue}>{value}</Text>
                        </View>
                      ))}
                      {results.ai_generated_array.length > 20 && (
                        <Text style={styles.arrayMore}>
                          ... and {results.ai_generated_array.length - 20} more
                        </Text>
                      )}
                    </View>
                  </ScrollView>
                </View>
              )}
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.header}>DeepTrue</Text>

            {/* API URL Display (for debugging) */}
        {apiUrl && __DEV__ && (
          <View style={styles.apiUrlContainer}>
            <Text style={styles.apiUrlLabel}>Connecting to:</Text>
            <Text style={styles.apiUrlText}>{apiUrl}</Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Enter TikTok URL</Text>
          <TextInput
            style={styles.input}
            placeholder="https://vt.tiktok.com/..."
            placeholderTextColor="#666"
            value={videoUrl}
            onChangeText={setVideoUrl}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
          />
        </View>

        <TouchableOpacity
          style={styles.checkButton}
          onPress={handleFactCheck}
          activeOpacity={0.8}
        >
          <Text style={styles.buttonText}>Start Analysis</Text>
        </TouchableOpacity>

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
          activeOpacity={0.8}
        >
          <Text style={styles.backButtonText}>Back</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  header: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'left',
    marginBottom: 30,
    fontFamily: 'System',
  },
  inputContainer: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    color: '#ffffff',
    marginBottom: 8,
    fontFamily: 'System',
  },
  input: {
    backgroundColor: '#2a2a2a',
    color: '#ffffff',
    padding: 16,
    borderRadius: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#3a3a3a',
    fontFamily: 'System',
  },
  checkButton: {
    backgroundColor: '#0066ff',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
    marginBottom: 16,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'System',
  },
  backButton: {
    backgroundColor: '#0066ff',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    marginTop: 'auto',
    marginBottom: 20,
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'System',
  },
  loadingContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  loadingContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 20,
    fontFamily: 'System',
  },
  loadingSubtext: {
    color: '#999',
    fontSize: 14,
    fontFamily: 'System',
  },
  errorContainer: {
    backgroundColor: '#ff3333',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  errorText: {
    color: '#ffffff',
    fontSize: 14,
    fontFamily: 'System',
  },
  apiUrlContainer: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#3a3a3a',
  },
  apiUrlLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
    fontFamily: 'System',
  },
  apiUrlText: {
    fontSize: 14,
    color: '#0066ff',
    fontFamily: 'System',
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  resultsContainer: {
    gap: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
    fontFamily: 'System',
  },
  statCard: {
    backgroundColor: '#003366',
    padding: 20,
    borderRadius: 12,
  },
  statLabel: {
    color: '#999',
    fontSize: 14,
    marginBottom: 8,
    fontFamily: 'System',
  },
  statValue: {
    color: '#ffffff',
    fontSize: 32,
    fontWeight: 'bold',
    fontFamily: 'System',
  },
  explanationContainer: {
    backgroundColor: '#003366',
    padding: 20,
    borderRadius: 12,
  },
  explanationText: {
    color: '#ffffff',
    fontSize: 16,
    lineHeight: 24,
    fontFamily: 'System',
  },
  framesContainer: {
    gap: 12,
  },
  frameCard: {
    backgroundColor: '#003366',
    padding: 16,
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  frameName: {
    color: '#ffffff',
    fontSize: 14,
    fontFamily: 'System',
  },
  framePercentage: {
    color: '#0066ff',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'System',
  },
  arrayContainer: {
    backgroundColor: '#003366',
    padding: 20,
    borderRadius: 12,
  },
  arraySummary: {
    color: '#ffffff',
    fontSize: 14,
    marginBottom: 12,
    fontFamily: 'System',
  },
  arrayView: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  arrayItem: {
    backgroundColor: '#004488',
    padding: 8,
    borderRadius: 6,
    minWidth: 40,
    alignItems: 'center',
  },
  arrayValue: {
    color: '#ffffff',
    fontSize: 12,
    fontFamily: 'System',
  },
  arrayMore: {
    color: '#999',
    fontSize: 12,
    alignSelf: 'center',
    fontFamily: 'System',
  },
});

