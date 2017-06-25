# vlive-downloader

Flask based vlive.tv video &amp; subtitle scraper

## Dependencies
    python2.7

## How to run
    pip install -r requirements.txt
    python vlive-downloader.py

## Docker:
    docker pull lippylee/vlive-downloader
    docker run -d -p 5000:5000 -name vlive-downloader lippylee/vlive-downloader

Or you can build it on your own with

    docker build -t vlive-downloader .

### To access the scraper
Open [http://localhost:5000](http://localhost:5000) in your favorite browser and enjoy.

### Changing port
Change the line `app.run()` to `app.run(port = 80)` or your port of choice.
