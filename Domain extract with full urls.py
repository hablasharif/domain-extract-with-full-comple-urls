import streamlit as st
import json
import re
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os

def extract_urls(obj):
    """Recursively extract all URLs from a nested dictionary, list, or string."""
    urls = []

    if isinstance(obj, dict):
        for value in obj.values():
            urls.extend(extract_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            url.extend(extract_urls(item))
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

def get_url_info(url):
    """Extract title, meta description, and check if URL exists."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        
        title = "N/A"
        meta_description = "N/A"
        status = response.status_code
        exists = status != 404
        
        if status == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()[:100] + "..." if len(title_tag.get_text().strip()) > 100 else title_tag.get_text().strip()
            
            # Extract meta description
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc_tag:
                meta_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            
            if meta_desc_tag and meta_desc_tag.get('content'):
                meta_description = meta_desc_tag.get('content').strip()[:150] + "..." if len(meta_desc_tag.get('content').strip()) > 150 else meta_desc_tag.get('content').strip()
        
        return {
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "status_code": status,
            "exists": exists
        }
    except Exception as e:
        return {
            "url": url,
            "title": "Error fetching",
            "meta_description": f"Error: {str(e)}",
            "status_code": "Error",
            "exists": False
        }

def generate_html_report(urls_data, filename):
    """Generate a beautiful HTML report with URL information."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Extraction Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #eaeaea;
            }}
            .header h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .summary {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            .url-card {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                background: white;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .url-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .url-header {{
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .url-link {{
                font-size: 16px;
                font-weight: bold;
                color: #1a73e8;
                text-decoration: none;
                flex-grow: 1;
            }}
            .url-link:hover {{
                text-decoration: underline;
            }}
            .status-badge {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status-200 {{ background: #d4edda; color: #155724; }}
            .status-404 {{ background: #f8d7da; color: #721c24; }}
            .status-error {{ background: #fff3cd; color: #856404; }}
            .status-other {{ background: #cce7ff; color: #004085; }}
            .title {{
                font-weight: 600;
                color: #2c3e50;
                margin: 10px 0 5px 0;
            }}
            .description {{
                color: #666;
                font-size: 14px;
                line-height: 1.4;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-200 {{ color: #28a745; }}
            .stat-404 {{ color: #dc3545; }}
            .stat-error {{ color: #ffc107; }}
            .stat-label {{
                font-size: 0.9em;
                color: #666;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eaeaea;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔗 URL Extraction Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Report Summary</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(urls_data)}</div>
                        <div class="stat-label">Total URLs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number stat-200">{len([u for u in urls_data if u.get('status_code') == 200])}</div>
                        <div class="stat-label">Working URLs (200)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number stat-404">{len([u for u in urls_data if u.get('status_code') == 404])}</div>
                        <div class="stat-label">Broken URLs (404)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number stat-error">{len([u for u in urls_data if u.get('status_code') == 'Error'])}</div>
                        <div class="stat-label">Error URLs</div>
                    </div>
                </div>
            </div>
            
            <h2>🔗 Extracted URLs</h2>
    """
    
    for url_info in urls_data:
        status_class = f"status-{url_info['status_code']}" if url_info['status_code'] != 'Error' else "status-error"
        if url_info['status_code'] not in [200, 404, 'Error']:
            status_class = "status-other"
        
        html_content += f"""
            <div class="url-card">
                <div class="url-header">
                    <a href="{url_info['url']}" class="url-link" target="_blank">{url_info['url']}</a>
                    <span class="status-badge {status_class}">
                        {f"Status: {url_info['status_code']}" if url_info['status_code'] != 'Error' else 'Error'}
                    </span>
                </div>
                <div class="title">📝 Title: {url_info['title']}</div>
                <div class="description">📋 Description: {url_info['meta_description']}</div>
            </div>
        """
    
    html_content += """
            <div class="footer">
                <p>Generated by URL Extractor Pro • Powered by Streamlit</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

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
        - ✅ Get page titles & meta descriptions
        - ✅ Check URL status (404 detection)
        - ✅ Generate beautiful HTML reports
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
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            fetch_details = st.checkbox("Fetch URL details", value=True, 
                                       help="Extract page titles, meta descriptions, and check URL status")
        with col2:
            parallel_processing = st.checkbox("Parallel processing", value=False,
                                            help="Process multiple URLs simultaneously (faster but more resource intensive)")
    
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
                
                # Fetch URL details if enabled
                url_details = []
                if fetch_details and results["unique_urls"]:
                    st.info("🌐 Fetching URL details (this may take a while for many URLs)...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, url in enumerate(results["unique_urls"]):
                        status_text.text(f"Processing URL {i+1}/{len(results['unique_urls'])}: {url[:50]}...")
                        url_info = get_url_info(url)
                        url_details.append(url_info)
                        progress_bar.progress((i + 1) / len(results["unique_urls"]))
                    
                    status_text.text("✅ URL details fetched successfully!")
                    
                    # Display URL details in a dataframe
                    st.subheader("📄 URL Details")
                    if url_details:
                        details_df = pd.DataFrame(url_details)
                        st.dataframe(details_df, use_container_width=True)
                        
                        # Status summary
                        st.subheader("📈 Status Summary")
                        status_counts = details_df['status_code'].value_counts()
                        cols = st.columns(len(status_counts))
                        
                        for idx, (status, count) in enumerate(status_counts.items()):
                            with cols[idx % len(cols)]:
                                if status == 200:
                                    st.metric("Working URLs", count, delta=f"{count/len(url_details)*100:.1f}%")
                                elif status == 404:
                                    st.metric("Broken URLs", count, delta=f"{count/len(url_details)*100:.1f}%", delta_color="inverse")
                                else:
                                    st.metric(f"Status {status}", count)
                
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
                
                col1, col2, col3 = st.columns(3)
                
                # JSON export
                with col1:
                    json_data = json.dumps(results, indent=2)
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_data,
                        file_name=f"url_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                # CSV export for URLs
                with col2:
                    if results["unique_urls"]:
                        csv_data = pd.DataFrame({'URLs': results["unique_urls"]}).to_csv(index=False)
                        st.download_button(
                            label="📥 Download URLs as CSV",
                            data=csv_data,
                            file_name=f"urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                # HTML Report export
                with col3:
                    if url_details:
                        html_filename = f"url_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                        generate_html_report(url_details, html_filename)
                        
                        with open(html_filename, 'rb') as f:
                            html_data = f.read()
                        
                        st.download_button(
                            label="📊 Download HTML Report",
                            data=html_data,
                            file_name=html_filename,
                            mime="text/html",
                            use_container_width=True
                        )
                        
                        # Clean up temporary file
                        try:
                            os.remove(html_filename)
                        except:
                            pass
                
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
