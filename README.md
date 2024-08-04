First make sure the driver is on the path
```
export PATH=$PATH:/Users/remy/Code/patent-scraper
```

Then call the crawler
```
python crawler.py
```

Let the driver load, then set the language to English and continue.

Then login, and go to the crawler terminal and hit enter.

TODO:
The crawler downloads the html on each subpage of the patent registry. We still need to parse the downloaded html, grabbing text from the downloaded files, resolving any paths to images or pdfs to their canonical urls and download those as well.

We also need to automate logging in.
