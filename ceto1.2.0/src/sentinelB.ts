export class SentinelB {
  private apiUrl: string = 'http://localhost:3001/api';
  private container: HTMLElement;
  private searchHistory: string[] = [];

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
    this.attachEventListeners();
  }

  private render(): void {
    this.container.innerHTML = `
      <div class="sentinel-container">
        <div class="sentinel-header">
          <div class="sentinel-title">
            <span class="sentinel-icon">🛰️</span>
            <h2>Sentinel B</h2>
          </div>
          <p class="sentinel-subtitle">Local Search Engine - Internet Enabled</p>
        </div>

        <div class="search-section">
          <div class="search-box">
            <input 
              type="text" 
              id="search-input" 
              placeholder="Enter your search query..." 
              class="search-input"
              autocomplete="off"
            />
            <button id="search-btn" class="search-btn">
              <span>Search</span>
            </button>
          </div>
          <div class="search-controls">
            <label>
              <input type="number" id="result-limit" value="10" min="1" max="50" />
              <span>Results to fetch</span>
            </label>
          </div>
        </div>

        <div id="results-container" class="results-container hidden">
          <div class="results-header">
            <h3 id="results-title">Search Results</h3>
            <span id="results-meta" class="results-meta"></span>
          </div>
          <div id="results-list" class="results-list"></div>
        </div>

        <div id="error-container" class="error-container hidden">
          <p id="error-message"></p>
        </div>

        <div id="search-history" class="search-history hidden">
          <h3>Search History</h3>
          <div id="history-list" class="history-list"></div>
        </div>

        <div id="loading" class="loading hidden">
          <div class="spinner"></div>
          <p>Searching...</p>
        </div>
      </div>
    `;
  }

  private attachEventListeners(): void {
    const searchBtn = this.container.querySelector('#search-btn') as HTMLButtonElement;
    const searchInput = this.container.querySelector('#search-input') as HTMLInputElement;

    searchBtn.addEventListener('click', () => this.performSearch());
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.performSearch();
    });
  }

  private async performSearch(): Promise<void> {
    const searchInput = this.container.querySelector('#search-input') as HTMLInputElement;
    const query = searchInput.value.trim();
    const limit = parseInt((this.container.querySelector('#result-limit') as HTMLInputElement).value);

    if (!query) {
      this.showError('Please enter a search query');
      return;
    }

    this.showLoading(true);
    this.hideError();

    try {
      const response = await fetch(`${this.apiUrl}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        this.displayResults(data.results, query, data.searchTime);
        this.addToHistory(query);
      } else {
        this.showError(data.error || 'Search failed');
      }
    } catch (error) {
      console.error('Search error:', error);
      this.showError('Failed to connect to Sentinel B server. Is it running on port 3001?');
    } finally {
      this.showLoading(false);
    }
  }

  private displayResults(results: any[], query: string, searchTime: number): void {
    const resultsContainer = this.container.querySelector('#results-container') as HTMLElement;
    const resultsList = this.container.querySelector('#results-list') as HTMLElement;
    const resultsTitle = this.container.querySelector('#results-title') as HTMLElement;
    const resultsMeta = this.container.querySelector('#results-meta') as HTMLElement;

    resultsTitle.textContent = `Results for "${query}"`;
    resultsMeta.textContent = `${results.length} result${results.length !== 1 ? 's' : ''} in ${searchTime}ms`;

    resultsList.innerHTML = results
      .map(
        (result, index) => `
          <div class="result-item">
            <div class="result-number">${index + 1}</div>
            <div class="result-content">
              <h4 class="result-title">${this.escapeHtml(result.title)}</h4>
              <p class="result-snippet">${this.escapeHtml(result.snippet)}</p>
              <div class="result-meta">
                <a href="${result.link}" target="_blank" rel="noopener noreferrer" class="result-link">
                  ${this.escapeHtml(result.link)}
                </a>
                <span class="result-source">${result.source}</span>
              </div>
            </div>
          </div>
        `
      )
      .join('');

    resultsContainer.classList.remove('hidden');
  }

  private addToHistory(query: string): void {
    if (!this.searchHistory.includes(query)) {
      this.searchHistory.unshift(query);
      if (this.searchHistory.length > 5) {
        this.searchHistory.pop();
      }
      this.updateHistoryDisplay();
    }
  }

  private updateHistoryDisplay(): void {
    const historyContainer = this.container.querySelector('#search-history') as HTMLElement;
    const historyList = this.container.querySelector('#history-list') as HTMLElement;

    if (this.searchHistory.length === 0) {
      historyContainer.classList.add('hidden');
      return;
    }

    historyList.innerHTML = this.searchHistory
      .map(
        (query) => `
          <button class="history-item" data-query="${this.escapeHtml(query)}">
            ${this.escapeHtml(query)}
          </button>
        `
      )
      .join('');

    historyContainer.classList.remove('hidden');

    // Add click handlers to history items
    historyList.querySelectorAll('.history-item').forEach((item) => {
      item.addEventListener('click', (e) => {
        const searchInput = this.container.querySelector('#search-input') as HTMLInputElement;
        searchInput.value = (e.target as HTMLElement).getAttribute('data-query') || '';
        this.performSearch();
      });
    });
  }

  private showLoading(show: boolean): void {
    const loading = this.container.querySelector('#loading') as HTMLElement;
    if (show) {
      loading.classList.remove('hidden');
    } else {
      loading.classList.add('hidden');
    }
  }

  private showError(message: string): void {
    const errorContainer = this.container.querySelector('#error-container') as HTMLElement;
    const errorMessage = this.container.querySelector('#error-message') as HTMLElement;
    errorMessage.textContent = message;
    errorContainer.classList.remove('hidden');
  }

  private hideError(): void {
    const errorContainer = this.container.querySelector('#error-container') as HTMLElement;
    errorContainer.classList.add('hidden');
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}
