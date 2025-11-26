import requests
import json
from datetime import datetime, UTC
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://www.cnblogs.com/XuYueming/ajax"
OUTPUT_PATH = Path("data")
INTERESTED_BLOGS = [18313014, 18397758]


def fetch_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def extract_int_by_id(soup: BeautifulSoup, element_id: str) -> int:
    el = soup.find(id=element_id)
    if not el:
        return 0
    text = el.get_text(strip=True)
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def fetch_blog_info(blog_ids: list[int]) -> dict:
    resp = requests.post(f'{BASE_URL}/GetPostStat',
                         data=json.dumps(blog_ids),
                         headers={"Content-Type": "application/json; charset=utf-8"})
    resp.raise_for_status()
    return resp.json()


def fetch_blog_stats() -> dict:
    soup = fetch_html(f"{BASE_URL}/blog-stats")
    return {
        "post_count": extract_int_by_id(soup, "stats_post_count"),
        "article_count": extract_int_by_id(soup, "stats_article_count"),
        "comment_count": extract_int_by_id(soup, "stats-comment_count"),
        "view_count": extract_int_by_id(soup, "stats-total-view-count"),
    }


def fetch_news() -> dict:
    soup = fetch_html(f"{BASE_URL}/news")
    profile_div = soup.find(id="profile_block")
    if not profile_div:
        return {"nickname": "", "join_age": "", "fans": 0, "follow": 0}

    a_tags = profile_div.find_all("a")
    nickname = a_tags[0].get_text(strip=True) if len(a_tags) > 0 else ""
    join_age = a_tags[1].get_text(strip=True) if len(a_tags) > 1 else ""

    fans_tag = profile_div.find("a", class_="follower-count")
    fans = int(fans_tag.get_text(strip=True)) if fans_tag and fans_tag.get_text(
        strip=True).isdigit() else 0

    follow_tag = profile_div.find("a", class_="folowing-count")
    follow = int(follow_tag.get_text(
        strip=True)) if follow_tag and follow_tag.get_text(strip=True).isdigit() else 0

    return {
        "nickname": nickname,
        "join_age": join_age,
        "fans": fans,
        "follow": follow
    }


def fetch_sidecolumn() -> dict:
    soup = fetch_html(f"{BASE_URL}/sidecolumn.aspx")
    data = {}

    # recent_posts = []
    # ul = soup.select_one("#sidebar_recentposts ul")
    # if ul:
    #     for li in ul.find_all("li"):
    #         a = li.find("a")
    #         if a:
    #             recent_posts.append({"title": a.get_text(strip=True), "link": a.get("href")})
    # data["recent_posts"] = recent_posts

    # tags = []
    # ul = soup.select_one("#sidebar_toptags ul")
    # if ul:
    #     for li in ul.find_all("li"):
    #         a = li.find("a")
    #         if a and "更多" not in a.get_text():
    #             count_span = li.find("span", class_="tag-count")
    #             count = int(count_span.get_text(
    #                 strip=True).strip("()")) if count_span else 0
    #             tags.append({
    #                 "name": a.get_text(strip=True).replace(f"({count})", ""),
    #                 "count": count,
    #                 # "link": a.get("href")
    #             })
    # data["tags"] = tags

    # collections = []
    # for div in soup.select("#sidebar_categories .catList"):
    #     title = div.select_one(".catListTitle")
    #     if title:
    #         title_text = title.get_text(strip=True).split("(")[0]
    #         items = []
    #         for a in div.select("ul li a"):
    #             items.append({"name": a.get_text(strip=True), "link": a.get("href")})
    #         collections.append({"title": title_text, "items": items})
    # data["collections"] = collections

    # archives = []
    # archive_div = soup.select_one("#sidebar_postarchive ul")
    # if archive_div:
    #     for a in archive_div.find_all("a"):
    #         archives.append({"name": a.get_text(strip=True), "link": a.get("href")})
    # data["archives"] = archives

    # recent_comments = []
    # comment_block = soup.select_one("#sidebar_recentcomments .RecentCommentBlock ul")
    # if comment_block:
    #     items = comment_block.find_all(recursive=False)
    #     for i in range(0, len(items), 3):
    #         title_li = items[i]
    #         body_li = items[i + 1] if i + 1 < len(items) else None
    #         author_li = items[i + 2] if i + 2 < len(items) else None
    #         if title_li and body_li and author_li:
    #             a = title_li.find("a")
    #             title = a.get_text(strip=True) if a else ""
    #             link = a.get("href") if a else ""
    #             content = body_li.get_text(strip=True)
    #             author = author_li.get_text(strip=True).lstrip("--")
    #             recent_comments.append({"title": title, "link": link, "content": content, "author": author})
    # data["recent_comments"] = recent_comments

    score_rank = {}
    ul = soup.select_one("#sidebar_scorerank ul")
    if ul:
        score_li = ul.find("li", class_="liScore")
        rank_li = ul.find("li", class_="liRank")
        score = int("".join(ch for ch in score_li.get_text()
                    if ch.isdigit())) if score_li else 0
        rank = int("".join(ch for ch in rank_li.get_text()
                   if ch.isdigit())) if rank_li else 0
        score_rank = {"score": score, "rank": rank}
    data["score_rank"] = score_rank

    return data


def main():
    snapshot = {
        "fetched_at": datetime.now(UTC).isoformat() + "Z",
        "blog_stats": fetch_blog_stats(),
        "news": fetch_news(),
        "sidecolumn": fetch_sidecolumn(),
        "interested_blogs:": fetch_blog_info(INTERESTED_BLOGS)
    }

    OUTPUT_PATH.mkdir(exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_PATH / f"cnblogs_snapshot_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print("blog snapshot saved:", output_file)


if __name__ == "__main__":
    main()
