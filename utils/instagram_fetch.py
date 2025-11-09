# utils/instagram_fetch.py
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
from utils.selenium_fetch import fetch_with_selenium

def is_instagram_url(url):
    try:
        host = urlparse(url).netloc.lower().replace("www.", "")
        return host.endswith("instagram.com")
    except:
        return False

def parse_json_ld(soup):
    # Buscar json-ld
    script = soup.find("script", {"type": "application/ld+json"})
    if script:
        try:
            return json.loads(script.string)
        except:
            pass
    return None

def parse_shared_data(soup):
    # algunas páginas antiguas incluían window._sharedData en un <script>
    for s in soup.find_all("script"):
        if s.string and "window._sharedData" in s.string:
            try:
                start = s.string.index("window._sharedData") 
                js = s.string[s.string.index("{", start): s.string.rindex("}") + 1]
                return json.loads(js)
            except Exception:
                pass
    return None

def fetch_instagram_profile(url, headless=True, wait_seconds=2, screenshot=False):
    """
    Devuelve dict: {'username', 'full_name', 'biography', 'followers', 'following',
                     'posts_count', 'profile_pic', 'recent_posts': [ {type, url, caption}... ] }
    Nota: para posts a escala usar API oficial.
    """
    res = fetch_with_selenium(url, headless=headless, wait_seconds=wait_seconds, screenshot=screenshot)
    html = res.get("html", "")
    soup = BeautifulSoup(html, "html.parser")

    out = {
        "url": url,
        "username": None,
        "full_name": None,
        "biography": None,
        "followers": None,
        "following": None,
        "posts_count": None,
        "profile_pic": None,
        "recent_posts": []
    }

    # 1) metadata OG (útil para posts individuales)
    og_title = soup.find("meta", {"property": "og:title"})
    og_desc = soup.find("meta", {"property": "og:description"})
    og_image = soup.find("meta", {"property": "og:image"})
    if og_title and og_title.get("content"):
        out["full_name"] = og_title["content"]
    if og_desc and og_desc.get("content"):
        out["biography"] = og_desc["content"]
    if og_image and og_image.get("content"):
        out["profile_pic"] = og_image["content"]

    # 2) json-ld
    jd = parse_json_ld(soup)
    if jd:
        # estructura puede variar; probar con claves comunes
        out["username"] = jd.get("mainEntityofPage", {}).get("url") or jd.get("url")
        # otros campos:
        if isinstance(jd, dict):
            if not out["profile_pic"]:
                out["profile_pic"] = jd.get("image")
            if "description" in jd and not out["biography"]:
                out["biography"] = jd.get("description")

    # 3) window._sharedData (si existe) suele contener el graf de usuario con stats
    sd = parse_shared_data(soup)
    try:
        if sd:
            # ruta típica para perfil: entry_data -> ProfilePage -> [0] -> graphql -> user
            user = sd.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user")
            if user:
                out["username"] = user.get("username") or out["username"]
                out["full_name"] = user.get("full_name") or out["full_name"]
                out["profile_pic"] = user.get("profile_pic_url_hd") or user.get("profile_pic_url") or out["profile_pic"]
                out["biography"] = user.get("biography") or out["biography"]
                out["followers"] = user.get("edge_followed_by", {}).get("count")
                out["following"] = user.get("edge_follow", {}).get("count")
                out["posts_count"] = user.get("edge_owner_to_timeline_media", {}).get("count")
                edges = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
                for e in edges[:6]:
                    node = e.get("node", {})
                    post = {
                        "id": node.get("id"),
                        "shortcode": node.get("shortcode"),
                        "display_url": node.get("display_url"),
                        "caption": (node.get("edge_media_to_caption", {}).get("edges") or [{}])[0].get("node", {}).get("text"),
                        "is_video": node.get("is_video")
                    }
                    out["recent_posts"].append(post)
    except Exception:
        pass

    # fallback: extraer username del path si falta
    if not out["username"]:
        p = urlparse(url).path.strip("/").split("/")
        if p:
            out["username"] = p[0]

    return out
