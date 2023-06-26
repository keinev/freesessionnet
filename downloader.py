from sessionnet_scraper import SessionnetCrawler

crawler = Sessionnet_Crawler("RIS2_PDF/", "Dessau", "https://sessionnet.dessau.de/bi/info.asp", 2022, 1, 12, False)
crawler.start_crawl()
