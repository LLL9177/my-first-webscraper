import requests
import sys
import json
import csv
import os
from selectolax.parser import HTMLParser
from tqdm import tqdm
from urllib.parse import urljoin
from dataclasses import asdict, dataclass, fields
from google import genai
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Item:
    url: str | None
    name: str | None
    review_count: int | None
    in_stock: bool | None
    old_price: int | None
    price: int | None
    rating: float | None


BASE_URL = "https://hard.rozetka.com.ua"


def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0"
    }

    res = requests.get(url, headers=headers)
    html = HTMLParser(res.text)

    if not res.ok:
        tqdm.write(f"Error response {res.status_code} while requesting {
                   res.url} (Pages exceeded)")
        return False

    return html


def extract_text(html, selector):
    try:
        return html.css_first(selector).text().strip().replace("\xa0", ' ')
    except AttributeError:
        return None


def extract_image(html, selector):
    try:
        return html.css_first(selector).attributes["src"]
    except AttributeError:
        return None


def extract_url(html):
    try:
        return html.css_first("a.tile-image-host").attributes["href"]
    except AttributeError:
        return None


def parse_search_page(html):
    url_arr = []
    products = html.css("rz-product-tile")

    for product in products:
        item = {
            "url": extract_url(product),
            "name": extract_text(product, ".tile-title")
        }

        if item["url"] is None:
            tqdm.write(f"Url for {item["name"]} was not found")
            return 1

        url_arr.append(item["url"])

    return url_arr


def parse_product_page(html, url):
    old_price = extract_text(html, "p.product-price__small")
    if old_price is not None:
        old_price = int(old_price.replace(' ', '').replace('₴', ''))

    try:
        rating = float(extract_text(
            html, "rz-product-comment-rating").split(' ')[2].replace("/5на", ''))
    except IndexError:
        rating = None

    try:
        review_count = int(extract_text(
            html, ".product-comment-rating__text").split(' ')[2])
    except Exception:
        review_count = 0

    item = Item(
        url=url,
        name=extract_text(html, "rz-title-block h1"),
        rating=rating,
        in_stock=True if extract_text(
            html, "p.status-label") == "Є в наявності" else False,
        old_price=old_price,
        price=int(extract_text(
            html, "p.product-price__big").replace("₴", '').replace(' ', '')),
        review_count=review_count
    )

    return item


def export_to_json(products):
    tqdm.write("Writing data to json file...")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(list(map(lambda product: asdict(product), products)),
                  f, indent=2, ensure_ascii=False)

def append_to_json(product):
    product_name = asdict(product)["name"]
    if len(product_name) > 20:
        product_name = product_name[:20] + "..."
    
    tqdm.write(f"Writing {product_name} into data.json...")
    data = []
    with open("data.json", "r", encoding="utf-8") as f:
        content = f.read()
        try:
            if content.strip() != "":
                data = json.loads(content)
        except Exception as e:
            tqdm.write(str(e))
            return 1

    data.append(asdict(product))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        

def append_to_csv(product):
    product_name = asdict(product)["name"]
    if len(product_name) > 20:
        product_name = product_name[:20] + "..."

    tqdm.write(f"Writing {product_name} into products.csv...")
    field_names = [field.name for field in fields(Item)]
    write_header = False

    with open("products.csv", "r") as f:
        if f.read().strip() == "":
            write_header = True

    with open("products.csv", "a") as f:
        writer = csv.DictWriter(f, field_names)
        if write_header: 
            writer.writeheader()
            
        writer.writerow(asdict(product))

def llm_session(file):
    data = []

    with open(file, "r", encoding="utf-8") as f:
        if ".csv" in file:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        elif ".json" in file:
            data = json.load(f)

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-3.1-flash-lite")
    system_prompt = ""
    developer_prompt = f"Here's the data: \n{data}"

    with open("system_prompt.txt", 'r') as f:
        system_prompt = f.read()

    print("To finish chatting, press CTRL + C")
    while True:
        user_input = input('> ')
        resp = chat.send_message(system_prompt + developer_prompt + user_input).text
        print
        for line in resp.split('\n'):
            print(f"| {line}")
        print


def main():
    PAGES = 10
    data = []
    usage_text = "Usage: python main.py [pages] [clear output file (yes/no)] [mode (json/csv)]"

    try:
        PAGES = int(sys.argv[1])
    except Exception:
        print(f"Missing pages command line argument. Defaulting to {
              PAGES} pages")

    try:
        clear_mode = sys.argv[2].lower()
        if clear_mode == "yes":
            clear_mode = True
        elif clear_mode == "no":
            clear_mode = False
        else:
            tqdm.write(usage_text)
    except Exception:
        tqdm.write(
            f"Missing clear output file command line argument. Defaulting to no.")
        clear_mode = False

    try:
        file_mode = sys.argv[3].lower()

        if file_mode == "json":
            file = "data.json"
        elif file_mode == "csv":
            file = "products.csv"
        else:
            tqdm.write(usage_text)
            return

    except Exception:
        tqdm.write(
            "Missing file mode command line argument. Defaulting to csv."
        )
        file = "products.csv"

    if clear_mode:
        with open(file, "w") as f:
            f.write('')

    url = "https://hard.rozetka.com.ua/ua/monitors/c80089/page="
    print(f"Scraping {PAGES} pages from {BASE_URL}\n")

    for i in tqdm(range(1, PAGES + 1), desc="Pages"):
        html = get_html(url + str(i))
        if html is False:
            return 1

        urls = parse_search_page(html)

        for url in tqdm(urls, desc="Products"):
            html = get_html(url)
            product = parse_product_page(html, url)
            if file == "data.json":
                if append_to_json(product) == 1:
                    tqdm.write("Invalid json format in data.json.")
                    return
            elif file == "products.csv":
                append_to_csv(product)
            
            data.append(product)

    llm_session(file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
