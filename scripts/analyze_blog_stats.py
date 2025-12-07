from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt

DATA_DIR = Path("data")
OUTPUT_DIR = Path("charts")
FILE_PATTERN = "cnblogs_snapshot_*.json"

OUTPUT_DIR.mkdir(exist_ok=True)

interested_dir = OUTPUT_DIR / "interested_blogs"
interested_dir.mkdir(exist_ok=True)

if datetime.now().day != 1:
    # due to images stroage limitation, update images monthly
    print('Skipped charts generation')
    exit(0)

files = sorted(DATA_DIR.glob(FILE_PATTERN))

daily_data = {}
for f in files:
    ts_str = f.stem.replace("cnblogs_snapshot_", "")
    dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").date()
    if dt not in daily_data:
        with f.open("r", encoding="utf-8") as fp:
            daily_data[dt] = json.load(fp)

dates = sorted(daily_data.keys())

post_count = [daily_data[d]["blog_stats"]["post_count"] for d in dates]
comment_count = [daily_data[d]["blog_stats"]["comment_count"] for d in dates]
view_count = [daily_data[d]["blog_stats"]["view_count"] for d in dates]
score = [daily_data[d]["sidecolumn"]["score_rank"]["score"] for d in dates]
rank = [daily_data[d]["sidecolumn"]["score_rank"]["rank"] for d in dates]
fans = [daily_data[d]["news"]["fans"] for d in dates]
follow = [daily_data[d]["news"]["follow"] for d in dates]

def plot_series(values, ylabel, title, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o")
    plt.xticks(rotation=30)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename)
    plt.close()

plot_series(post_count, "Post Count", "Post Count Trend", "post_count.png")
plot_series(comment_count, "Comment Count", "Comment Count Trend", "comment_count.png")
plot_series(view_count, "View Count", "View Count Trend", "view_count.png")
plot_series(score, "Score", "Score Trend", "score.png")
plot_series(rank, "Rank", "Rank Trend", "rank.png")
plot_series(fans, "Fans", "Fans Trend", "fans.png")
plot_series(follow, "Follow", "Follow Trend", "follow.png")

all_posts = {}
for d in dates:
    for item in daily_data[d]["interested_blogs:"]:
        pid = item["postId"]
        if pid not in all_posts:
            all_posts[pid] = {"date": [], "view": [], "digg": [], "bury": [], "feedback": []}
        all_posts[pid]["date"].append(d)
        all_posts[pid]["view"].append(item["viewCount"])
        all_posts[pid]["digg"].append(item["diggCount"])
        all_posts[pid]["bury"].append(item["buryCount"])
        all_posts[pid]["feedback"].append(item["feedbackCount"])

for pid, data in all_posts.items():
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(data["date"], data["view"], marker="o", label="viewCount", color="tab:blue")
    ax1.set_ylabel("viewCount")
    ax1.tick_params(axis="y")

    ax2 = ax1.twinx()
    ax2.plot(data["date"], data["digg"], marker="o", linestyle="--", label="diggCount", color="tab:red")
    ax2.plot(data["date"], data["bury"], marker="o", linestyle=":", label="buryCount", color="tab:green")
    ax2.plot(data["date"], data["feedback"], marker="o", linestyle="-.", label="feedbackCount", color="tab:orange")
    ax2.set_ylabel("digg/bury/feedback")
    ax2.tick_params(axis="y")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title(f"Post {pid} Trend")
    plt.xticks(rotation=30)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(interested_dir / f"post_{pid}.png")
    plt.close()

print(f"Charts generated in: {OUTPUT_DIR}")
