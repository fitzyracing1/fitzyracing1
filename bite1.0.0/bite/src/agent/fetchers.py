from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


class DomainPolicyError(RuntimeError):
    pass


class WebNavigator:
    def __init__(self, allowed_domains: set[str], timeout_s: float, user_agent: str):
        self.allowed_domains = allowed_domains
        self.timeout_s = timeout_s
        self.user_agent = user_agent

    def _assert_allowed(self, url: str) -> None:
        host = urlparse(url).netloc.lower()
        host = host[4:] if host.startswith("www.") else host
        if host not in self.allowed_domains:
            raise DomainPolicyError(f"Domain not allowed: {host}")

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        host = parsed.netloc.lower()
        host = host[4:] if host.startswith("www.") else host

        filtered_qs = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if not k.lower().startswith("utm_")
        ]

        normalized = urlunparse(
            (
                scheme,
                host,
                parsed.path or "/",
                "",
                urlencode(filtered_qs),
                "",
            )
        )
        return normalized

    def fetch(self, url: str) -> tuple[str, str]:
        normalized_url = self.normalize_url(url)
        self._assert_allowed(normalized_url)
        req = Request(normalized_url, headers={"User-Agent": self.user_agent})
        with urlopen(req, timeout=self.timeout_s) as resp:
            final_url = resp.geturl()
            payload = resp.read().decode("utf-8", errors="replace")
        return payload, final_url

    def _clean_text(self, text: str) -> str:
        return " ".join(text.split())

    def _extract_github_trending_candidate(self, soup: BeautifulSoup, page_url: str) -> tuple[str, str, str] | None:
        row = soup.select_one("article.Box-row")
        if row is None:
            return None
        anchor = row.select_one("h2 a[href]")
        if anchor is None:
            return None
        href = anchor.get("href", "")
        title = self._clean_text(anchor.get_text(" "))
        snippet = self._clean_text((row.select_one("p") or row).get_text(" "))
        source_url = urljoin(page_url, href)
        return title, snippet, source_url

    def _extract_hacker_news_candidate(self, soup: BeautifulSoup, page_url: str) -> tuple[str, str, str] | None:
        anchor = soup.select_one("span.titleline a[href]")
        if anchor is None:
            return None
        href = anchor.get("href", "")
        title = self._clean_text(anchor.get_text(" "))
        source_url = urljoin(page_url, href)
        subtext = soup.select_one("span.subline")
        snippet = self._clean_text(subtext.get_text(" ")) if subtext else title
        return title, snippet, source_url

    def _extract_arxiv_candidate(self, soup: BeautifulSoup, page_url: str) -> tuple[str, str, str] | None:
        title_block = soup.select_one("dd div.list-title")
        if title_block is None:
            return None
        title = self._clean_text(title_block.get_text(" ").replace("Title:", "", 1))
        abstract_link = soup.select_one("dt a[title='Abstract']")
        if abstract_link is None:
            return None
        source_url = urljoin(page_url, abstract_link.get("href", ""))
        abstract_block = soup.select_one("dd p.mathjax")
        snippet = self._clean_text(abstract_block.get_text(" ")) if abstract_block else title
        return title, snippet, source_url

    def _extract_huggingface_candidate(self, soup: BeautifulSoup, page_url: str) -> tuple[str, str, str] | None:
        disallowed_prefixes = {"models", "datasets", "spaces", "docs", "tasks", "blog", "pricing", "join", "login", "search"}
        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "")
            if not href.startswith("/") or href.startswith("//"):
                continue
            parts = [part for part in href.split("/") if part]
            if len(parts) < 2 or parts[0] in disallowed_prefixes:
                continue
            title = self._clean_text(anchor.get_text(" "))
            if not title:
                continue
            source_url = urljoin(page_url, href)
            snippet = title
            return title, snippet, source_url
        return None

    def _extract_techcrunch_candidate(self, soup: BeautifulSoup, page_url: str) -> tuple[str, str, str] | None:
        selectors = [
            "a.loop-card__title-link[href]",
            "h3.loop-card__title a[href]",
            "article a[href]",
        ]
        for selector in selectors:
            for anchor in soup.select(selector):
                href = anchor.get("href", "")
                source_url = urljoin(page_url, href)
                if "techcrunch.com/" not in source_url or source_url.rstrip("/") == "https://techcrunch.com":
                    continue
                title = self._clean_text(anchor.get_text(" "))
                if len(title) < 12:
                    continue
                snippet = title
                return title, snippet, source_url
        return None

    def extract_finding(self, html: str, page_url: str) -> tuple[str, str, str]:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        fallback_title = (soup.title.string or "Untitled").strip() if soup.title else "Untitled"
        fallback_body = self._clean_text(soup.get_text(" "))[:4000]

        host = urlparse(page_url).netloc.lower()
        host = host[4:] if host.startswith("www.") else host
        candidate = None
        if host == "github.com" and "/trending" in urlparse(page_url).path:
            candidate = self._extract_github_trending_candidate(soup, page_url)
        elif host == "news.ycombinator.com":
            candidate = self._extract_hacker_news_candidate(soup, page_url)
        elif host == "arxiv.org" and "/list/" in urlparse(page_url).path:
            candidate = self._extract_arxiv_candidate(soup, page_url)
        elif host == "huggingface.co" and "/models" in urlparse(page_url).path:
            candidate = self._extract_huggingface_candidate(soup, page_url)
        elif host == "techcrunch.com":
            candidate = self._extract_techcrunch_candidate(soup, page_url)

        if candidate is not None:
            title, snippet, source_url = candidate
            text = self._clean_text(snippet)
            if len(text) < 160:
                text = self._clean_text(f"{text} {fallback_body}")
            return title[:300], text[:4000], source_url

        return fallback_title[:300], fallback_body, page_url

    def extract_title_and_text(self, html: str) -> tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = (soup.title.string or "Untitled").strip() if soup.title else "Untitled"
        body = " ".join(soup.get_text(" ").split())
        return title[:300], body[:4000]

    def close(self) -> None:
        return None
