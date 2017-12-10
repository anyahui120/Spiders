import scrapy
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field

class EdxItem(Item):
    name = Field()
    about = Field()
    instructor = Field()
    school = Field()
    courseCode = Field()
    startDate = Field()
    url = Field()
    length = Field()
    effort = Field()
    prereqs = Field()
    video = Field()
    category = Field()

class EdXSpider(CrawlSpider):
    name = "edx"
    allowed_domains = ["edx.org"]
    start_urls = ["https://www.edx.org/course/?course=all",]


    rules = (Rule (SgmlLinkExtractor(allow=("", ),)
    , callback="parse_sites", follow= True),
    )

    def parse_sites(self, response):
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)
        sel = Selector(response)
        sites = sel.xpath('//*[@id="search-results-section"]/div[3]/div[1]/div/a/@href').extract() # course-list-all //*[@id="search-results-section"]/div[3]/div[1]/div/a
        # sites = sel.xpath('//strong/a/@href').extract()
        # sites.pop(0) # remove home directory link

        requests = []
        for site in sites:
            # site = "https://edx.org/" + site
            item = EdxItem()
            item['url'] = site
            item['category'] = response.request.url.split("/")[5]
            request = scrapy.Request(site, callback=self.parse_details)
            request.meta['item'] = item
            requests.append(request)
        return requests


    def parse_details(self, response):
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)
        sel = Selector(response)
        # print sel
        item = response.meta['item'] #/html/head/script[19]/text()
        item['name'] = sel.xpath('/html/head/meta[20]/@content').extract() #/html/head/title
        item['about'] = sel.xpath('//*[@id="course-about-area"]/div[1]/div/div/text()').extract() #//*[@id="course-about-area"]/div[1]/div/div
        item['instructor'] = sel.xpath('//*[@id="course-about-area"]/ul/li[1]/a/p/text()').extract() #//*[@id="course-about-area"]/ul/li[1]/a/p
        item['school'] = sel.xpath('//*[@id="course-summary-area"]/ul/li[4]/span[2]/a/text()').extract() #
        # item['courseCode'] = sel.xpath('//*[@class="course-detail-number item"]/text()').extract()
        item['courseCode'] = ''
        item['startDate'] = sel.xpath('//*[@id="course-info-page"]/header/div/div/div[3]/div/div/div[1]/span/text()').extract() #
        item['length'] = sel.xpath('//*[@id="course-summary-area"]/ul/li[1]/span[2]/text()').extract() #
        item['effort'] = sel.xpath('//*[@id="course-summary-area"]/ul/li[2]/span[2]/text()').extract()
        item['prereqs'] = sel.xpath('//*[@id="course-summary-area"]/div[2]/p/text()').extract()#
        item['video'] = sel.xpath('/html/head/meta[9]/@content').extract()
        yield item