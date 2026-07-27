import React, { useState, useMemo } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  TextInput,
  Linking,
  Alert,
} from 'react-native';

export interface AppItem {
  id: string;
  name: string;
  icon: string;
  description: string;
  category: string;
  url?: string;
}

const appStoreData: AppItem[] = [
  {
    id: 'edge',
    name: 'Microsoft Edge',
    icon: '🌐',
    description: 'The web browser from Microsoft',
    category: 'Browser',
    url: 'https://www.microsoft.com/edge'
  },
  {
    id: 'teams',
    name: 'Microsoft Teams',
    icon: '👥',
    description: 'Chat, meet, and call all in one place',
    category: 'Communication',
    url: 'https://www.microsoft.com/teams/download'
  },
  {
    id: 'outlook',
    name: 'Outlook',
    icon: '📧',
    description: 'Email and calendar management',
    category: 'Productivity',
    url: 'https://outlook.live.com'
  },
  {
    id: 'onenote',
    name: 'OneNote',
    icon: '📝',
    description: 'Digital notebook for notes and ideas',
    category: 'Productivity',
    url: 'https://www.onenote.com'
  },
  {
    id: 'onedrive',
    name: 'OneDrive',
    icon: '☁️',
    description: 'Cloud storage and file sync',
    category: 'Storage',
    url: 'https://onedrive.live.com'
  },
  {
    id: 'copilot',
    name: 'Copilot',
    icon: '🤖',
    description: 'AI assistant powered by ChatGPT',
    category: 'AI',
    url: 'https://copilot.microsoft.com'
  },
  {
    id: 'netflix',
    name: 'Netflix',
    icon: '🎬',
    description: 'Streaming movies and shows',
    category: 'Entertainment',
    url: 'https://www.netflix.com'
  },
  {
    id: 'spotify',
    name: 'Spotify',
    icon: '🎵',
    description: 'Music streaming service',
    category: 'Entertainment',
    url: 'https://www.spotify.com'
  },
  {
    id: 'discord',
    name: 'Discord',
    icon: '💬',
    description: 'Voice, video, and text communication',
    category: 'Communication',
    url: 'https://discord.com'
  },
  {
    id: 'slack',
    name: 'Slack',
    icon: '🔗',
    description: 'Team messaging and collaboration',
    category: 'Communication',
    url: 'https://slack.com'
  },
  {
    id: 'notion',
    name: 'Notion',
    icon: '🗂️',
    description: 'All-in-one workspace',
    category: 'Productivity',
    url: 'https://www.notion.so'
  },
  {
    id: 'figma',
    name: 'Figma',
    icon: '🎨',
    description: 'Collaborative design tool',
    category: 'Design',
    url: 'https://www.figma.com'
  }
];

interface Props {
  onOpenWindowsSegment: () => void;
}

export default function AppStoreScreen({ onOpenWindowsSegment }: Props) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = Array.from(new Set(appStoreData.map(app => app.category))).sort();

  const filteredApps = useMemo(() => {
    return appStoreData.filter(app => {
      const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          app.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = !selectedCategory || app.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  const handleLaunchApp = (app: AppItem) => {
    if (app.url) {
      Linking.openURL(app.url).catch(() => {
        Alert.alert('Error', `Could not open ${app.name}`);
      });
    } else {
      Alert.alert('Info', `${app.name} is not available on iPad. Please use the Windows Segment to access desktop applications.`);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>EdgeBook OS - App Store</Text>
      </View>

      <View style={styles.searchSection}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search apps..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#999"
        />
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesScroll}
        contentContainerStyle={styles.categoriesContainer}
      >
        <TouchableOpacity
          style={[
            styles.categoryButton,
            selectedCategory === null && styles.categoryButtonActive,
          ]}
          onPress={() => setSelectedCategory(null)}
        >
          <Text style={[
            styles.categoryText,
            selectedCategory === null && styles.categoryTextActive,
          ]}>
            All
          </Text>
        </TouchableOpacity>

        {categories.map(category => (
          <TouchableOpacity
            key={category}
            style={[
              styles.categoryButton,
              selectedCategory === category && styles.categoryButtonActive,
            ]}
            onPress={() => setSelectedCategory(category)}
          >
            <Text style={[
              styles.categoryText,
              selectedCategory === category && styles.categoryTextActive,
            ]}>
              {category}
            </Text>
          </TouchableOpacity>
        ))}

        <TouchableOpacity
          style={[styles.categoryButton, { borderColor: '#007AFF', borderWidth: 2 }]}
          onPress={onOpenWindowsSegment}
        >
          <Text style={[styles.categoryText, { color: '#007AFF', fontWeight: 'bold' }]}>
            Windows Apps
          </Text>
        </TouchableOpacity>
      </ScrollView>

      <ScrollView style={styles.appsContainer} showsVerticalScrollIndicator={false}>
        <View style={styles.appsGrid}>
          {filteredApps.map(app => (
            <TouchableOpacity
              key={app.id}
              style={styles.appCard}
              onPress={() => handleLaunchApp(app)}
            >
              <View style={styles.appIcon}>
                <Text style={styles.iconText}>{app.icon}</Text>
              </View>
              <Text style={styles.appName} numberOfLines={2}>{app.name}</Text>
              <Text style={styles.appDescription} numberOfLines={2}>{app.description}</Text>
              <Text style={styles.appCategory}>{app.category}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  searchSection: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#fff',
  },
  searchInput: {
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#000',
  },
  categoriesScroll: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  categoriesContainer: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    gap: 8,
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#e0e0e0',
  },
  categoryButtonActive: {
    backgroundColor: '#007AFF',
  },
  categoryText: {
    color: '#000',
    fontSize: 14,
    fontWeight: '500',
  },
  categoryTextActive: {
    color: '#fff',
  },
  appsContainer: {
    flex: 1,
    padding: 20,
  },
  appsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 16,
  },
  appCard: {
    width: '22%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  appIcon: {
    width: 60,
    height: 60,
    borderRadius: 12,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconText: {
    fontSize: 32,
  },
  appName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#000',
    textAlign: 'center',
    marginBottom: 4,
  },
  appDescription: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
    marginBottom: 4,
  },
  appCategory: {
    fontSize: 9,
    color: '#999',
    textAlign: 'center',
  },
});
