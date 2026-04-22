"""skills/web_ops.py — Web operations"""
import webbrowser, urllib.parse

class WebOps:
    def search(self, query: str) -> str:
        for p in ["search for","google","look up","search"]:
            if p in query.lower():
                term = query.lower().split(p,1)[-1].strip(); break
        else:
            term = query.strip()
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(term)}")
        return f"Searching for '{term}'."

    def open_site(self, query: str) -> str:
        for p in ["open","go to","visit","launch website"]:
            if p in query.lower():
                site = query.lower().split(p,1)[-1].strip(); break
        else:
            site = query.strip()
        if not site.startswith("http"):
            site = "https://" + site
        webbrowser.open(site)
        return f"Opening {site}."

    def open_youtube(self, query: str) -> str:
        if "search" in query.lower() or "play" in query.lower():
            for p in ["search youtube for","play on youtube","youtube search","youtube"]:
                if p in query.lower():
                    term = query.lower().split(p,1)[-1].strip()
                    webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(term)}")
                    return f"Searching YouTube for '{term}'."
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
