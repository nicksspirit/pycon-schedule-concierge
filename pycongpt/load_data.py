import httpx
import config as cfg
from bs4 import BeautifulSoup, Tag
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from slugify import slugify

http_client = httpx.Client(
    base_url=cfg.BASE_EVENT_URL,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.36"
        )
    },
    follow_redirects=True,
)


def fetch_pycon_presentations_anchors(http_client: httpx.Client):
    resp = http_client.get("2024/schedule/")
    shedule_soup = BeautifulSoup(resp.text, "html.parser")
    presentation_anchors = shedule_soup.select("div.presentation > div.title a[href]")

    return presentation_anchors


def fetch_presentation_details(http_client: httpx.Client, anchor: Tag):
    href = anchor["href"]
    resp = http_client.get(href)
    file_name = slugify(anchor.text.strip()) + ".txt"

    return file_name, resp.text


def main():
    futures = []

    with ThreadPoolExecutor(3) as pool:
        for anchor in fetch_pycon_presentations_anchors(http_client):
            futures.append(
                pool.submit(
                    fetch_presentation_details,
                    http_client=http_client,
                    anchor=anchor,
                )
            )

        for future in tqdm(as_completed(futures), total=len(futures)):
            file_name, presentation_detail_html = future.result()
            pres_detail_soup = BeautifulSoup(presentation_detail_html, "html.parser")
            content = pres_detail_soup.select_one("main.content").text.strip()
            with open(cfg.DATA_DIR / "pycon-2024-schedule" / file_name, "w") as f:
                f.write(content)


if __name__ == "__main__":
    main()
