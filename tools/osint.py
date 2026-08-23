import whois
import dns.resolver
import httpx
from datetime import datetime
from typing import Dict, Any, List

# ====================== LEGAL DISCLAIMER ======================
DISCLAIMER = """
⚠️ LEGAL NOTICE
This tool only uses publicly available information.
You are solely responsible for ensuring your use complies with all applicable laws.
Do not use this tool for stalking, harassment, doxxing, or any illegal purpose.
"""

async def username_search(username: str) -> Dict[str, Any]:
    """Check public presence of a username across popular platforms."""
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter/X": f"https://x.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Medium": f"https://medium.com/@{username}",
    }

    results = []
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        for name, url in platforms.items():
            try:
                resp = await client.head(url)
                # Simple check - many platforms return 200 even for non-existing,
                # so we treat 404 as not found, others as "possible"
                exists = resp.status_code != 404
                results.append({
                    "platform": name,
                    "url": url,
                    "status": "Found" if exists else "Not Found",
                    "http_code": resp.status_code
                })
            except Exception:
                results.append({
                    "platform": name,
                    "url": url,
                    "status": "Error / Timeout",
                    "http_code": None
                })

    return {
        "username": username,
        "results": results,
        "disclaimer": DISCLAIMER
    }


def domain_whois(domain: str) -> Dict[str, Any]:
    """Public WHOIS lookup."""
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": str(w.registrar) if w.registrar else None,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "name_servers": w.name_servers if w.name_servers else [],
            "status": w.status if w.status else [],
            "emails": w.emails if w.emails else [],
            "org": str(w.org) if w.org else None,
            "country": str(w.country) if w.country else None,
            "disclaimer": DISCLAIMER
        }
    except Exception as e:
        return {"domain": domain, "error": str(e), "disclaimer": DISCLAIMER}


def dns_lookup(domain: str) -> Dict[str, Any]:
    """Public DNS records."""
    records = {}
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(r) for r in answers]
        except Exception:
            records[rtype] = []

    return {
        "domain": domain,
        "records": records,
        "disclaimer": DISCLAIMER
    }


async def ip_info(ip: str) -> Dict[str, Any]:
    """Basic public IP information (using free public API)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "ip": ip,
                    "city": data.get("city"),
                    "region": data.get("region"),
                    "country": data.get("country_name"),
                    "org": data.get("org"),
                    "asn": data.get("asn"),
                    "timezone": data.get("timezone"),
                    "disclaimer": DISCLAIMER
                }
            return {"ip": ip, "error": "Could not fetch data", "disclaimer": DISCLAIMER}
    except Exception as e:
        return {"ip": ip, "error": str(e), "disclaimer": DISCLAIMER}
