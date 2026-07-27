import './CosmeticsShop.css'

interface Cosmetic {
  id: string
  name: string
  category: 'avatar' | 'title' | 'theme'
  description: string
  price: number
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

interface CosmeticsShopProps {
  playerGold: number
  onBuy: (cosmeticId: string) => void
  onClose: () => void
}

const COSMETICS: Cosmetic[] = [
  {
    id: 'avatar-cyber',
    name: 'Cyber Punk Avatar',
    category: 'avatar',
    description: 'Glowing neon avatar frame',
    price: 500,
    rarity: 'rare',
  },
  {
    id: 'avatar-golden',
    name: 'Golden Elite',
    category: 'avatar',
    description: 'Premium golden avatar',
    price: 1000,
    rarity: 'epic',
  },
  {
    id: 'title-founder',
    name: 'Founder',
    category: 'title',
    description: 'Early player title',
    price: 0,
    rarity: 'legendary',
  },
  {
    id: 'title-legend',
    name: 'Legend',
    category: 'title',
    description: 'Seasonal champion title',
    price: 2000,
    rarity: 'epic',
  },
  {
    id: 'theme-dark',
    name: 'Dark Mode UI',
    category: 'theme',
    description: 'Higher contrast theme',
    price: 250,
    rarity: 'common',
  },
  {
    id: 'theme-matrix',
    name: 'Matrix Theme',
    category: 'theme',
    description: 'Green code cascade theme',
    price: 750,
    rarity: 'rare',
  },
]

export function CosmeticsShop({ playerGold, onBuy, onClose }: CosmeticsShopProps) {
  return (
    <div className="cosmetics-overlay">
      <div className="cosmetics-modal">
        <div className="cosmetics-header">
          <h2>Cosmetics Shop</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="gold-balance">
          <span>Your Gold:</span>
          <strong>{playerGold.toLocaleString()}</strong>
        </div>

        <div className="cosmetics-grid">
          {COSMETICS.map((cosmetic) => (
            <div key={cosmetic.id} className={`cosmetic-card rarity-${cosmetic.rarity}`}>
              <div className="cosmetic-icon">{cosmetic.category === 'avatar' ? '👤' : cosmetic.category === 'title' ? '👑' : '🎨'}</div>
              <h3>{cosmetic.name}</h3>
              <p className="description">{cosmetic.description}</p>
              <div className="rarity-badge">{cosmetic.rarity.toUpperCase()}</div>

              {cosmetic.price === 0 ? (
                <button className="free-btn" disabled>
                  FREE
                </button>
              ) : (
                <button
                  className={`buy-btn ${playerGold >= cosmetic.price ? 'affordable' : 'locked'}`}
                  onClick={() => {
                    if (playerGold >= cosmetic.price) {
                      onBuy(cosmetic.id)
                    }
                  }}
                  disabled={playerGold < cosmetic.price}
                >
                  {playerGold >= cosmetic.price ? `${cosmetic.price} 💰` : 'LOCKED'}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
