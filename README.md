# My first web scraper

Since I'm still learning, this probably isn't the best scraper you'll ever see—but I'm pretty happy with how it turned out.
Feel free to add any comment, maybe push something from yourself (with explanation). I'm still into learning it.

### What is the point?

This scraper collects monitor listings from Rozetka.
I liked that the site's html has a lot of straight-forward stuff. It has classes that are human readable, custom elements, and test ids. So I didn't face anything difficult.
I didn't have to reverse-engineer any API endpoints because all the information I needed was already present in the HTML.

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
pip install -r requirements.txt
```

*Fourth step: Actual usage*

There are 2 cli arguments:

1. Pages amount: How many pages of search you want to scrape (default is 10)
2. Clear csv [yes or no]: Wether you want to clear the products.csv file before putting anything into it (default is "no")

## Features

- Scrapes monitor listings from Rozetka
- Exports to CSV
- Exports to JSON
- Progress bars with tqdm
- Configurable number of pages
- You can ask some questions to AI right in the terminal after scraping

## AI

I'm using Gemini here. You can put whatever gemini model you wish (see .env.example).
I actually did it for my Fiverr gig. But now I'm thinking of actually using this program because I can change the url whenever I want

The system prompt lays in system_prompt.txt. So you can tweak if or create your own easily.
The developer prompt is just `Here's the data: ...`. It's in the function `llm_session` if you with to change it.

## How it could be improved

No ideas