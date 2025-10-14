import json
import re
from urllib.parse import urlparse

def extract_urls(obj):
    """Recursively extract all URLs from a nested dictionary, list, or string."""
    urls = []

    if isinstance(obj, dict):
        for value in obj.values():
            urls.extend(extract_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls(item))
    elif isinstance(obj, str):
        urls.extend(re.findall(r'https?:\/\/[^\s"\'<>]+|\/\/[^\s"\'<>]+', obj))

    return urls

def normalize_url(url):
    """Ensure the URL has a proper scheme."""
    if url.startswith("//"):
        return "https:" + url
    return url

def extract_domain(url):
    """Extract domain from a URL."""
    parsed = urlparse(url)
    return parsed.netloc

def safe_parse_json(raw_input):
    """Try to parse raw input into JSON; fallback to None if fails."""
    try:
        return json.loads(raw_input)
    except json.JSONDecodeError:
        return None

def process_data(raw_input):
    """Main processing logic that handles structured and unstructured input."""

    # Try to parse the input as JSON
    parsed_data = safe_parse_json(raw_input)

    # If parsing failed, treat the input as plain text
    if parsed_data is None:
        parsed_data = raw_input

    # Extract all URLs
    all_urls_raw = extract_urls(parsed_data)
    all_urls = set(normalize_url(url) for url in all_urls_raw)

    # Try to extract stream URLs only if input was structured
    stream_urls = []
    if isinstance(parsed_data, dict) and "streams" in parsed_data:
        stream_urls = [normalize_url(item.get("stream")) for item in parsed_data.get("streams", []) if item.get("stream")]

    unique_stream_urls = set(stream_urls)
    unique_domains = set(extract_domain(url) for url in all_urls)

    return {
        "total_urls_found": len(all_urls),
        "unique_urls": list(all_urls),
        "total_stream_urls": len(unique_stream_urls),
        "unique_stream_urls": list(unique_stream_urls),
        "total_unique_domains": len(unique_domains),
        "unique_domains": list(unique_domains)
    }

# === EXAMPLE USAGE ===

# Paste your raw input data here (can be JSON or plain text)
raw_input_data = """
{
    "hat.": "",
    "links": 53,
    "added": "2015-03-02T06:28:25.000Z",
    "img_link": "https://www.tata.to/images/file/3a62a280a048b27aef14ef463f0323c4/4e9545af0f5db2c0bcb04c15ec0d1ae7.jpg",
    "filmpalast_url": "http://www.filmpalast.to/movies/view/the-dark-knight-rises",
    "kinox_url": "http://kinox.to/Stream/the_dark_knight_rises-1.html",
    "imdb_url": "http://www.imdb.com/title/tt1345836",
    "streams": [
        {"stream": "//upstream.to/517skprps31y"},
        {"stream": "//streamtape.com/v/BJM8weeODRty0lk/41440%29_The_Dark_Knight_Rises.mp4"},
        {"stream": "https://streamtape.com/v/J3BxgdWGMjfjq7O"},
        {"stream": "https://streamtape.com/e/XbOO7pA6ejSD7RJ"},
        {"stream": "//dood.to/d/078gn38956i4"},
        {"stream": "https://streamtape.com/e/G6Kdy7G0lpu1Ddg"},
        {"stream": "https://streamtape.com/e/0zDMyAYR6bfblGZ"},
        {"stream": "https://streamtape.com/e/yBeGqVxaovI11XR"},
        {"stream": "https://upstream.to/embed-nho5n7ge1qcv.html"},
        {"stream": "https://streamtape.com/e/6kyOqG93aou9XKM"},
        {"stream": "https://dl.streamcloud.club/files/movies/480p/6195193258607cdfb9fa35e9.mp4"}
    ]
}
"""

# Run the processing
results = process_data(raw_input_data)

# Print counts
print("📌 Total unique URLs found:", results["total_urls_found"])
print("📌 Total unique stream URLs:", results["total_stream_urls"])
print("📌 Total unique domains:", results["total_unique_domains"])

# Print Unique Domains
print("\n🌐 Unique Domains:")
if results["unique_domains"]:
    for domain in results["unique_domains"]:
        print("-", domain)
else:
    print("- (None found)")

# Print Unique URLs
print("\n🔗 Unique URLs:")
if results["unique_urls"]:
    for url in results["unique_urls"]:
        print("-", url)
else:
    print("- (None found)")

# Print Unique Stream URLs
print("\n🎥 Unique Stream URLs:")
if results["unique_stream_urls"]:
    for url in results["unique_stream_urls"]:
        print("-", url)
else:
    print("- (None found)")
