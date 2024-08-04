from html.parser import HTMLParser
from bs4 import BeautifulSoup
import urllib.parse
from selenium.common.exceptions import NoSuchElementException

class DescriptionItemsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = {"key":False, "value":False}
        self.output = dict()
        self.key, self.value = None, None
    def handle_starttag(self, tag, attrs):
        attrs = {x[0]:x[1] for x in attrs}
        #print("Encountered a start tag:", tag)
        if tag == 'div':
            if 'class' in attrs and attrs['class'] == 'key':
                self.found["key"] = True
            elif 'class' in attrs and attrs['class'] == "value":
                self.found["value"] = True

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        if self.found["key"]:
            self.found["key"] = False
            self.key = data
        elif self.found["value"]:
            self.found["value"] = False
            self.value = data
        if self.key is not None and self.value is not None:
            self.output[self.key] = self.value
            self.key, self.value = None, None
        #print("Encountered some data  :", data)

def parse_description_items(pub_no):
    with open('data/{0}/description_items_00000000000000000000.html'.format(pub_no)) as f:
        parser = DescriptionItemsParser()
        page = '\n'.join(f.readlines())
        parser.feed(page)
        soup = BeautifulSoup(page, 'html.parser')
        try:
            parser.output['Abstract'] = soup.find_all('base:paragraphs')[0].get_text()
        except IndexError:
            parser.output['Abstract'] = "" 
        return parser.output

def parse_full_text(pub_no):
    with open('data/{0}/full_text_00000000000000000000.html'.format(pub_no)) as f:
        page = '\n'.join(f.readlines())
        soup = BeautifulSoup(page, 'html.parser')
        full_text = '\n'.join([x.text for x in soup.find_all("div", {"class": "fullText"})])
        return {"Full text": full_text}
        
def parse_full_text_image(pub_no):
    try:
        with open('data/{0}/full_text_image_00000000000000000000.html'.format(pub_no)) as f:
            page = '\n'.join(f.readlines())
            soup = BeautifulSoup(page, 'html.parser')
            iframe_tag = soup.find('iframe')
            if iframe_tag is not None:
                pdf_url = urllib.parse.urljoin('https://pss-system.cponline.cnipa.gov.cn/', iframe_tag['src'])
                return {"Pdf url": pdf_url}
            else:
                return {"Pdf url": "No file"}
    except FileNotFoundError:
        pass
def parse_abstract_attached_drawings(pub_no):
    with open('data/{0}/abstract_attached_drawings_00000000000000000000.html'.format(pub_no)) as f:
        page = '\n'.join(f.readlines())
        soup = BeautifulSoup(page, 'html.parser')
        image_urls = [urllib.parse.urljoin('https://pss-system.cponline.cnipa.gov.cn/', x['src']) for x in soup.find_all('img') if x['src'].startswith('/service-image-url/')]
        return {"Abstract attached drawings Urls": image_urls}

def parse_drawings_of_specification(pub_no):
    with open('data/{0}/attached_drawings_of_the_specification_00000000000000000000.html'.format(pub_no)) as f:
        page = '\n'.join(f.readlines())
        soup = BeautifulSoup(page, 'html.parser')
        image_urls = [urllib.parse.urljoin('https://pss-system.cponline.cnipa.gov.cn/', x['src']) for x in soup.find_all('img') if x['src'].startswith('/service-image-url/')]
        return {"Attached drawings of the specification urls": image_urls}

class LegalStatusParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_row = False
        self.output = []
        self.buffer = []
    def handle_starttag(self, tag, attrs):
        attrs = {x[0]:x[1] for x in attrs}
        if tag == 'tr':
            self.table_row = True
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if tag == 'tr':
            self.table_row = False
            self.output.append({'Application No.':self.buffer[0], 'Legal status announcement date':self.buffer[1], "Chinese Meaning":self.buffer[2], "English Meaning":self.buffer[3]})
            self.buffer = []

    def handle_data(self, data):
        if self.table_row:
            self.buffer.append(data)
        #print("Encountered some data  :", data)

def parse_legal_status(pub_no):
    index = 0
    parser = LegalStatusParser()
    while True:
        try:
            f = open('data/{0}/legal_status_{1}.html'.format(pub_no,str(index).zfill(20)))
        except IOError:
            break
        parser.feed('\n'.join(f.readlines()))
        index += 1
    return {"Legal status": parser.output}


class HomologyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_row = False
        self.output = []
        self.buffer = []
    def handle_starttag(self, tag, attrs):
        attrs = {x[0]:x[1] for x in attrs}
        if tag == 'tr':
            self.table_row = True
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if tag == 'tr':
            self.table_row = False
            self.output.append({'Public Notice No.':self.buffer[0], 'Application No.':self.buffer[1]})
            self.buffer = []

    def handle_data(self, data):
        if self.table_row:
            self.buffer.append(data)
        #print("Encountered some data  :", data)

def parse_homology(pub_no):
    index = 0
    parser = HomologyParser()
    while True:
        try:
            f = open('data/{0}/homology_{1}.html'.format(pub_no,str(index).zfill(20)))
        except IOError:
            break
        parser.feed('\n'.join(f.readlines()))
        index += 1
    try:
        return {"Homology": parser.output[1:]}
    except IndexError:
        pass
    return {}

class CitationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_row = False
        self.output = []
        self.buffer = []
        
    def handle_starttag(self, tag, attrs):
        attrs = {x[0]:x[1] for x in attrs}
        if tag == 'tr':
            self.table_row = True
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if tag == 'tr':
            self.table_row = False
            try:
                self.output.append({'Publication No.':self.buffer[0], "Application No.":self.buffer[1], "IPC Classification No.":self.buffer[2]})
            except IndexError:
                pass
            self.buffer = []

    def handle_data(self, data):
        if self.table_row:
            self.buffer.append(data)
        #print("Encountered some data  :", data)

def parse_citation(pub_no):
    index = 0
    parser = CitationParser()
    while True:
        try:
            f = open('data/{0}/citation_{1}.html'.format(pub_no,str(index).zfill(20)))
        except IOError:
            break
        parser.feed('\n'.join(f.readlines()))
        index += 1
    try:
        return {"Citation": parser.output[1:]}
    except IndexError:
        pass
    return {}

class CitedParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_row = False
        self.output = []
        self.buffer = []
        
    def handle_starttag(self, tag, attrs):
        attrs = {x[0]:x[1] for x in attrs}
        if tag == 'tr':
            self.table_row = True
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        if tag == 'tr':
            self.table_row = False
            try:
                self.output.append({'Publication No.':self.buffer[0], "Application No.":self.buffer[1], "IPC Classification No.":self.buffer[2], "Applicant":self.buffer[3], "Inventor":self.buffer[4], "Relevant paragraphs":self.buffer[5], "Claims":self.buffer[6]})
            except IndexError:
                pass
            self.buffer = []

    def handle_data(self, data):
        if self.table_row:
            self.buffer.append(data)
        #print("Encountered some data  :", data)

def parse_cited(pub_no):
    index = 0
    parser = CitedParser()
    output = []
    while True:
        try:
            f = open('data/{0}/cited_{1}.html'.format(pub_no,str(index).zfill(20)))
        except IOError:
            break
        soup = BeautifulSoup('\n'.join(f.readlines()), 'html.parser')
        header = ['', 'Relevance', 'Publication No.', 'Application No.', 'IPC Classification No.', 'Applicant', 'Inventor', 'Relevant paragraphs', 'Claims']
        for tr in soup.find_all('tr'):
            temp = dict()
            for i,td in enumerate(tr.find_all('td')):
                temp[header[i]] = td.get_text()
            if len(temp):
                del temp['']
                print(temp)
                output.append(temp)
        index += 1
    try:
        return {"Cited": output}
    except IndexError:
        pass
    return {}

