import React, { useState } from 'react';

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
    category: 'Communication'
  },
  {
    id: 'outlook',
    name: 'Outlook',
    icon: '📧',
    description: 'Email and calendar management',
    category: 'Productivity'
  },
  {
    id: 'onenote',
    name: 'OneNote',
    icon: '📝',
    description: 'Digital notebook for notes and ideas',
    category: 'Productivity'
  },
  {
    id: 'onedrive',
    name: 'OneDrive',
    icon: '☁️',
    description: 'Cloud storage and file sync',
    category: 'Storage'
  },
  {
    id: 'copilot',
    name: 'Copilot',
    icon: '🤖',
    description: 'AI assistant powered by ChatGPT',
    category: 'AI'
  },
  {
    id: 'netflix',
    name: 'Netflix',
    icon: '🎬',
    description: 'Streaming movies and shows',
    category: 'Entertainment'
  },
  {
    id: 'spotify',
    name: 'Spotify',
    icon: '🎵',
    description: 'Music streaming service',
    category: 'Entertainment'
  },
  {
    id: 'discord',
    name: 'Discord',
    icon: '💬',
    description: 'Voice, video, and text communication',
    category: 'Communication'
  },
  {
    id: 'slack',
    name: 'Slack',
    icon: '🔗',
    description: 'Team messaging and collaboration',
    category: 'Communication'
  },
  {
    id: 'notion',
    name: 'Notion',
    icon: '🗂️',
    description: 'All-in-one workspace',
    category: 'Productivity'
  },
  {
    id: 'figma',
    name: 'Figma',
    icon: '🎨',
    description: 'Collaborative design tool',
    category: 'Design'
  }
];

export default function AppStore() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  
  const categories = ['All', ...new Set(appStoreData.map(app => app.category))];
  
  const filteredApps = selectedCategory === 'All' 
    ? appStoreData 
    : appStoreData.filter(app => app.category === selectedCategory);

  const handleAppClick = async (app: AppItem) => {
    setLoading(app.id);
    setMessage(null);
    
    try {
      const result = await window.edgebook?.launchApp?.(app.id);
      if (result?.success) {
        setMessage(`✓ Opening ${app.name}...`);
      } else {
        setMessage(`Opening ${app.name} in browser...`);
      }
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setMessage(`✗ Failed to open ${app.name}`);
      console.error(err);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🛍️ Edge App Store</h1>
        <p style={styles.subtitle}>Discover and launch your favorite apps</p>
      </div>

      {message && (
        <div style={{
          padding: '12px 16px',
          margin: '0 24px 16px',
          backgroundColor: message.startsWith('✗') ? '#fee' : '#efe',
          color: message.startsWith('✗') ? '#c33' : '#3a3',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          {message}
        </div>
      )}

      <div style={styles.filterContainer}>
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            style={{
              ...styles.filterButton,
              ...(selectedCategory === category ? styles.filterButtonActive : {})
            }}
          >
            {category}
          </button>
        ))}
      </div>

      <div style={styles.gridContainer}>
        {filteredApps.map(app => (
          <div
            key={app.id}
            style={{
              ...styles.appCard,
              ...(loading === app.id ? { opacity: 0.7, pointerEvents: 'none' } : {})
            }}
            onClick={() => handleAppClick(app)}
          >
            <div style={styles.appIcon}>{app.icon}</div>
            <h3 style={styles.appName}>{app.name}</h3>
            <p style={styles.appDescription}>{app.description}</p>
            <span style={styles.appCategory}>{app.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: '24px',
    minHeight: '100vh',
    backgroundColor: '#f3f3f3',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  } as React.CSSProperties,
  
  header: {
    marginBottom: '32px',
    textAlign: 'center' as const
  },
  
  title: {
    fontSize: '32px',
    margin: '0 0 8px 0',
    color: '#1f1f1f'
  } as React.CSSProperties,
  
  subtitle: {
    fontSize: '16px',
    color: '#666',
    margin: 0
  } as React.CSSProperties,
  
  filterContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
    flexWrap: 'wrap' as const,
    justifyContent: 'center'
  } as React.CSSProperties,
  
  filterButton: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    backgroundColor: '#fff',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    transition: 'all 0.2s'
  } as React.CSSProperties,
  
  filterButtonActive: {
    backgroundColor: '#0078d4',
    color: '#fff',
    borderColor: '#0078d4'
  } as React.CSSProperties,
  
  gridContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '16px'
  } as React.CSSProperties,
  
  appCard: {
    backgroundColor: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '16px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
  } as React.CSSProperties,
  
  appIcon: {
    fontSize: '48px',
    marginBottom: '12px'
  },
  
  appName: {
    margin: '12px 0 8px 0',
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f1f1f'
  } as React.CSSProperties,
  
  appDescription: {
    margin: '0 0 12px 0',
    fontSize: '13px',
    color: '#666',
    lineHeight: '1.4'
  } as React.CSSProperties,
  
  appCategory: {
    display: 'inline-block',
    padding: '4px 12px',
    backgroundColor: '#e8f2ff',
    color: '#0078d4',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500'
  } as React.CSSProperties
};
