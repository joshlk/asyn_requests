#!/usr/bin/env python

import multiprocessing
from multiprocessing import Queue
from Queue import Full, Empty

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.spider import DefaultSpider


def _spawn_spider(queue, urls):
    responses = []

    class FetchSpider(DefaultSpider):
        name = 'fetch_spider'
        start_urls = urls

        def parse(self, response):
            responses.append(response)

    spider = FetchSpider()
    settings = Settings()
    settings.set('DOWNLOAD_HANDLERS', {'s3': None})
    crawler_process = CrawlerProcess(settings)
    crawler_process.crawl(spider)
    crawler_process.start()

    # Put into queue a bit at a time to stop deadlock due to the queue being full
    for response in responses:
        while True:
            try:
                queue.put_nowait(response)
                break
            except Full:
                pass


def fetch(urls):
    """
    Fetch a list of URLs asynchronously

    :param urls: List of URLs
    :return: List of scrapy.http.response.html.HtmlResponse
    """

    # Start in separate process as Twisted reactor cannot be started once stopped previously
    queue = Queue()
    p = multiprocessing.Process(target=_spawn_spider, args=(queue, urls))
    p.start()

    # Collect data while process is still running to prevent the queue becoming full and creating a deadlock
    responses = []
    while True:
        queue_empty = False
        try:
            response = queue.get_nowait()
            responses.append(response)
        except Empty:
            queue_empty = True

        is_dead = not p.is_alive()

        if queue_empty and is_dead:
            break

    return responses
