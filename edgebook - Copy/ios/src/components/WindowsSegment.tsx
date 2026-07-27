import React, { useState, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  TextInput,
  Alert,
  Linking,
  FlatList,
} from 'react-native';

export interface WindowsApp {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  executablePath?: string;
  webUrl?: string;
  isInstalled?: boolean;
}

const windowsAppsData: WindowsApp[] = [
  {
    id: 'vscode',
    name: 'Visual Studio Code',
    description: 'Lightweight code editor',
    icon: '💻',
    category: 'Development',
    executablePath: 'C:\\Users\\[USER]\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
    isInstalled: true,
  },
  {
    id: 'vs',
    name: 'Visual Studio 2022',
    description: 'Full-featured IDE',
    icon: '🔧',
    category: 'Development',
    executablePath: 'C:\\Program Files\\Microsoft Visual Studio\\2022\\[Edition]\\Common7\\IDE\\devenv.exe',
    isInstalled: false,
  },
  {
    id: 'node',
    name: 'Node.js',
    description: 'JavaScript runtime',
    icon: '⚙️',
    category: 'Development',
    executablePath: 'C:\\Program Files\\nodejs\\node.exe',
    isInstalled: true,
  },
  {
    id: 'git',
    name: 'Git',
    description: 'Version control system',
    icon: '📦',
    category: 'Development',
    executablePath: 'C:\\Program Files\\Git\\bin\\git.exe',
    isInstalled: true,
  },
  {
    id: 'docker',
    name: 'Docker Desktop',
    description: 'Container platform',
    icon: '🐳',
    category: 'Development',
    executablePath: 'C:\\Program Files\\Docker\\Docker\\Docker.exe',
    isInstalled: false,
  },
  {
    id: 'azure-cli',
    name: 'Azure CLI',
    description: 'Azure command line interface',
    icon: '☁️',
    category: 'Development',
    executablePath: 'C:\\Program Files (x86)\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd',
    isInstalled: false,
  },
  {
    id: 'powershell',
    name: 'PowerShell 7',
    description: 'Modern shell and scripting language',
    icon: '🖥️',
    category: 'System',
    executablePath: 'C:\\Program Files\\PowerShell\\7\\pwsh.exe',
    isInstalled: true,
  },
  {
    id: 'terminal',
    name: 'Windows Terminal',
    description: 'Modern terminal application',
    icon: '⌨️',
    category: 'System',
    webUrl: 'https://github.com/microsoft/terminal',
    isInstalled: true,
  },
  {
    id: 'wsl',
    name: 'Windows Subsystem for Linux',
    description: 'Linux compatibility layer',
    icon: '🐧',
    category: 'System',
    webUrl: 'https://docs.microsoft.com/windows/wsl',
    isInstalled: false,
  },
  {
    id: 'hyper-v',
    name: 'Hyper-V',
    description: 'Virtual machine platform',
    icon: '🖨️',
    category: 'System',
    webUrl: 'https://docs.microsoft.com/virtualization/hyper-v-on-windows',
    isInstalled: false,
  },
  {
    id: 'photoshop',
    name: 'Adobe Photoshop',
    description: 'Image editing software',
    icon: '🎨',
    category: 'Design',
    executablePath: 'C:\\Program Files\\Adobe\\Adobe Photoshop [Version]\\Photoshop.exe',
    isInstalled: false,
  },
  {
    id: 'illustrator',
    name: 'Adobe Illustrator',
    description: 'Vector graphics editor',
    icon: '✏️',
    category: 'Design',
    executablePath: 'C:\\Program Files\\Adobe\\Adobe Illustrator [Version]\\Support Files\\Contents\\Windows\\Illustrator.exe',
    isInstalled: false,
  },
  {
    id: 'blender',
    name: 'Blender',
    description: '3D modeling and animation',
    icon: '🎬',
    category: 'Design',
    executablePath: 'C:\\Program Files\\Blender Foundation\\Blender [Version]\\blender.exe',
    isInstalled: false,
  },
  {
    id: 'obs',
    name: 'OBS Studio',
    description: 'Video recording and streaming',
    icon: '📹',
    category: 'Media',
    executablePath: 'C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe',
    isInstalled: false,
  },
  {
    id: 'ffmpeg',
    name: 'FFmpeg',
    description: 'Multimedia framework',
    icon: '🎥',
    category: 'Media',
    executablePath: 'C:\\ffmpeg\\bin\\ffmpeg.exe',
    isInstalled: false,
  },
  {
    id: 'vlc',
    name: 'VLC Media Player',
    description: 'Multimedia player',
    icon: '▶️',
    category: 'Media',
    executablePath: 'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',
    isInstalled: true,
  },
];

interface Props {
  onBack: () => void;
}

export default function WindowsSegment({ onBack }: Props) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [filteredApps, setFilteredApps] = useState(windowsAppsData);

  const categories = Array.from(new Set(windowsAppsData.map(app => app.category))).sort();

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    const filtered = windowsAppsData.filter(app => {
      const matchesSearch = app.name.toLowerCase().includes(query.toLowerCase()) ||
                          app.description.toLowerCase().includes(query.toLowerCase());
      const matchesCategory = !selectedCategory || app.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
    setFilteredApps(filtered);
  }, [selectedCategory]);

  const handleCategoryFilter = useCallback((category: string | null) => {
    setSelectedCategory(category);
    const filtered = windowsAppsData.filter(app => {
      const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          app.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = !category || app.category === category;
      return matchesSearch && matchesCategory;
    });
    setFilteredApps(filtered);
  }, [searchQuery]);

  const handleLaunchApp = (app: WindowsApp) => {
    if (!app.isInstalled) {
      Alert.alert(
        'App Not Installed',
        `${app.name} is not installed on your Windows machine. To use this app, you need to install it on your Windows system first.`,
        [
          { text: 'Close', onPress: () => {} },
          app.webUrl ? {
            text: 'Learn More',
            onPress: () => Linking.openURL(app.webUrl!),
          } : { text: '', onPress: () => {} },
        ]
      );
      return;
    }

    // In a real implementation, this would send a request to your Windows backend
    // to launch the application via Remote Desktop or a custom API
    Alert.alert(
      'Launching Application',
      `${app.name} would be launched on your Windows machine.\n\nPath: ${app.executablePath || app.webUrl}`,
      [
        { text: 'Close', onPress: () => {} },
      ]
    );
  };

  const renderApp = ({ item }: { item: WindowsApp }) => (
    <TouchableOpacity
      style={styles.appCard}
      onPress={() => handleLaunchApp(item)}
    >
      <View style={styles.appCardContent}>
        <Text style={styles.iconText}>{item.icon}</Text>
        <View style={styles.appInfo}>
          <Text style={styles.appName}>{item.name}</Text>
          <Text style={styles.appDescription}>{item.description}</Text>
          <View style={styles.appMeta}>
            <Text style={[styles.appCategory, { color: item.isInstalled ? '#4CAF50' : '#FF9800' }]}>
              {item.isInstalled ? '✓ Installed' : '○ Not Installed'}
            </Text>
            <Text style={styles.appCategory}>{item.category}</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Windows Apps</Text>
        <View style={{ width: 60 }} />
      </View>

      <View style={styles.searchSection}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search Windows apps..."
          value={searchQuery}
          onChangeText={handleSearch}
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
          onPress={() => handleCategoryFilter(null)}
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
            onPress={() => handleCategoryFilter(category)}
          >
            <Text style={[
              styles.categoryText,
              selectedCategory === category && styles.categoryTextActive,
            ]}>
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <FlatList
        data={filteredApps}
        renderItem={renderApp}
        keyExtractor={item => item.id}
        style={styles.appsList}
        contentContainerStyle={styles.appsListContent}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    width: 60,
    paddingVertical: 8,
  },
  backText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
    flex: 1,
    textAlign: 'center',
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
  appsList: {
    flex: 1,
  },
  appsListContent: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    gap: 12,
  },
  appCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  appCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 12,
  },
  iconText: {
    fontSize: 40,
  },
  appInfo: {
    flex: 1,
  },
  appName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  appDescription: {
    fontSize: 13,
    color: '#666',
    marginBottom: 8,
  },
  appMeta: {
    flexDirection: 'row',
    gap: 12,
  },
  appCategory: {
    fontSize: 12,
    color: '#999',
  },
});
