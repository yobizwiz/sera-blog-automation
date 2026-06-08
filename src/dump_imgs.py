#!/usr/bin/env python3
"""One-off: dump body-image URLs for ALL articles (published + scheduled/unpublished),
sorted by publish date, so images not yet on the public storefront can be reviewed."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import load_env, log
from repair_images import shop_req, get_blog_id

IMG = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.I)


def fetch_all_any(env, blog_id):
    arts = []
    path = (f"blogs/{blog_id}/articles.json?limit=250&published_status=any"
            f"&fields=id,title,handle,body_html,published_at")
    while path:
        data, link = shop_req(env, path)
        arts += data["articles"]
        m = re.search(r'page_info=([^&>]+)>;\s*rel="next"', link) if 'rel="next"' in link else None
        path = f"blogs/{blog_id}/articles.json?limit=250&page_info={m.group(1)}" if m else None
    return arts


def main():
    env = load_env()
    blog_id = get_blog_id(env)
    arts = fetch_all_any(env, blog_id)
    out = []
    for a in arts:
        body = a.get("body_html") or ""
        srcs = [s.split('?')[0] for s in IMG.findall(body)]
        out.append({"slug": a.get("handle"), "pub": (a.get("published_at") or "")[:10], "imgs": srcs})
    out.sort(key=lambda x: x["pub"], reverse=True)
    for a in out:
        log(f"{a['pub']} | {a['slug'][:46]:46} | {len(a['imgs'])} imgs")
    print(json.dumps({"total": len(out), "articles": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
