import React, { useState } from 'react';
import { View, StyleSheet, SafeAreaView } from 'react-native';
import AppStoreScreen from './src/screens/AppStoreScreen';
import WindowsSegment from './src/components/WindowsSegment';

type Screen = 'appstore' | 'windows-segment';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('appstore');

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {currentScreen === 'appstore' && (
          <AppStoreScreen onOpenWindowsSegment={() => setCurrentScreen('windows-segment')} />
        )}
        {currentScreen === 'windows-segment' && (
          <WindowsSegment onBack={() => setCurrentScreen('appstore')} />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
});
