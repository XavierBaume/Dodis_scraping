#!/usr/bin/env python
# coding: utf-8

# In[1]:


import scrapy
from scrapy.crawler import CrawlerProcess
import json


# In[2]:


class DodisSpider(scrapy.Spider):
    name = "dodis"
    start_urls = [f"https://dodis.ch/{str(i).zfill(5)}" for i in range(10000, 11000)]

    def parse(self, response):
        # Fonction pour nettoyer et formater les chaînes de caractères
        def clean_text(text):
            if text:
                return " ".join(text.split()).strip()
            return ""

        # Fonction pour extraire les données avec une valeur par défaut
        def extract_with_default(selector, default=""):
            result = selector.get()
            return clean_text(result) if result else default

        document = {
            'digital_id': response.xpath("//meta[@itemprop='url']/@content").re_first(r'(\d+)$') or "",
            'language_code': extract_with_default(response.xpath("//meta[@itemprop='inLanguage']/@content")),
            'publication_date': extract_with_default(response.xpath("//meta[@itemprop='datePublished']/@content")),
            'type_document': extract_with_default(response.css(".document-detail-type::text")),
            'summary': extract_with_default(response.css(".document-detail-summary::text")),
            'reference': extract_with_default(response.css(".document-details-dossier-reference a::text")),
            'if_published_publication_details': extract_with_default(response.xpath("normalize-space(//meta[@name='DC.description']/@content)")),
            'if_published_volume_reference': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r'\bBd\. \d{4}\b') or "",
            'if_published_volume_reference_noDoc': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r"(Dok\. \d+)") or "",
            'if_published_volume_link': extract_with_default(response.css(".documents-volume-icon::attr(href)")),
            'related_to_dodis_docs': response.css(".searchResult a::text").getall(),
        }

        tags = {
            'document_tags': response.xpath("//meta[@name='DC.subject']/@content").get("").split("; "),
        }

        persons = {
            'author_person': extract_with_default(response.css("#anc_pau .tag::text")),
            'signatory_person': extract_with_default(response.css("#anc_ps .tag::text")),
            'recipient_person': extract_with_default(response.css("#anc_pad .tag::text")),
            'other_persons_mentioned': response.css("#anc_pm .tag::text").getall(),
        }

        organizations = {
            'author_organization': extract_with_default(response.css("#anc_oau .tag::text")),
            'recipient_organization': extract_with_default(response.css("#anc_oad .tag::text")),
            'other_organizations_mentioned': response.css("#anc_om .tag::text").getall(),
        }

        geographic_nouns = {
            'geo_nouns_mentioned': response.css("#anc_plm .tag::text").getall(),
        }

        locations_archives = {
            'recipient_location': extract_with_default(response.xpath("//meta[@name='DC.coverage']/@content")),
        }

        dates = {
            'document_date': extract_with_default(response.xpath("//meta[@name='DC.date']/@content")),
        }

        structured_data = {
            'document': document,
            'tags': tags,
            'persons': persons,
            'organizations': organizations,
            'geographic_nouns': geographic_nouns,
            'locations_archives': locations_archives,
            'dates': dates,
        }

        yield structured_data


# In[3]:


class JSONPipeline:
    def open_spider(self, spider):
        self.file = open('dodis_dataBaseRendu.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(item, ensure_ascii=False, indent=2)
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
        self.file.write(line)
        return item


# In[4]:


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
    'ITEM_PIPELINES': {'__main__.JSONPipeline': 1},
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_DELAY': 0.5,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 0.5,
    'AUTOTHROTTLE_MAX_DELAY': 5,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
})

process.crawl(DodisSpider)
process.start()

