# My first web scraper

Since i've been just learning it might not come out as the best one. But in my opinion it's pretty darn good.
Feel free to add any comment, maybe push something from yourself (with explanation). I'm still into learning it.

### What is the point?

This scraper collects monitor listings from Rozetka.
I liked that the site's html has a lot of straight-forward stuff. It has classes that are human readable, custom elements, and test ids. So I didn't face anything difficult.
I didn't even have to send requests to backend to recieve some data. All the important stuff was in the html document.

Now It's the learning project. Because I love making something real (maybe not *that* real) while learning. It seems a fun and a productive way to learn

### Usage

*First step: Initialize .venv*
```sh
python -m venv .venv
```

Or a cool name like
```sh
python -m venv .very-cool-name-Like-seriously-cool-name
```

Nah, I'm kidding

*Second step: Open it*

```sh
source .venv/bin/activate
```

```sh
source .very-cool-name-Like-seriously-cool-name/bin/activate
```

(If you are on windows, well...............)

*Third step: Install dependencies*
```sh
pip install -r requiremente.txt
```

*Fourth step: Actuall usage*

There are 2 cli arguments:

1. Pages amount: How many pages of search you want to scrape (default is 10)
2. Clear csv [yes or no]: Wether you want to clear the products.csv file before putting anything into it (default is "no")


## How it could be improved
The only thing I could think of is doing the same to JSON file as I did to CSV file