import xml.etree.ElementTree as ET
from arachnid.models import Article

class Parser:
    def __init__(self, xml_bytes, source):
        self.xml = xml_bytes
        self.source = source
        
    def parse_xml(self):
        root = ET.fromstring(self.xml)
        channel = root.find("channel")
        
        for item in channel.findall("item"):
            yield Article(
                title = item.findtext("title"),
                link = item.findtext("link"),
                description = item.findtext("description"),
                pub_date=item.findtext("pubDate"),
                source=self.source
            )