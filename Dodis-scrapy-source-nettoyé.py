#!/usr/bin/env python
# coding: utf-8

# In[1]:


import scrapy
from scrapy.crawler import CrawlerProcess
import json


# In[2]:


class DodisSpider(scrapy.Spider):
    name = "dodis"
    
    # Générer les URLs à scraper
    start_urls = [f"https://dodis.ch/{str(i).zfill(5)}" for i in range(61431, 61438)]  # Ajustez la plage selon vos besoins

    # Possibilité de scraper à partir des SPAN3 et SPAN9
    # Exemple basé sur https://dodis.ch/61431
    
    # revoir xpath = catégorie à part?
    def parse(self, response):
        # Informations document
        document = {
            'url': response.xpath("//meta[@itemprop='url']/@content").get(default=""),
            # retirer "le language_code" ou "language_text" ?
            'digital_id': response.xpath("//meta[@itemprop='url']/@content").re_first(r'(\d+)$'),
            'document_identifier': response.xpath("//meta[@name='DC.identifier']/@content").get(default=""),
            'language_code': response.xpath("//meta[@itemprop='inLanguage']/@content").get(default=""),
            'language_text': response.css(".float-right.blue-box-content-language.document-detail-language::text").get(default=""),
            'publication_date': response.xpath("//meta[@itemprop='datePublished']/@content").get(default=""),
            # Faut-il intégrer <meta name="DC.type"  content="document" /> ? Est-ce qu'il y a un DC.type pour les thématiques, personnes, pays, etc. ?
            'type_document': " ".join(response.css(".document-detail-type::text").get(default="").split()) or None,
            'summary': response.css(".document-detail-summary::text").get(default=""),
            'reference': response.css(".document-details-dossier-reference a::text").get(default=""),
            'citation_recommendation': response.css(".cite-box input::attr(value)").get(default=""),
            'if_published_publication_details': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").get(default=""),
            'if_published_volume_reference': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r'\bBd\. \d{4}\b'),
            'if_published_volume_reference_noDoc': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r"(Dok\. \d+)"),
            'if_published_volume_link': response.css(".documents-volume-icon::attr(href)").get(default=""),
            'related_to_dodis_docs': response.css(".searchResult a::text").getall(),
        }
        
        

        # Tags - et mots-clés - associés au document
        # Faut-il distinguer 
        tags = {
            #retirer premier tag? metadata
            'document_tags': response.xpath("//meta[@name='DC.subject']/@content").get(default="").split("; "),
            'classification_tags': response.css(".document-detail-tags .tag::text").getall() or response.css("[class*='tag']::text").getall(),
            # Important à garder ? Quid liste ??
            'tags_multilang': {
                lang: response.css(f".tag[hreflang='{lang}']::text").getall() 
                for lang in ['de', 'fr', 'it', 'en']
            }
        }

        
        # Personnes mentionnées + rôles OK
        persons = {
            'author_person': response.css("#anc_pau .tag::text").get(default=""),
            'signatory_person': response.css("#anc_ps .tag::text").get(default=""),
            'recipient_person': response.css("#anc_pad .tag::text").get(default=""),
            'other_persons_mentioned': response.css("#anc_pm .tag::text").getall(),
        }

        # Organisations mentionnées OK
        organizations = {
            'author_organization': response.css("#anc_oau .tag::text").get(default=""),
            'recipient_organization': response.css("#anc_oad .tag::text").get(default=""),
            'other_organizations_mentioned': response.css("#anc_om .tag::text").getall(),
        }
        
        # Lieux géographiques mentionnées OK
        geographic_nouns = {
            'geo_nouns_mentioned': response.css("#anc_plm .tag::text").getall(),
        }

        
        locations = {
            'recipient_location': response.xpath("//meta[@name='DC.coverage']/@content").get(default=""),
            # pertinent de garder ? le dictionnaires archives les indique aussi, mais de manière plus structurée !
        }

        # Archives et dossiers OK
        # archive_location1, archive_location_link_dodis1, ..., archive_location2
        # trier selon speciment
        archives = {
            'archive_location1': response.css("#specimen-0 td:contains('Archive') + td ::text").get(default=""),
            'archive_location_link_dodis1': response.css("#specimen-0 td:contains('Archival classification') + td ::text").get(default=""),
            'archive_reference1': " ".join(response.css("#specimen-0 td:contains('Dossier title') + td ::text").get(default="").replace('\n', '').strip().split()),
            'archive_folder_title1': response.css("#specimen-0 td:contains('File reference archive') + td ::text").get(default=""),
            'archive_location2': response.css("#specimen-1 td:contains('Archive') + td ::text").get(default=""),
            'archive_location_link_dodis2': response.css("#specimen-1 td:contains('Archival classification') + td ::text").get(default=""),
            'archive_reference2': " ".join(response.css("#specimen-1 td:contains('Dossier title') + td ::text").get(default="").replace('\n', '').strip().split()),
            'archive_folder_title2': response.css("#specimen-1 td:contains('File reference archive') + td ::text").get(default=""),
            'archive_location3': response.css("#specimen-2 td:contains('Archive') + td ::text").get(default=""),
            'archive_location_link_dodis3': response.css("#specimen-2 td:contains('Archival classification') + td ::text").get(default=""),
            'archive_reference3': " ".join(response.css("#specimen-2 td:contains('Dossier title') + td ::text").get(default="").replace('\n', '').strip().split()),
            'archive_folder_title3': response.css("#specimen-2 td:contains('File reference archive') + td ::text").get(default=""),
        }

        # Autres informations 
        # Indiquer en booléen les _link ?
        additional_info = {
            'contributors': response.xpath("//meta[@name='DC.contributor']/@content").get(default=""),
            # pertinent de garder ?
            'usage_rights': response.xpath("//meta[@name='DC.rights']/@content").get(default=""),
            'transcription_link': response.css(".nav.nav-tabs a[href='#tabs-0']::attr(href)").get(default=""),
            'DDS_link': response.css(".nav.nav-tabs a[href='#tabs-1']::attr(href)").get(default=""),
            'facsimile_link': response.css(".nav.nav-tabs a[href='#tabs-2']::attr(href)").get(default=""),
        }

        # Langues -> renvoie deux fois certaines abréviations de langues
        languages = {
            'available_languages': response.css(".language-link::attr(hreflang)").getall()
        }

        # Dates supplémentaires OK
        dates = {
            'document_date': response.xpath("//meta[@name='DC.date']/@content").get(default=""),
        }

        # Dictionnaires
        structured_data = {
            'document': document,
            'tags': tags,
            'persons': persons,
            'organizations': organizations,
            'geographic_nouns': geographic_nouns,
            'locations': locations,
            'archives': archives,
            'additional_info': additional_info,
            'languages': languages,
            'dates': dates,
        }

        yield structured_data


# In[3]:


class JSONPipeline:
    def open_spider(self, spider):
        self.file = open('dodis_dataScrapyEssai5.json', 'w', encoding='utf-8')
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(item, ensure_ascii=False) + ",\n"
        self.file.write(line)
        return item


# In[4]:


# Configuration du processus Scrapy
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
    'ITEM_PIPELINES': {'__main__.JSONPipeline': 1},
    'FEEDS': {
        "dodis_dataScrapyEssai5.json": {"format": "json", "overwrite": True},
    },
    # Réglages de vitesse
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_DELAY': 0.5,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 0.5,
    'AUTOTHROTTLE_MAX_DELAY': 5,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
})

# Lancer le spider
process.crawl(DodisSpider)
process.start()  # Lancer le scraping


# In[ ]:




