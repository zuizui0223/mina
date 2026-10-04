import io
import json
import unittest
import zipfile

from scripts.audit_emperor_mobile_node_support import (
    extract_urls_from_xml,
    parse_kmz,
)


class EmperorMobileNodeSupportTests(unittest.TestCase):
    def test_extract_urls(self):
        xml=b'''<root><URL>https://example.org/a</URL><x>hello</x><URL>https://example.org/b</URL></root>'''
        self.assertEqual(extract_urls_from_xml(xml),["https://example.org/a","https://example.org/b"])

    def test_parse_kmz(self):
        kml='''<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>
        <Placemark><name>A</name><Point><coordinates>10,-70,0</coordinates></Point></Placemark>
        <Placemark><name>B</name><Point><coordinates>20,-71,0</coordinates></Point></Placemark>
        </Document></kml>'''
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w") as z:
            z.writestr("doc.kml",kml)
        r=parse_kmz(buf.getvalue())
        self.assertEqual(r["placemarks"],2)
        self.assertEqual(r["coordinate_points"],2)


if __name__=="__main__":
    unittest.main()
