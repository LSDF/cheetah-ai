from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import whois
import dns.resolver
import httpx

app = FastAPI(title="Cheetah Cyber", version="1.0.0")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

DISCLAIMER = "This platform is for educational purposes only. All tools and challenges use publicly available information or simulated environments. Users are fully responsible for complying with all laws."

# ====================== PAGES ======================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Cheetah Cyber - Learn Ethical Hacking & Cybersecurity",
        "description": "Free cybersecurity learning platform with ethical hacking challenges, OSINT tools, and study materials. Practice legally and improve your skills."
    })

@app.get("/learn", response_class=HTMLResponse)
async def learn(request: Request):
    return templates.TemplateResponse("learn.html", {
        "request": request,
        "title": "Learn Cybersecurity - Cheetah Cyber",
        "description": "Structured cybersecurity learning paths covering networking, web security, OSINT, cryptography, and ethical hacking fundamentals."
    })

@app.get("/challenges", response_class=HTMLResponse)
async def challenges(request: Request):
    return templates.TemplateResponse("challenges.html", {
        "request": request,
        "title": "Hacking Challenges & CTF Practice - Cheetah Cyber",
        "description": "Practice ethical hacking with beginner to intermediate challenges in OSINT, web security, cryptography, and more."
    })

@app.get("/osint", response_class=HTMLResponse)
async def osint_page(request: Request):
    return templates.TemplateResponse("osint.html", {
        "request": request,
        "title": "OSINT Tools - Public Information Search - Cheetah Cyber",
        "description": "Free OSINT tools for username search, WHOIS, DNS, and IP lookup. Public information only."
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "title": "About Cheetah Cyber - Educational Cybersecurity Platform",
        "description": "Cheetah Cyber is an educational platform for learning ethical hacking, cybersecurity, and OSINT using only legal methods."
    })

# ====================== OSINT API ======================

@app.get("/api/username")
async def api_username(q: str = Query(..., min_length=2, max_length=40)):
    platforms = {
        "GitHub": f"https://github.com/{q}",
        "Twitter/X": f"https://x.com/{q}",
        "Instagram": f"https://www.instagram.com/{q}/",
        "Reddit": f"https://www.reddit.com/user/{q}",
        "TikTok": f"https://www.tiktok.com/@{q}",
        "YouTube": f"https://www.youtube.com/@{q}",
        "LinkedIn": f"https://www.linkedin.com/in/{q}",
        "Twitch": f"https://www.twitch.tv/{q}",
    }
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CheetahCyber/1.0)"}
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=headers) as client:
        for name, url in platforms.items():
            try:
                resp = await client.get(url)
                status = "Not Found" if resp.status_code == 404 else "Found / Possible"
                results.append({"platform": name, "url": url, "status": status, "code": resp.status_code})
            except:
                results.append({"platform": name, "url": url, "status": "Error", "code": None})
    return {"username": q, "results": results, "disclaimer": DISCLAIMER}

@app.get("/api/whois")
def api_whois(domain: str = Query(...)):
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": str(getattr(w, "registrar", None)),
            "creation_date": str(getattr(w, "creation_date", None)),
            "expiration_date": str(getattr(w, "expiration_date", None)),
            "name_servers": list(w.name_servers) if w.name_servers else [],
            "disclaimer": DISCLAIMER
        }
    except Exception as e:
        return {"domain": domain, "error": str(e), "disclaimer": DISCLAIMER}

@app.get("/api/dns")
def api_dns(domain: str = Query(...)):
    records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(r) for r in answers]
        except:
            records[rtype] = []
    return {"domain": domain, "records": records, "disclaimer": DISCLAIMER}

@app.get("/api/ip")
async def api_ip(ip: str = Query(...)):
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
            data = resp.json() if resp.status_code == 200 else {}
            return {
                "ip": ip,
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "org": data.get("org"),
                "asn": data.get("asn"),
                "disclaimer": DISCLAIMER
            }
    except Exception as e:
        return {"ip": ip, "error": str(e), "disclaimer": DISCLAIMER}
