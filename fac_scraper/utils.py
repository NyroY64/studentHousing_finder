def clean_url(url):
    """Ensure that the URL is absolute."""
    if not url.startswith("https://www.fac-habitat.com"):
        return f"https://www.fac-habitat.com{url}"
    return url
