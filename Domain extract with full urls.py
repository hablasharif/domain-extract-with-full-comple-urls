import streamlit as st
import json
import re
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime

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

def main():
    # Configure the page
    st.set_page_config(
        page_title="URL Extractor Pro",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🔗 Universal URL Extractor")
    st.markdown("Extract URLs, domains, and stream links from JSON data or plain text")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.markdown("""
        **How to use:**
        1. Paste your JSON data or plain text in the input area
        2. Click 'Extract URLs' to process
        3. View results in organized sections
        4. Download results as needed
        
        **Supported formats:**
        - JSON with nested structures
        - Plain text with URLs
        - Mixed content with stream URLs
        """)
        
        st.header("📊 Features")
        st.markdown("""
        - ✅ Extract all URLs recursively
        - ✅ Normalize protocol-relative URLs
        - ✅ Identify stream URLs specifically
        - ✅ Extract unique domains
        - ✅ Beautiful visual presentation
        - ✅ Export capabilities
        """)
    
    # Input section
    st.subheader("📥 Input Data")
    
    # Example data for quick testing
    example_data = """{
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
}"""
    
    # Input text area with example
    input_text = st.text_area(
        "Paste your JSON data or text here:",
        value=example_data,
        height=300,
        placeholder="Paste your JSON data or any text containing URLs here..."
    )
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_btn = st.button("🚀 Extract URLs", type="primary", use_container_width=True)
    
    if process_btn:
        if not input_text.strip():
            st.error("❌ Please enter some data to process.")
            return
            
        with st.spinner("🔄 Processing your data..."):
            try:
                # Process the data
                results = process_data(input_text)
                
                # Display results in a nice layout
                st.success("✅ Extraction completed successfully!")
                
                # Summary cards
                st.subheader("📊 Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total URLs Found", results["total_urls_found"])
                with col2:
                    st.metric("Stream URLs", results["total_stream_urls"])
                with col3:
                    st.metric("Unique Domains", results["total_unique_domains"])
                
                # Unique Domains section
                st.subheader("🌐 Unique Domains")
                if results["unique_domains"]:
                    domains_df = pd.DataFrame({
                        'Domain': results["unique_domains"]
                    })
                    st.dataframe(domains_df, use_container_width=True, hide_index=True)
                    
                    # Display as badges
                    st.write("**Quick View:**")
                    cols = st.columns(4)
                    for i, domain in enumerate(results["unique_domains"]):
                        with cols[i % 4]:
                            st.markdown(f"🔹 `{domain}`")
                else:
                    st.info("No domains found in the input data.")
                
                # Unique URLs section
                st.subheader("🔗 All Unique URLs")
                if results["unique_urls"]:
                    urls_df = pd.DataFrame({
                        'URL': results["unique_urls"]
                    })
                    st.dataframe(urls_df, use_container_width=True, hide_index=True)
                    
                    # Show count by type
                    http_urls = [url for url in results["unique_urls"] if url.startswith('http://')]
                    https_urls = [url for url in results["unique_urls"] if url.startswith('https://')]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("HTTPS URLs", len(https_urls))
                    with col2:
                        st.metric("HTTP URLs", len(http_urls))
                else:
                    st.info("No URLs found in the input data.")
                
                # Stream URLs section
                st.subheader("🎥 Stream URLs")
                if results["unique_stream_urls"]:
                    streams_df = pd.DataFrame({
                        'Stream URL': results["unique_stream_urls"]
                    })
                    st.dataframe(streams_df, use_container_width=True, hide_index=True)
                    
                    # Stream URL analysis
                    stream_domains = [extract_domain(url) for url in results["unique_stream_urls"]]
                    domain_count = pd.Series(stream_domains).value_counts()
                    
                    st.write("**Stream URLs by Domain:**")
                    for domain, count in domain_count.items():
                        st.write(f"- `{domain}`: {count} URLs")
                else:
                    st.info("No stream URLs found. Make sure your JSON has a 'streams' array.")
                
                # Export section
                st.subheader("📤 Export Results")
                
                # JSON export
                json_data = json.dumps(results, indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_data,
                    file_name=f"url_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # CSV export for URLs
                if results["unique_urls"]:
                    csv_data = pd.DataFrame({'URLs': results["unique_urls"]}).to_csv(index=False)
                    st.download_button(
                        label="📥 Download URLs as CSV",
                        data=csv_data,
                        file_name=f"urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Raw results expander
                with st.expander("📋 View Raw Results"):
                    st.json(results)
                    
            except Exception as e:
                st.error(f"❌ An error occurred during processing: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**URL Extractor Pro** • Extract URLs from any structured or unstructured data • "
        "Built with Streamlit"
    )

if __name__ == "__main__":
    main()
