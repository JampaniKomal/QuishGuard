import requests
import re
from urllib.parse import urlparse
from defang import defang

class URLAnalyzer:
    def analyze(self, qr_data):
        # 1. Basic Validation
        if not qr_data:
            return {"status": "error", "message": "Empty Data"}
            
        # Check if it looks like a URL
        if not (qr_data.startswith("http://") or qr_data.startswith("https://")):
            return {
                "status": "info",
                "type": "Text",
                "original": defang(qr_data),
                "verdict": "SAFE",
                "score": 0,
                "flags": ["Plain Text Content"]
            }

        # 2. Unshortening
        chain, connection_failed = self.trace_redirects(qr_data)
        final_url = chain[-1] if chain else qr_data

        # 3. Heuristic Analysis (The Verdict)
        verdict, score, flags = self.calculate_threat_score(final_url, chain, connection_failed)

        safe_final_url = defang(final_url)
        
        return {
            "status": "success",
            "type": "URL",
            "original": defang(qr_data),
            "final": safe_final_url,
            "chain": chain,
            "domain": urlparse(final_url).netloc,
            "verdict": verdict, # NEW
            "score": score,     # NEW
            "flags": flags      # NEW
        }

    def trace_redirects(self, url):
        """Returns (history, connection_failed). connection_failed is True if
        the destination could not be reached at all (timeout, DNS failure,
        connection refused, etc.) - this is distinct from a clean HTTP
        response and must not be treated as equivalent to a verified-safe
        destination."""
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        history = [url]
        current_url = url
        for _ in range(10):
            try:
                response = session.head(current_url, headers=headers, allow_redirects=False, timeout=5)
                if 300 <= response.status_code < 400:
                    next_url = response.headers.get('Location')
                    if not next_url: break
                    if next_url.startswith('/'):
                        parsed = urlparse(current_url)
                        next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                    history.append(next_url)
                    current_url = next_url
                else: break
            except requests.exceptions.RequestException:
                return history, True
        return history, False

    def calculate_threat_score(self, url, chain, connection_failed=False):
        """
        0-2: Safe
        3-5: Suspicious
        6+: High Risk
        """
        score = 0
        flags = []
        parsed = urlparse(url)

        # Check 0: Could not verify the destination at all. This must never
        # be scored as equivalent to a confirmed-clean response - phishing
        # infrastructure is often short-lived or blocks automated scanners.
        if connection_failed:
            score += 3
            flags.append("Could not verify destination (connection failed, timed out, or refused)")

        # Check 1: Redirection Depth
        if len(chain) > 2:
            score += 2
            flags.append(f"Deep Redirection Chain ({len(chain)} hops)")
            
        # Check 2: IP Address Hostname (e.g., http://192.168.1.1/login)
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", parsed.netloc):
            score += 5
            flags.append("Destination is a Raw IP Address")

        # Check 3: Suspicious Keywords
        sus_keywords = ["login", "verify", "update", "secure", "account", "banking", "free"]
        for word in sus_keywords:
            if word in url.lower():
                score += 1
                flags.append(f"Suspicious Keyword: '{word}'")

        # Check 4: File Extensions
        if url.lower().endswith(('.exe', '.zip', '.scr', '.apk')):
            score += 5
            flags.append("Direct File Download Detected")

        # Verdict Logic
        if not flags:
            flags.append("Clean URL Structure")

        if score >= 5:
            return "HIGH RISK", score, flags
        elif score >= 2:
            return "SUSPICIOUS", score, flags
        else:
            return "SAFE", score, flags