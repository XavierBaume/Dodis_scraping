#!/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install scrapy


# In[2]:


import scrapy
from scrapy.crawler import CrawlerProcess
import json


# In[3]:


class DodisSpider(scrapy.Spider):
    name = "dodis"
    
    # URLs à scraper
    start_urls = [f"https://dodis.ch/{str(i).zfill(5)}" for i in range(61431, 61438)]  # Ajuster la plage 
    # robots.txt pour fichiers interdits à scraper

    # Possibilité de scraper à partir des SPAN3 et SPAN9
    
    # revoir xpath = catégorie à part?
    def parse(self, response):
        # Informations document
        document = {
            'url': response.xpath("//meta[@itemprop='url']/@content").get(default=""),
            # retirer "le language:"
            'digital_id': response.xpath("//meta[@itemprop='url']/@content").re_first(r'(\d+)$'),
            'document_identifier': response.xpath("//meta[@name='DC.identifier']/@content").get(default=""),
            'language_code': response.xpath("//meta[@itemprop='inLanguage']/@content").get(default=""),
            'language_text': response.css(".float-right.blue-box-content-language.document-detail-language::text").get(default=""),
            'publication_date': response.xpath("//meta[@itemprop='datePublished']/@content").get(default=""),
            # pas d'info dans script
            #'last_modified_date': response.xpath("//meta[@itemprop='dateModified']/@content").get(default=""),
            # ??? <meta name="DC.type"  content="document" /> DONC pas forcément, PV SI DOCUMENT parce Personne, orga., dossier
            'type_document': response.css(".document-detail-type::text").get(default="").strip() or None,
            'summary': response.css(".document-detail-summary::text").get(default=""),
            'reference': response.css(".document-details-dossier-reference a::text").get(default=""),
            'citation_recommendation': response.css(".cite-box input::attr(value)").get(default=""),
            # même output que full_reference
            'if_published_publication_details': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").get(default=""),
            'if_published_volume_reference': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r'\bBd\. \d{4}\b'),
            'if_published_volume_reference_noDoc': response.xpath("normalize-space(//meta[@name='DC.description']/@content)").re_first(r"(Dok\. \d+)"),
            'if_published_volume_link': response.css(".documents-volume-icon::attr(href)").get(default=""),
            #'download_xml': response.xpath("//a[contains(@href, 'dodis-') and contains(@href, '.xml')]/@href").get(default=""),
            #'download_html': response.xpath("//a[contains(@href, 'dodis-') and contains(@href, '.html')]/@href").get(default=""),
            # inexistant dans script : 'access_status': response.css(".access-status::text").get(default=""),
            # inexistant dans script :'declassification_date': response.xpath("//meta[@name='DC.date.declassified']/@content").get(default=""),
            #'full_reference': response.xpath("//meta[@name='DC.description']/@content").get(default=""),
            #ressort les liens
            'related_to_dodis_docs': response.css(".searchResult a::text").getall(),
        }
        
        

        # Tags - et mots-clés - associés au document
        # Revoir tags2 Main_tag? Second_Tag
        tags = {
            #retirer premier tag? metadata
            'document_tags': response.xpath("//meta[@name='DC.subject']/@content").get(default="").split("; "),
            'classification_tags': response.css(".document-detail-tags .tag::text").getall() or response.css("[class*='tag']::text").getall(),
            'keywords': response.xpath("//meta[@name='keywords']/@content").get(default="").split(", "),
            # Quid liste ??
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

        # Lieux de localisation aux AFS : cotes
        # lié dossier au bon fond d'archive --> changer DC coverage car ne permet pas de lier au fond spécifique 
        locations = {
            'recipient_location': response.xpath("//meta[@name='DC.coverage']/@content").get(default=""),
            # pertinent ?
            'other_locations_mentioned': response.css(".other-locations-mentioned a::text").getall(),
        }

        # Archives et dossiers
        # archive_location1, archive_location_link_dodis1, ..., archive_location2
        archives = {
            'archive_location1': response.css(".fundort a::text").get(default=""),
            'archive_location_link_dodis1': response.css(".fundort a::attr(href)").get(default=""),
            'archive_reference': response.css(".foldable-switch-signature a::text").get(default=""),
            'archive_old_reference': response.css(".foldable-content-signature a::text").get(default=""),
            'archive_folder_title': response.css("td::text").get(default=""),
            'archive_folder_reference': response.css(".document-details-dossier-reference a::text").get(default=""),
        }

        # Autres informations 
        additional_info = {
            'contributors': response.xpath("//meta[@name='DC.contributor']/@content").get(default=""),
            'usage_rights': response.xpath("//meta[@name='DC.rights']/@content").get(default=""),
            'data_source': response.css("li[title*='Transcription'] a::attr(title)").get(default="") or \
                           response.css("li[title*='Facsimile'] a::attr(title)").get(default=""),
            'contextual_notes': response.css(".contextual-notes::text").get(default=""),
            'transcription_link': response.css(".nav.nav-tabs a[href='#tabs-0']::attr(href)").get(default=""),
             # A ajouter 'DDS_link': response.css(".nav.nav-tabs a[href='#tabs-1']::attr(href)").get(default=""),
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


# In[4]:


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


# In[5]:


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




