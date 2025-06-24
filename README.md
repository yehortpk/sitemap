# Template-Aware Sitemap Builder

A fast, structure-based web scraper that builds semantic sitemaps by clustering similar HTML pages into template-based routes. Unlike traditional crawlers, this tool automatically identifies reusable page layouts (e.g., blog posts, product pages) and generalizes them into dynamic routes like `/article/:id`, while preserving static routes like `/about`.

---

## 🛡️ Tech Stack & Compatibility

![Python](https://img.shields.io/badge/python-3.12-blue)
![aiohttp](https://img.shields.io/badge/aiohttp-%3E%3D3.9-lightgrey)
![BeautifulSoup](https://img.shields.io/badge/bs4-%3E%3D4.12-yellow)

---

## ✨ Features

- 🚀 Asynchronous static HTML crawler (no rendering required)
- 🔎 Template detection via structural feature hashing (SimHash)
- 🧠 Clustering of pages based on layout similarity
- 🗺️ Outputs semantic sitemap with both static and dynamic routes
- 💡 Detects common content templates without storing full page data

---

## 🔧 How It Works

1. **Crawl HTML pages** using `aiohttp` or `httpx` with async queues.
2. **Parse DOM structure** (tags, class names, IDs).
3. **Generate SimHash fingerprints** from DOM features.
4. **Compare pages** by SimHash Hamming distance.
5. **Cluster pages** into templates and extract dynamic patterns from their URLs.
6. **Output a semantic sitemap** in JSON or YAML.

---

## 🛠️ Requirements

- Python 3.12+
- [`aiohttp`](https://docs.aiohttp.org/)
- [`beautifulsoup4`](https://www.crummy.com/software/BeautifulSoup/)
- [`lxml`](https://lxml.de/)
- [`simhash`](https://pypi.org/project/simhash/)
- (Optional) `fastapi`, `uvicorn`, `tqdm`, `networkx`

---

## 🚀 Quick Start

```bash
git clone https://github.com/yehortpk/sitemap.git
cd sitemap-builder
pip install -r requirements.txt

python main.py --url https://example.com --depth 2
