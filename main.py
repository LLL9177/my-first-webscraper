import requests, sys, json, csv
from selectolax.parser import HTMLParser
from tqdm import tqdm
from urllib.parse import urljoin
from dataclasses import asdict, dataclass, fields

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
        tqdm.write(f"Error response {res.status_code} while requesting {res.url} (Pages exceeded)")
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
        rating = float(extract_text(html, "rz-product-comment-rating").split(' ')[2].replace("/5на", ''))
    except IndexError:
        rating = None

    try:
        review_count = int(extract_text(html, ".product-comment-rating__text").split(' ')[2])
    except Exception:
        review_count = 0

    item = Item(
        url=url,
        name=extract_text(html, ".title__font"),
        rating=rating,
        in_stock=True if extract_text(html, "p.status-label") == "Є в наявності" else False,
        old_price=old_price,
        price=int(extract_text(html, "p.product-price__big").replace("₴", '').replace(' ', '')),
        review_count=review_count
    )

    return item


def export_to_json(products):
    tqdm.write("Writing data to json file...")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(list(map(lambda product: asdict(product), products)), f, indent=2, ensure_ascii=False)

# def export_to_csv(products):
#     tqdm.write("Exporting to CSV...")
#     field_names = [field.name for field in fields(Item)]
#
#     with open("products.csv", 'w') as f:
#         writer = csv.DictWriter(f, field_names)
#         writer.writeheader()
#         writer.writerows(asdict(product) for product in products)

def append_to_csv(product):
    tqdm.write(f"Writing {asdict(product)["name"]} into products.csv...")
    field_names = [field.name for field in fields(Item)]

    with open("products.csv", "a") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerow(asdict(product))

def main():
    PAGES = 10
    data = []
    try:
        PAGES = int(sys.argv[1])
    except Exception:
        print(f"Missing pages command line argument. Defaulting to {PAGES} pages")

    try:
        clear_mode = sys.argv[2].lower()
        if clear_mode == "yes":
            clear_mode = True
        elif clear_mode == "no":
            clear_mode = False
        else:
            tqdm.write("Usage: python main.py [pages] [clear products.csv (yes/no)]")
    except Exception:
        tqdm.write(f"Messing clear products.csv command line argument. Defaulting to no value")
        clear_mode = False

    if clear_mode:
        with open("products.csv", "w") as f:
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
            append_to_csv(product)
            data.append(product)

    export_to_json(data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
