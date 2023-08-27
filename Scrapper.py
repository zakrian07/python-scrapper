from urllib.parse import quote_plus
from bs4.element import NavigableString
import requests
from bs4 import BeautifulSoup
import urllib
from sites.mouser import Mouser
import re
import json
from sites.Festo import Festo
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
from undetected_chromedriver import Chrome, ChromeOptions
from time import sleep
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import ssl


# from distributors.rshughes import scrap_rshughes

options = webdriver.ChromeOptions()
options.add_argument('--headless')


class Scrapper(Mouser):

    def scrap_newark(self, partNumber):
        headers = {
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            'User-Agent': 'MyAppName/1.0'
        }
        try:
            url = 'https://www.newark.com/webapp/wcs/stores/servlet/AjaxSearchLookAhead?storeId=10194&catalogId=15003&langId=-1&searchTerm='
            response = requests.get(url + str(partNumber), headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find('table', class_="searchBoxResultTable")
            tr = table.find_all('tr')[0]
            url_prod = tr.find('td', class_="leftcolumn").find(
                'a', id="searchResultProductList").attrs['href']

            response_prod = requests.get(url_prod, headers=headers)
            soup_prod = BeautifulSoup(response_prod.text, 'lxml')

            partNumber = re.findall(r'\bsku: "(.+?)"', response_prod.text)
            partName = re.findall(r"\bd: '(.+?)'", response_prod.text)
            brand = re.findall(r'\bm: "(.+?)"', response_prod.text)
            ds = soup_prod.find(
                'a', {'data-dtm-eventinfo': "Technical Data Sheet"})
            st = soup_prod.find('span', class_="availTxtMsg").text or ''

            rohs_table = soup_prod.find(
                'table', class_='details-table-desktop')
            for tr in rohs_table.find_all('tr'):
                if 'RoHS Compliant' in tr.find('th').text:
                    rohs_stat = tr.find(
                        'td', class_="rohsDescription").contents[0] or ''
                    break

            result = {
                'Results': 'Found',
                'status': re.sub(r'\d', '', st).strip() or None,
                'partNumber': partNumber[0] if partNumber else None,
                'partName': partName[0] if partName else None,
                'dataSheet': ds.attrs['href'] if ds else None,
                'brand': brand[0] if brand else None,
                'RoHSCompliantStatus': rohs_stat.strip()
            }
        except Exception as e:
            print('part number is not found on server')
            return {"status": 404}

        return result

    def scrap_3m(self, productNumber):
        print('hello world', productNumber)
        url = 'https://www.3m.com/3M/en_US/p/?Ntt=' + str(productNumber)
        response = requests.get(url,
                                headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
        matches = re.search(
            r'window.__INITIAL_DATA = ({.+})', response.text).group(1)
        matches_list = json.loads(matches)['items']
        try:
            headers = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru;q=0.6',
                'cache-control': 'max-age=0',
                'connection': 'keep-alive',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }
            prod_url = matches_list[0].get('url')
            response_page = requests.get(prod_url, headers=headers)

            safety_sheets = []
            soup = BeautifulSoup(response_page.text, 'lxml')
            tab_divs = soup.find_all('div', class_='MMM--dataGroup-hd')
            for div in tab_divs:
                if div.find('div', text='Safety Data Sheets'):
                    safety_links = div.find_all('a')
                    for a in safety_links:
                        safety_sheets.append(a.attrs['href'])

            disc_notice = soup.find('div', text="Discontinuation Notices")
            if disc_notice:
                status = 'discontinued'
            else:
                status = 'active'

            re_stock_no = re.search(
                r'<em>(.+?)</em>', matches_list[0].get('stockNumber'))
            if re_stock_no:
                stock_no = re_stock_no.group(1)
            else:
                stock_no = productNumber

            result = {
                'Results': 'Found',
                'status': status,
                'productNumber': stock_no,
                'partName': soup.find('h1').text,
                'safetyDataSheetURL': safety_sheets

            }
        except Exception as e:
            print('part number is not found on server')
            return {"status": 404}

        return result

    def scrap_ti(self, partnumber):
        print("oldPartnumber", partnumber)
        if str(partnumber).find('&45F') != -1:
            print("replace")
            partnumber = str(partnumber).replace('&45F', '/')
            url = 'https://www.ti.com/product/LM741QML/part-details/' + \
                str(partnumber)
        else:
            url = 'https://www.ti.com/product/' + str(partnumber)
        print("newPartnumber", partnumber)
        # url = 'https://www.ti.com/product/LM741QML/part-details/' + str(partnumber)
        print("url = ", url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        datasheet = soup.find('a', navtitle="data sheet") or ''
        # print("status", soup.find('ti-product-status').find('a').text )
        # print("Partnumber", soup.find('ti-main-panel').attrs["gpn"])
        try:
            if url.find('/') == -1:
                result = {
                    'Results': 'Found',
                    'status': soup.find('ti-product-status').find('a').text,
                    'Partnumber': soup.find('ti-main-panel').attrs["gpn"],
                    'partName': soup.find('h2').text,
                    'CertificateDeclaration': None,
                    'DataSheetURL': ('https://www.ti.com' + datasheet.attrs["href"]) if datasheet else None
                }
            else:
                result = {
                    'Results': 'Found',
                    'status': soup.find('ti-product-status').find('a').text,
                    # 'Partnumber': soup.find('ti-main-panel').attrs["gpn"],
                    'partName': soup.find('h2').text,
                    'CertificateDeclaration': None,
                    'DataSheetURL': ('https://www.ti.com' + datasheet.attrs["href"]) if datasheet else None
                }
        except Exception as e:
            print('part number is not found on server')
            return {"status": 404}

        return result

    def scrap_murata(self, partNumber):
        try:
            url = 'https://www.murata.com/en-us/products/productdetail?partno=' + \
                quote_plus(str(partNumber))
            response = requests.get(url)
            series_re = re.search(r'Series=(.+?)(,| /)', response.text)
            if series_re:
                series = series_re.group(1)
            else:
                series = partNumber
            print(response.text)
            soup = BeautifulSoup(response.text, 'lxml')
            status_icons = soup.find('ul', class_='detail-status-icon')
            for icon in status_icons.find_all('li'):
                status_img_link = icon.find('img').attrs['src']
                if 'avairable' in status_img_link:
                    status = 'available'
                    break
                elif 'discontinued' in status_img_link:
                    status = 'discontinued'
                    break
                elif 'planneddiscontinue' in status_img_link:
                    status = 'to be discontinued'
                    break
                elif 'nrnd' in status_img_link:
                    status = 'not recommended for new design'
                    break

            def search_doc_link(type_: list, section):
                docs_divs = soup.find_all('div', class_="detail-sidenavi")
                for dd in docs_divs:
                    if dd.find('h2', text=section):
                        for doc_a in dd.find_all('a'):
                            for t in type_:
                                if t in doc_a.text:
                                    doc_link = doc_a.attrs['href']
                                if not doc_link.startswith('http'):
                                    return 'https://murata.com/' + doc_link
                                else:
                                    return doc_link

            dsheet = search_doc_link(
                ['Data Sheet', 'Specifications Sheet'], 'Details')
            rohs_url = search_doc_link(['RoHS'], 'Related Links')
            reach_url = search_doc_link(['REACH'], 'Related Links')
            for pdf_list_url in {rohs_url, reach_url}:
                response_pdflist = requests.get(pdf_list_url)
                soup_pdf = BeautifulSoup(response_pdflist.text, 'lxml')
                rohs, reach = (None, None)
                # cannot access local variable 'table' where it is not associated with a value (BUG)
                for table in soup_pdf.find_all('table', class_="m-table_table"):
                    links_pdf = []
                for tbody in table.find_all('tbody'):
                    for tr in table.find_all('tr'):
                        tds = tr.find_all('td')
                    if tds:
                        series_pdf = tds[0].text.split()[0].rstrip('*')
                        links_pdf.append(
                            (series_pdf, tds[1].find('a').attrs['href']))
                links_pdf = sorted(links_pdf, key=lambda x: -len(x[0]))
                for sr_pdf, pdf_link in links_pdf:
                    if sr_pdf in series:
                        if '-rohs-' in tds[1].find('a').attrs['href'] and rohs is None:
                            rohs = 'https://www.murata.com' + pdf_link
                    elif '-reach-' in tds[1].find('a').attrs['href'] and reach is None:
                        reach = 'https://www.murata.com' + pdf_link
            result = {
                'Results': 'Found',
                'status': status,
                'partNumber': partNumber,
                'partName': soup.find('h1').text.strip(),
                'DataSheet': dsheet,
                'RoHS': rohs,
                'REACH': reach
            }
        except Exception as e:
            print(e)
            return {"status": 404}
        return result

    def scrap_festo(self, partnumber):
        # print(partnumber)
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
        url = "https://www.festo.com/ca/en/search/autocomplete/SearchBoxComponent?term=" + \
            str(partnumber)

        try:
            # request part information from Festo server
            res = requests.request("GET", url, headers=HEADERS)
        except:
            return {"status": 404}

        response = json.loads(res.text)

        results = response['pagination']['totalNumberOfResults']

        # handle the returns depending on how many parts are found
        if results == 0:
            # no parts have been found
            print(f'part number {partnumber} is not found on server')
            return {"status": 404}

        elif results > 1:
            # more than one part has been found, search for exact match
            part = Festo().multiple_results(response, partnumber)
            # make sure error message is correctly handled if no exact match is found
            if part == {"status": 404}:
                return part

        elif results == 1:
            # exactly one part has been found
            part = response['products'][0]

        # search if part is on SVHC / Exemption list
        dsl_found = Festo().substances.loc[Festo(
        ).substances['Identifier'] == str(part['code'])]

        # extract the wanted part information
        result = {

            # search result
            'Results': 'found',

            # Festo Part Number
            'FestoPartNumber': part['code'],

            # Festo Part Name
            'FestoPartName': part['name'],

            # Festo Order Code
            "FestoOrderCode": part['orderCode'],

            # Part link
            "PartURL": f"https://www.festo.com/ca/en{str(part['url'])}",

            # ROHS information
            'ROHS exemption': " / ".join(str(v) for v in dsl_found['ROHS Exemption:']),

            # SVHC substance
            'SVHC contained:': " / ".join(str(v) for v in dsl_found['SVHC contained:']),

            # SVHC CAS
            'SVHC CAS number': " / ".join(str(v) for v in dsl_found['CAS:']),

            # SCIP number
            'SCIP number': " / ".join(str(v) for v in dsl_found['SCIP number']),

            # Article name
            'Article name': " / ".join(str(v) for v in dsl_found['Article name']),

            # Last updated
            'Last updated': " / ".join(str(v) for v in dsl_found['Last Updated'])
        }

        return result

    def scrap_onsemi(self, partnumber):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        try:
            response = requests.get(
                "https://www.onsemi.com/PowerSolutions/MaterialComposition.do?searchParts=" + urllib.parse.quote(str(partnumber), safe=''), headers=headers)
            data = BeautifulSoup(response.text, 'lxml')
            table = data.find(id="MaterialCompositionTable")
            pn = table.tbody.tr.td.find_next('td').text
            status = table.tbody.tr.td.find_next('td').find_next('td').text
            hf = table.tbody.tr.td.find_next(
                'td').find_next('td').find_next('td').text
            excempt = table.tbody.tr.td.find_next('td').find_next(
                'td').find_next('td').find_next('td').text
            links = table.find_all('a', href=True)
            declaration = "https://www.onsemi.com" + links[5]['href']
            lead = "not found"
            if len(excempt) > 1:
                lead = table.tbody.tr.td.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next(
                    'td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text

            return {"Results": "Found", "SPN_grabbed": pn, "Status": status, "HF": hf, "Excemption": excempt, "Declaration": declaration, "Lead(Cas No:7439-92-1)": lead}

        except Exception as e:
            return {"status": 404}

    def scrap_Maxim(self, partnumber):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        # part = re.sub.replace(":", "/", partnumber)
        # print(part)
        url = requests.get(
            "https://www.maximintegrated.com/en/qa-reliability/emmi/content-lookup/product-content-info.html?partNumber=" + partnumber, headers=headers)
        soup = BeautifulSoup(url.text, 'lxml')
        print(soup)
        try:
            table = soup.find(id="productcontentinfo")
            Rohs_Compliance = table.tbody.tr.td.find_next('td').text
            Rohs2_compliance = table.tbody.tr.td.find_next(
                'tr').td.find_next('td').text
            Halogen_compliance = table.tbody.tr.find_next(
                'tr').find_next('tr').td.find_next('td').text
            Reach_Compliance = table.tbody.tr.find_next('tr').find_next(
                'tr').find_next('tr').td.find_next('td').text
            print(Rohs_Compliance, Rohs2_compliance,
                  Halogen_compliance, Reach_Compliance)
            return {"Results": "Found", "Partnumber": partnumber, "Rohs_Compliance": Rohs_Compliance, "Rohs2_compliance": Rohs2_compliance, "Halogen_compliance": Halogen_compliance, "Reach_Compliance": Reach_Compliance}
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_Molex(self, partnumber):
        url = "https://www.molex.com/en-us/products/part-detail/" + partnumber

        payload = {}
        headers = {
            'authority': 'www.molex.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            Results = 'Found'
            dSPNGrabbed = soup.find(
                class_='cmp-pdp__overview-product-info').find_all('span')[0].text.strip()
            PartStatus = soup.find(
                class_='cmp-pdp__overview-status').find('span').text.strip()
            Reach = soup.find(
                class_='cmp-pdp__compliance').find_all('dd')[-2].text.strip()
            Rohs = soup.find(
                class_='cmp-pdp__compliance').find_all('dd')[-1].text.strip()
            SPNGrabbed = soup.find(
                class_='cmp-pdp__overview-product-info').find_all('span')[0].text
            DeclarationLink = "https://www.molex.com/molex/electrical_model/rohsCoC.jsp?data=" + \
                urllib.parse.quote(SPNGrabbed, safe="")
            return {"Results": Results, "dSPNGrabbed": dSPNGrabbed, "PartStatus": PartStatus, "Reach": Reach, "Rohs": Rohs, "SPNGrabbed": SPNGrabbed, DeclarationLink: DeclarationLink}
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_Phoenix(self, partnumber):
        try:
            url = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/products?_locale=en-CA&_realm=ca&offset=0&requestedSize=11"
            reporturl = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/report/guid?_locale=en-CA&_realm=ca"

            # payload = "{\"searchItems\":[\"1084745\"]}"
            payload = '{\"searchItems\":[\"' + \
                urllib.parse.quote(str(partnumber)) + '\"]}'
            headers = {
                'authority': 'www.phoenixcontact.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,de;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://www.phoenixcontact.com',
                'pragma': 'no-cache',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', }
            try:
                response = requests.request(
                    "POST", url, timeout=9000000, headers=headers, data=payload)
            except Exception as f:
                return {"status": 404}
            try:
                report_response = requests.request(
                    "POST", reporturl, headers=headers, timeout=9000000, data=payload)
            except Exception as g:
                return {"status": 404}

            link = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/report/guid/" + \
                report_response.text + "?_locale=en-US&_realm=us"
            if (response):
                res = response.json()
            else:
                return {"status": 404}

            for results in res['items'].values():

                if results["validItem"] == False:
                    return {"status": 404}
                else:
                    return results
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrape_bivar(self, part_number):
        base_url = "https://www.bivar.com"
        print(f"Scraping data for part number: {part_number}")
        url = f"https://www.bivar.com/product/{part_number.replace(' ', '-')}"

        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            part_name = soup.find("h4").get_text(strip=True)
            if part_name == "CHECK STOCK":
                print(f"Part {part_number} is not found on server.")
                return {"status": 404}

            datasheet = (
                rohs_compliance
            ) = prop_65 = tsca_statement = emrt_statement = reach_compliance = "N/A"

            if soup.find("span", string="RoHS Compliance"):
                rohs_compliance = soup.find(
                    "span", string="RoHS Compliance").parent["href"]

            if soup.find("span", string="Prop 65 Statement"):
                prop_65 = soup.find(
                    "span", string="Prop 65 Statement").parent["href"]

            if soup.find("span", string="TSCA Compliance"):
                tsca_statement = soup.find(
                    "span", string="TSCA Compliance").parent["href"]
            if soup.find("span", string="EMRT Compliance"):
                emrt_statement = soup.find(
                    "span", string="EMRT Compliance").parent["href"]
            if soup.find("span", string="REACH Compliance"):
                reach_compliance = soup.find("span", string="REACH Compliance").parent[
                    "href"
                ]

            if soup.find("a", {"id": "datasheet"}):
                datasheet = soup.find("a", {"id": "datasheet"})["href"]

            return {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "RoHS Compliance": f"{base_url}{rohs_compliance.replace(' ', '%20')}",
                "Prop 65 Statement": f"{base_url}{prop_65.replace(' ', '%20')}",
                "TSCA Statement": f"{base_url}{tsca_statement.replace(' ', '%20')}",
                "EMRT Statement": f"{base_url}{emrt_statement.replace(' ', '%20')}",
                "REACH Compliance": f"{base_url}{reach_compliance.replace(' ', '%20')}",
                "Datasheet": f"{base_url}{datasheet.replace(' ', '%20')}",
            }
        except AttributeError:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

    def scrap_infineon(self, part_number):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        base_url = "https://www.infineon.com/cms/en/"
        # SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 114
        driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
        # Current browser version is 116.0.5845.110 (BUG)
        print(f"Scraping data for part number: {part_number}")
        driver.implicitly_wait(2)
        driver.get(base_url)
        try:
            sleep(1)
            cookies_btn = driver.find_elements(
                By.ID, "onetrust-accept-btn-handler")
            if cookies_btn:
                cookies_btn[0].click()

            search_field = driver.execute_script(
                """return document.querySelector('#offcanvas-wrapper > div > header > div.centered > main-search-input').shadowRoot.querySelector("form > span > input.mainSearchInput.typeahead.tt-input")"""
            )
            search_field.send_keys(part_number)
            search_field_button = driver.execute_script(
                """return document.querySelector('#offcanvas-wrapper > div > header > div.centered > main-search-input').shadowRoot.querySelector("form > button")"""
            )
            search_field_button.click()

            sleep(2)
            category_list = driver.find_elements(
                By.XPATH, '//div[@class="stickyElement-wrapper"]//li'
            )
            category = category_list[-2].text

            product_status = (
                driver.find_element(
                    By.XPATH, "//*[contains(text(), 'Product Status')]")
                .find_element(By.XPATH, "following-sibling::td")
                .text
            )

            datasheet = (
                driver.find_element(
                    By.XPATH, "//span[contains(text(), 'Download')]")
                .find_element(By.XPATH, "..")
                .get_attribute("href")
            )

            rohs = (
                driver.find_element(
                    By.XPATH, "//th[contains(text(), 'RoHS compliant')]")
                .find_element(By.XPATH, "following-sibling::td")
                .text
            )
            material_content = "N/A"
            materail_cont_div = driver.find_elements(
                By.XPATH, "//a[contains(text(), 'Material Content Sheet')]"
            )
            if materail_cont_div:
                sheets_list_div = materail_cont_div[0].find_element(
                    By.XPATH, "../../following-sibling::div"
                )
                sheets_list = sheets_list_div.find_elements(
                    By.XPATH, ".//li/a[1]")

                material_content = [a.get_attribute(
                    "href") for a in sheets_list]
            result = {
                "Results": 'Found',
                "Part Number": part_number,
                "Category": category,
                "Product Status": product_status,
                "RoHS Compliant Status": rohs,
                "Material Content Sheet": material_content,
                "Datasheet": datasheet,
            }
            print(f"Data successfully scraped for part number: {part_number}")
        except Exception as exc:
            print(f"Part {part_number} is not found on server.", exc)
            return {"status": 404}
        return result

    def scrap_Rscomponents(self, partnumber):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        try:
            url = "https://export.rsdelivers.com/productlist/search?query=" + \
                urllib.parse.quote(str(partnumber))

            r = requests.get(url, headers=headers)
            data = BeautifulSoup(r.text, 'lxml')
            partName = data.find(
                "h1", class_='product-detail-page-component_title__HAXxV').text

            manufacturerName = data.find("div", class_='pill-component-module_grey__38ctb').find_next(
                "div", class_='pill-component-module_grey__38ctb').text

            mpn = data.find("div", class_='pill-component-module_grey__38ctb').find_next(
                "div", class_='pill-component-module_grey__38ctb').find_next("div", class_='pill-component-module_grey__38ctb').text

            return {"Results": "Found", "Partnumber": partnumber, "mpn": mpn, "partName": partName, "manufacturerName": manufacturerName}
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_Te(self, partnumber):
        try:
            url = "https://www.te.com/commerce/alt/ValidateParts.do"
            payload = 'partNumber=' + partnumber
            headers = {
                'authority': 'www.te.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.te.com',
                'pragma': 'no-cache',
                'referer': 'https://www.te.com/commerce/alt/jsp/RoHSPartEntryPage.jsp',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36'
            }

            response = requests.request(
                "POST", url, headers=headers, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            Rohsexcemptions = ''
            svhc = ''
            count = 0
            try:
                tePartNum = soup.find(class_='product_description').text
            except Exception:
                pass
            status = soup.find('table').find('tbody').find('tr').find(
                'td').find('a').find_next('a').find_next('a').text
            try:
                rohsInfo = soup.find(
                    class_='compliance').find('a').text.strip()
            except Exception:
                pass
            excempt = soup.find(class_='compliance').find_all('li')
            for i in excempt:
                Rohsexcemptions = Rohsexcemptions.strip() + i.text.strip()
            currentReach = soup.find(class_='compliance').find_next(class_='compliance').find_next(
                class_='compliance').find_next(class_='compliance').find('span').text.strip()
            declaredReach = soup.find(class_='compliance').find_next(class_='compliance').find_next(
                class_='compliance').find_next(class_='compliance').find('span').find_next('span').text.strip()
            no_svhc = soup.find(class_='compliance').find_next(class_='compliance').find_next(
                class_='compliance').find_next(class_='compliance').find('span').find_next('span').find_next('a').text.strip()
            if no_svhc == 'Does not contain REACH SVHC':
                nohc = no_svhc

            else:
                svhc1 = soup.find(class_='compliance').find_next(class_='compliance').find_next(
                    class_='compliance').find_next(class_='compliance').find('div').find_all('span')
                for i in svhc1:
                    i = i.text.strip()
                    count += 1
                    if count > 2 and count < 6:
                        svhc = svhc + '\n' + i

            return {"Results": 'Found',
                    "status": status,
                    "TEPartNum": tePartNum,
                    "rohsInfo": rohsInfo,
                    "rohsExcemption": Rohsexcemptions,
                    "currentReachCandidate": currentReach,
                    "reachDeclaredAgainst": declaredReach,
                    "declarationLink": 'https://www.te.com/commerce/alt/SinglePartSearch.do?PN=' +
                    tePartNum+'&dest=stmt'}

        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_fair_rite(self, partNumber):
        try:
            q_resp = requests.get(
                'https://www.fair-rite.com/?s=' + str(partNumber))
            qsoup = BeautifulSoup(q_resp.text, 'lxml')
            h1s = qsoup.find_all('h1', class_='entry-title')
            for h1 in h1s:
                # error found 'NoneType' object has no attribute 'attrs' (BUG)
                if str(partNumber).lower() in h1.find('a').attrs['href'].lower():
                    url = h1.find('a').attrs['href']
                    break

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')

            dslink = soup.find(
                'a', attrs={'href': re.compile(r'.+?product_datasheet.*')})
            sdslink = soup.find('img', attrs={'alt': 'msds'}).parent
            result = {
                "partNumber": re.search(r'Part Number: (.+)', soup.find('div', class_="pdata").text).group(1),
                "Results": 'found',
                "partName": soup.find('h2', class_="tl_heading").text,
                "DataSheet link": ('https://www.fair-rite.com' + dslink.attrs['href']) if dslink else None,
                "RoHS Material Declaration": soup.find('img', attrs={'src': re.compile(r'.+?rohs_mat\.png')}).parent.attrs['href'],
                "RoHS Certificate of Compliance": soup.find('img', attrs={'src': re.compile(r'.+?rohs_comp\.png')}).parent.attrs['href'],
                "Safety Data Sheet": ('https://www.fair-rite.com' + sdslink.attrs['href']) if sdslink else None
            }
        except (IndexError, AttributeError) as e:
            print('part number is not found on server', e)
            return {"status": 404}

        print("result=====", result)

        return result

    def scrap_panduit(self, partNumber):
        try:
            url = 'https://www.panduit.com/en/search.html#q='
            print(url + str(partNumber) + '&t=all-content&sort=relevancy')
            driver = webdriver.Chrome(options=options)
            driver.get(url + str(partNumber) + '&t=all-content&sort=relevancy')
            # SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 114 (BUG)
            # Current browser version is 116.0.5845.110
            print("Code goes to sleep")
            time.sleep(10)
            print("Code wakes up")
            links = driver.find_elements(By.XPATH, '//a')
            product_link = ""
            for link in links:
                href = link.get_attribute('href')
                if str(href).find(str(partNumber)) != -1:
                    product_link = href
                    break
            print("productLink:", product_link)
            if product_link != "":
                driver.quit()
                scrap_driver = webdriver.Chrome(options=options)
                scrap_driver.get(product_link)
                print("Code goes to sleep")
                time.sleep(10)
                print("Code wakes up")
                product_name = scrap_driver.find_element(By.XPATH, '//h1')
                product_number = scrap_driver.find_element(By.XPATH, '//h3')
                table = scrap_driver.find_element(
                    By.XPATH, "//table[@class='table table-resources table-sm']")
                Specification_Sheet = table.find_element(
                    By.XPATH, "//td[@class='resource-desc border-block-resouces align-middle']")
                Specification_Sheet_link = Specification_Sheet.find_element(
                    By.TAG_NAME, 'a')

                print("td:", Specification_Sheet.get_attribute('href'))
                print("product_name:", product_name.text)
                print("product_number:", product_number.text)
                result = {
                    'Results': 'Found',
                    'Part Number': product_number.text,
                    'Part Name': product_name.text,
                    'Specification Sheet': Specification_Sheet_link.get_attribute('href')
                }
                scrap_driver.quit()
            else:
                print('part number is not found on server')
                return {"status": 404}
        except IndexError:
            print('part number is not found on server')
            return {"status": 404}
        return result

    # def scrap_analog(self, partNumber):
    #     try:
    #         url = 'https://www.analog.com/en/products/' + \
    #             str(partNumber) + '.html'
    #         driver = webdriver.Chrome(options=options)
    #         driver.get(url)
    #         product_name_div = driver.find_element(
    #             By.XPATH, "//div[@class='adi-pdp__product__description']")
    #         if product_name_div:
    #             texts = product_name_div.text.split("\n")
    #             result = {
    #                 'Results': 'Found',
    #                 'Part Number': str(partNumber),
    #                 'Part Name': texts[0],
    #                 'RoHS status': 'Yes'
    #             }
    #     except requests.exceptions.HTTPError as error:
    #         print('part number is not found on server')
    #         return {"status": 404}
    #     except Exception as error:
    #         print('part number is not found on server')
    #         return {"status": 404}
    #     return result

    def scrap_alphawire(self, partNumber):
        try:
            partNumber = str(partNumber).replace('&45F', '/')
            print(partNumber)
            url = 'https://www.alphawire.com/rohssearch/GetRohsPartNumbers?partnumber=' + \
                str(partNumber)
            print("url=", url)
            response = requests.get(url)
            # return response.json()
            if len(response.json()) != 0:
                partNumberUrl = 'https://www.alphawire.com/' + \
                    response.json()[0]['PartNumberUrl']
                print(partNumberUrl)
                # return partNumberUrl
                driver = webdriver.Chrome(options=options)
                driver.get(partNumberUrl)
                product_name = driver.find_element(By.XPATH, '//h1')
                product_description = driver.find_element(
                    By.NAME, 'description')
                print("product_name:", product_name.text)
                print("product_description:",
                      product_description.get_attribute('content'))
                result = {
                    'Results': 'Found',
                    'Part Number': str(partNumber),
                    'Part Name': product_name.text,
                    'RoHS Status': 'Yes',
                    'Description': product_description.get_attribute('content')
                }
            else:
                print('part number is not found on server')
                return {"status": 404}
        except IndexError:
            print('part number is not found on server')
            return {"status": 404}
        return result

    def scrap_tdk(self, partNumber):
        try:
            url = 'https://product.tdk.com/pdc_api/en/search/list/search_result/?part_no='
            print(url + str(partNumber) + '&_l=20&_p=1&_c=part_no-part_no&_d=0')
            response = requests.post(url + str(partNumber) + '&_l=20&_p=1&_c=part_no-part_no&_d=0',
                                     headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            },)
            soup = BeautifulSoup(response.json()['results'], 'lxml')

            table = soup.find('table', id="table_result")
            print("table:", table)
            tr = table.find('tbody').find_all('tr')[0]
            print("tr", tr)
            if "Part No." in tr:  # Substring not found! (BUG)
                print("Substring found!")
                part_detail = tr.find('td', {'data-label': "Part No."})
                print("part_detail", part_detail)
                part_no = part_detail.find('a').text
                result = {
                    'Results': 'Found',
                    'status': part_detail.find('img').attrs['title'],
                    'partNumber': part_no,
                    'partName': part_no,
                    'dataSheet': 'https://product.tdk.com' + tr.find('td', {'data-label': "Catalog / Data Sheet"}).find('a').attrs['href'],
                    'brand': tr.find('td', {'data-label': "Brand"}).text.strip()
                }
                return result
            else:
                print("Substring not found!")
                return {"status": 404}

        except IndexError:
            print('part number is not found on server')
            return {"status": 404}

        return result

    def scrap_allegro(self, partNumber):
        try:
            number_code = re.search(r'[A-Z]+(\d+)', partNumber).group(1)
            search_response = requests.get(
                'https://allegromicro.com/all-api/search?q=' + number_code)
            print("===========in", search_response.json())
            for result in search_response.json().get('Items'):
                if result.get('url'):
                    product_response = requests.get(result.get('url'))

                    products_soup = BeautifulSoup(
                        product_response.text, 'lxml')

                    item_list = list()
                    dsheets = ['https://allegromicro.com' + x.parent.attrs['href']
                               for x in products_soup.find_all('i', class_="fa fa-file-pdf-o")]
                    certs = ['https://allegromicro.com' + x.attrs.get('href', '') for x in products_soup.find_all(
                        "a", {'href': re.compile(".+certificates-of-compliance.+")})]

                    table = products_soup.find(
                        'div', class_="table-scroll div2")
                    headers = table.find('thead').find_all('th')
                    # here issue in table find funtion its throw error (BUG)
                    print("-----hello world-----")
                    table_header = list()
                    for th in headers:
                        table_header.append(th.text.strip())

                    for row in table.find_all('tr'):

                        item = {}
                        for n, td in enumerate(row.find_all('td')):

                            if table_header[n] == 'Part Number':
                                item['PartNumber'] = td.text
                            elif table_header[n] == 'Part Composition /RoHS Data':
                                item['RoHSData'] = (
                                    'https://allegromicro.com' + td.find('a').attrs.get('href')) if td.find('a') else None
                            elif table_header[n] == 'RoHSCompliant':
                                item['RoHSCompliant'] = td.text
                            elif table_header[n] == 'Package Type':
                                item['partName'] = td.text

                    if item:
                        item["Results"] = "Found"
                        item['DataSheets'] = dsheets
                        item['CertificateOfCompliance'] = certs
                        item_list.append(item)
                        if item['PartNumber'].lower() == partNumber.lower():
                            return item
        except (IndexError, AttributeError, requests.exceptions.MissingSchema) as e:
            print('part number is not found on server', e)
            return {"status": 404}

    def scrap_microchip(self, partNumber):
        try:
            url = 'https://www.microchip.com/sitesearch/api/autosuggestapi/GetAutoSuggest?q=' + \
                str(partNumber)
            response = requests.get(url)
            url_product = 'https://www.microchip.com/en-us/product/' + \
                response.text.strip('"\\r\\n')

            response_product = requests.get(url_product)

            soup = BeautifulSoup(response_product.text, 'lxml')

            dsheet = None
            docs = soup.find_all('a', class_="mchp-button red")
            for doc in docs:
                if doc.find('span').text == 'Download Data Sheet':
                    dsheet = doc.attrs['href']
                break

            status_re = re.search(r'Status: (.+?)\.', ' '.join(
                soup.find('div', 'dcf-product-status-container').find('div').text.split()))
            if status_re:
                status = status_re.group(1)
            else:
                status = None

            rohs_page_link = soup.find(
                'div', class_="rohs-editable-text").find('a').attrs['href']
            rohs_response = requests.get(rohs_page_link)

            soup_rohs = BeautifulSoup(rohs_response.text, 'lxml')
            # 'NoneType' object has no attribute 'find' (BUG)
            rohs_table = soup_rohs.find('table', class_='ROHSTable--table')
            header = [th.text.strip() for th in rohs_table.find(
                'thead').find('tr').find_all('th')]
            rohs_certificate, rohs_status = (None, None)
            for row in rohs_table.find('tbody').find_all('tr'):
                tds = row.find_all('td')
                index_product = header.index('Product')
                if tds[index_product].text.strip() == partNumber:
                    rohs_status_index = header.index('ROHS')
                    rohs_status = 'Compliant' if 'rohs-check' in tds[rohs_status_index].find(
                        'div').attrs['class'] else None
                    rohs_certificate_index = header.index('RoHS Certificate')
                    rohs_certificate = tds[rohs_certificate_index].find(
                        'div').find('a').attrs['href']
                break

            result = {
                'Results': 'Found',
                'status': status,
                'partNumber': partNumber,
                'partName': soup.find('h1').text.strip(),
                'DataSheet': dsheet,
                'RohsStatus': rohs_status,
                'RohsCertificate': rohs_certificate
            }
        except (IndexError, AttributeError) as e:
            print('part number is not found on server', e)
            return {"status": 404}
        return result

    def scrap_leespring(self, partNumber):
        try:
            payload = {
                'perpage': 20,
                'fLen_max': 10000000,
                'field_published_stock_code_value': partNumber
            }
            resp = requests.post(
                'https://www.leespring.com/compression-springs.php', data=payload)
            print(resp.json(), "----------- inresp s")
            for elem in resp.json().get('rdata', []):
                resp_new = requests.get(
                    'https://www.leespring.com/compression-specific-new/' + str(elem.get('entity_id')))
                soup = BeautifulSoup(resp_new.text, 'lxml')
                partNumber_site = soup.find(
                    'span', class_="field-content part-number-specific-product").text
                item = {
                    'Results': 'Found',
                    'partNumber': partNumber_site,
                    'partName': soup.find('span', class_=re.compile(r".*compression-outside-diameter-in-series.*")).text,
                    'SpecSheet': resp_new.url
                }
                return item
        except (IndexError, AttributeError, requests.exceptions.MissingSchema):
            print('part number is not found on server')
            return {"status": 404}

    def scrap_yageo(self, partNumber):
        try:
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "macOS",
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
            resp = requests.get(
                'https://www.yageo.com/en/ProductSearch/PartNumberSearch?part_number=' + str(partNumber), headers=headers)
            soup = BeautifulSoup(resp.text, 'lxml')

            table = soup.find('table', class_="destory_table item_sort_table")
            for tr in table.find('tbody').find_all('tr'):
                partNumber_site = ' '.join(tr.find(
                    'td', {'data-title': re.compile(r"[pP]art ?Number")}).text.split()).split()[0]

                if partNumber_site.lower().replace(' ', '') == str(partNumber).lower().replace(' ', ''):
                    pdescr = tr.find(
                        'td', {'data-title': "Packing Description"})

                    item = {
                        'Results': 'Found',
                        'partNumber': partNumber_site,
                        'packingDescription': pdescr.text.strip() if pdescr else None,
                        'SpecSheet': 'https://www.yageo.com' + tr.find('td', {'data-title': re.compile(r".*[Dd]atasheet.*|Doc\.")}).find('a').attrs['href'],
                    }
                    return item
        except (IndexError, AttributeError, requests.exceptions.MissingSchema):
            print('part number is not found on server')
            return {"status": 404}

    def scrap_Wago(self, partnumber):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        url = requests.get("https://smartdata.wago.com/articledata/svhc?articleNr=" +
                           urllib.parse.quote(str(partnumber), safe="") + "&country=Germany", headers=headers)
        soup = BeautifulSoup(url.text, 'lxml')
        try:

            table = soup.find(id="articleList")

            spn_grabbed = table.tbody.tr.td.text
            description = table.tbody.tr.td.find_next('td').text
            reach_substance = table.tbody.tr.td.find_next(
                'td').find_next('td').text
            scip = table.tbody.tr.td.find_next(
                'td').find_next('td').find_next('td').text
            cas_no = table.tbody.tr.td.find_next('td').find_next(
                'td').find_next('td').find_next('td').text
            rohs_status = table.tbody.tr.td.find_next('td').find_next(
                'td').find_next('td').find_next('td').find_next('td').text
            rohs_exception = table.tbody.tr.td.find_next('td').find_next('td').find_next(
                'td').find_next('td').find_next('td').find_next('td').text

            return {"Results": "Found", "Partnumber": partnumber, "PartName": description, "SPN_grabbed": spn_grabbed, "Reach": reach_substance, "Scip": scip, "Cas_no": cas_no, "ROHS_Exception": rohs_exception, "ROHS_Status": rohs_status, "Declaration": "https://smartdata.wago.com/articledata/svhc/download?articleNr=" + spn_grabbed + "&country=Austria"}

        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_omron(self, partnumber):
        url = "https://industrial.omron.eu/en/api/rohs_reach/search.json?q=" + partnumber

        payload = {}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': 'OMR_USER_LANG=EU-en; _navigation=60ba1233651a71dfcde6938d71ca7b99db31fc7c; _session=a89A9rz00hJU%2BO6dutS9p6tpyCwXRM1fKRn%2FGvdo%2Fd69pWd39VJDqNnaDRA3w1dkxSbRi9WuDMWyzBMpCjTMeu0YsgqCvlPIJjH8jTGpYTx1p5zbXtnsS3rqqqb61YBnxNGBjvuSC5PmpNez%2BmJqNwrP5elZMJCzda6mhh39z2LjFWpQfyZ1CfjlQyaMWtECmiMw5odcy7XhIjRvdutOq6Onjn4r4zXa%2BKkgQYIiZN%2FaeS5N%2FQDstIDu6cL4HfJ3vB%2B0%2BLosmA96O0GRZZXM3XO%2FroPM5cqNRaMS5ybAD1wP2lFWCAAtvUmxQvdBsd80V8qw580V%2FBoFjdiWfKcUO2CtUjGhbUpZajnJ8LcaY3ybZuct3u2mHGCPpSOUOyoYyWnl7V9GczEBKxPGAtXP7Lajq2iD%2F5g4aAV2cyMxA%2FIBQz32oFsB8uzJlMzU%2B1hUou525uFlNDL%2BNy6ieeH9m9vGfRAFhqq%2BMihKBl4AE490jXTJG8GlSrYJayoCftOr7jPYkSixW9fVRBEgrhi6T%2BsTij62Ygig%2B5u6yl%2FrSgcnhPUOX9EGo4rx6N7mKDxnbY5KETs%2BwG9TkODS5xSKZzHKbYZqd%2B9I%2Bv4e7b47uaJIZPm9lUCONcFUd1jeGbqVlldrtzeugn16vM5lIbeJu6G12EXGH%2FhAWSs7OANXH8YLNXS737vYLweFzqyEnu7cDafWndqd8pAy8KGNNqbH4o17ADLXV5aRA6Z8WeJeWdMxFQV23BS%2BpQ0kV4B1FpfBLdNdOubspwYd61H7vxMIXmpwC2nfxb5StcvhdaQ1UT76LKI7E%2BBDsf46H1QRoYjf0HAQushBJwrbSrvZP7hM0vYHz7bHptHqPW5o3twqbHgsjmadzVQMmGl1CLA6lljLnx3OlEDdZ5cyTUiKDhmZhY4p0RAi3%2FsmT5CQPmcujNab707DuBKyG8uSlxneLj%2B5IycdsvTqGMR0%2Bdl7wZk4rR3wfVrEVZcYW4k2IfukvGm8EXCkuF8HK95NTLlGuKArZ9omwGZ7jjQfn9b7VrnS%2FOFw--YjQ2z4HbNdWusOHT--SaGSEgdgTqvHGDhdHiTbWg%3D%3D; OMR_USER_LANG=EU-en; _session=HheGtDmB2w1klX6qnDIVAOozwBsBb4NQnDMXrCZXSPFLhgp%2FSFK576ATYhw3cadtK3bMlzIZ6KbP5UcZjpwERrGGu%2FiL6jzGzaTKK5eg%2Bx1pnLKhjjf6%2B2mAfNpXpVXXndoQp8KMUY%2FFCsEUfTTt1gwrCGBRnlnDFHIRy94zFiAcnxZJekpwYyXT1Rm4KQaWwRNKn3GZhs1AsUQSNHNesGYcivk0EFq8bHfRNFqvGamuGQNiG2O73n7YVnApkp5tloN37OusGvjfGMZ0DbVACcgDaxzG1DjPnu9EZ8ryrJK71suNxVxmypajKovggVNpOtMTsxUspmr%2Bx7vt9VWcnkSg7Hv8akGTU%2FAYPPs86e7kD1jU7rerC6MZD9SCIMllLe%2B%2B6lq8oKembbK70x8UEP7TRwTlS6Xixe5uqk45Rf8K0mGlK1AXugUs65mDBIuxpn9gryAO5XwT2QvSw2Jw7zRkRl3wrVsG4eMdV8NJXNCMnn2mFwFmDi%2BmKbeEyY6A2urrXqCBUnsBNkCJYpd%2BPEyiOnIsTEE%2By4h1HjLi13VYH2mWRBky3QLgZnd%2BFS4%2FL2OGY673kkCCWi8ICAAGfQ2c8YgfOIkHd6toxJorfmZAw69aBxXFY82MstQ2ru%2FiDi0jaJ9wfSGzCsUt7%2FuqlWalZDXe%2BWDuaV54f%2B%2B%2FmRFOzEKfHU9gHRkGgoVGoXux2me7x11le2HguvT0xD8b6I6j4JaUzSUBl3lKBY11jncmMVBCC0clRzndIT6QZj2PEtLHnIJXf7ZyXopzQ2EezsfUQ6%2FFF1O8lFsYqFni1Nra16eWem%2F1b7VL4nadnMFmFmCsK7Ao2uh0OE4cR3IuEvSFGDHv%2FiIJ3gNRdQ%2BKgXqiiYxCQe8J06stMNSNnqF3LDhyF8qVSa9h3I%2BU0bggMlPnNxIoZ4KPprN848ilJ8NfoaPc2GLLp8gdBg%2FiTpNWtRVxCed66a2UgTRzsDuNHnw1JwOiC0DAS1n0HGbVsAIzELuCnXAdk6yYs6QjeogwE6emIw6L3Vf2Ct7g2Ybg6B7G--4MTp5cmEEsIKQLhz--Y8AAJrY7J16PwvhWkYNWiQ%3D%3D',
            'If-None-Match': 'W/"db00db24f5657ad5823dbc91a3c68936"',
            'Referer': 'https://industrial.omron.eu/en/services-support/support/environmental-product-information',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        try:
            res = response.json()
            print(res, "--------")
            substanceQuantity = ''
            if res['results'] == []:
                df.loc[index, 'Results'] = 'Not Found'
                df.to_csv(path, index=False)
            else:
                for r in res['results']:
                    Results = 'Found'
                    SPNGrabbed = r['description']
                    rohsCompliant = r['rohs10_compliant']
                    rohsNotCompliant = r['rohs10_not_compliant']
                    reachSubstances = r['reach_substances']
                    rohslink = 'https://industrial.omron.eu/en/pdf/rohs/' + \
                        r['short_item_code']+'.pdf?directive=10'
                    reachlink = 'https://industrial.omron.eu/en/pdf/reach/' + \
                        r['short_item_code']+'.pdf'
                    if r['reach_substances'] == 'Yes':
                        substanceQuantity = str(r['svhc_1']) + ' ' + str(r['svhc_2']) + ' ' + str(r['svhc_3']) + ' ' + str(r['svhc_4']) + ' ' + str(
                            r['svhc_5']) + ' ' + str(r['svhc_6']) + ' ' + str(r['svhc_7']) + ' ' + str(r['svhc_8']) + ' ' + str(r['svhc_9']) + ' ' + str(r['svhc_10'])
                    return {"Results": Results, "SPNGrabbed": SPNGrabbed, "rohsCompliant": rohsCompliant, "rohsNotCompliant": rohsNotCompliant, "reachSubstances": reachSubstances, "rohslink": rohslink, "reachlink": reachlink, "substanceQuantity": substanceQuantity}
                    # else:
                    #     return {"status": 404}
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_vishay(self, partNumber):
        """
        Scrape information from the Vishay website for a given part number.

        Args:
            partNumber (str): The part number to search for.

        Returns:
            dict or None: A dictionary containing information about the part, or None if the part was not found.
        """

        try:
            # Construct the search query URL for the given part number
            search_url = 'https://www.vishay.com/search/?searchChoice=part&query=' + partNumber

            # Send a GET request to the search URL and parse the response with BeautifulSoup
            search_response = requests.get(search_url)
            soup = BeautifulSoup(search_response.text, 'html.parser')

            # Find all product links in the search results
            links = soup.select('.Table_listTable__2PExR td:nth-of-type(1) a')

            # Iterate over the product links and scrape information from each page
            for link in links:
                # Construct the URL for the product page
                link_url = "https://www.vishay.com/" + link['href']

                # Send a GET request to the product page and parse the response with BeautifulSoup
                product_response = requests.get(link_url)
                product_soup = BeautifulSoup(product_response.text, 'lxml')

                # Extract the part name and datasheet link from the product page
                partName = product_soup.find('h1').text
                datasheet = product_soup.find(
                    'td', text='Datasheet').find_next_sibling('td').find('a')['href']
                datasheet_link = "https://www.vishay.com/" + datasheet

                # Extract the sub-title from the product page
                sub_title = product_soup.find('div', class_='ppgHead').text

                # Send a GET request to the quality information tab and parse the response with BeautifulSoup
                quality_tab = requests.get(link_url + "/tab/quality/")
                quality_soup = BeautifulSoup(quality_tab.text, 'lxml')

                # Extract the quality information from the tab
                table = quality_soup.find(
                    'table', class_='Table_listTable__2PExR')
                headers = table.find_all('th')
                headers = [header.text.strip() for header in headers]
                rows = table.find_all('tr')[1:]

                items = list()
                for row in rows:
                    # Create a dictionary to store the quality information for a single part
                    item = {}

                    for index, td in enumerate(row.find_all('td')):
                        # Extract the quality information and store it in the dictionary
                        if headers[index] == 'Part Number':
                            item["PartNumber"] = td.text
                        elif headers[index] == 'RoHS-Compliant':
                            item["RoHSCompliant"] = td.text
                        elif headers[index] == 'Lead (Pb)-Free':
                            item["leadFree"] = td.text

                    # If the dictionary is not empty, add the part name, datasheet link, and dictionary to the list of items
                    if item != {}:
                        item["Results"] = 'Found'
                        item["PartName"] = partName
                        item["Datasheet"] = datasheet_link
                        items.append(item)
                        print(items)
                        # If the part number matches the one provided by the user, return the dictionary
                        print("-------in service ---------", item)
                        return item
        except (IndexError, AttributeError, requests.exceptions.MissingSchema):
            print('part number is not found on server')
            return {"status": 404}

    def scrap_alliedelectronics(self, partNumber):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }

        url = 'https://www.alliedelectronics.com/mm5/json.mvc?Store_Code=Allied04&Function=Module&Module_Code=cmp-cssui-searchfield&Module_Function=Search'

        data = {'Search': partNumber, 'Count': 5, 'Session_Type': 'runtime'}
        try:
            response = requests.post(url, headers=headers, data=data)
            json_data = response.json()
            if json_data:
                result_url = json_data.get('data', [])[0].get('product_link')
                prod_resp = requests.get(result_url, headers=headers)

            soup = BeautifulSoup(prod_resp.text, 'lxml')

            spec_a = soup.find('a', text='Product Specifications')
            result = {
                "Results": "Found",
                'partNumber': soup.find('span', class_='part-no').text,
                'partName': soup.find('h1', class_='normal nm').text,
                'productSpecifications': spec_a.attrs['href'] if spec_a else None
            }
            return result
        except IndexError:
            print('part number is not found on server')
            return {"status": 404}

    def scrap_rshughes(self, partNumber):

        # driver = webdriver.Chrome(options=options, service=Service)
        # driver.get("https://www.rshughes.com/search.html?q=" + partNumber)
        # # wait for the H1 WITH class called h2 to load
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "h2")))
        # # get the H1 element
        # part_name = driver.find_element(By.XPATH, "//h1[@class='h2']").text
        # part_number = driver.find_element(
        #     By.XPATH, "//h2[contains(@class,'text-gray')]").text
        # brand = driver.find_element(
        #     By.XPATH, "//li[./div[1]/span[contains(text(),'Brand')]]/div[2]").text
        # item = {
        #     "Results": "Found",
        #     'partNumber': part_number,
        #     'partName': part_name,
        #     'Brand': brand
        # }
        return

    def scrap_Arrow(self, partnumber):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        url = "http://api.arrow.com/itemservice/v4/en/search/token?login=assent1&apikey=e91ee2fc20668093198daaf7252a7208e06a428b551ac2e652c83ed5671aaaee&search_token=" + \
            str(partnumber)
        payload = {}
        headers = {}
        response = requests.request(
            "GET", url, headers=headers, timeout=1000, data=payload).json()
        results = response['itemserviceresult']['data']
        for res in results:
            try:
                for r in res['PartList']:

                    return {"Results": "Found", "MPN": r['partNum'], "Manufacturer": r['manufacturer']['mfrName']}
            except Exception as e:
                print(e)
                return {"status": 404}

    def find_Supplier(self, partnumber):

        suppliers = []
        result = []

        def Check_Response(supplier, response, foundlist):
            try:
                if response["Results"] == "Found":
                    print(supplier, response, "helloooooo world00----")
                    suppliers.append({"supplier": supplier, "data": response})
                    result.append(response)
            except Exception as e:
                pass

        # Checking the response of the scraped data from the two websites.
        response = self.scrap_festo(partnumber)
        Check_Response("Festo", response, suppliers)
        print("hello world in 1331", response)

        response = self.scrap_Arrow(partnumber)
        Check_Response("Arrow", response, suppliers)
        print("hello world in 000", response)

        response = self.scrap_omron(partnumber)
        Check_Response("Omron", response, suppliers)
        print("hello world in 222", response)

        response = self.scrap_Rscomponents(partnumber)
        Check_Response("RS-components", response, suppliers)
        print("hello world in 333", response)

        response = self.scrap_Maxim(partnumber)
        Check_Response("Maxim", response, suppliers)
        print("hello world in 5555", response)

        response = self.scrap_Molex(partnumber)
        Check_Response("Molex", response, suppliers)

        response = self.scrap_Wago(partnumber)
        Check_Response("Wago", response, suppliers)

        response = self.scrap_Te(partnumber)
        Check_Response("TE", response, suppliers)

        response = self.scrap_Phoenix(partnumber)
        Check_Response("Phoenix", response, suppliers)

        response = self.scrap_onsemi(partnumber)
        Check_Response("Onsemi", response, suppliers)

        response = self.scrap_mouser(partnumber)
        Check_Response("Mouser Electronics", response, suppliers)

        response = self.scrap_3m(partnumber)
        Check_Response("3M", response, suppliers)

        response = self.scrap_ti(partnumber)
        Check_Response("Texas Instruments", response, suppliers)

        response = self.scrap_murata(partnumber)
        Check_Response("Murata Manufacturing Co", response, suppliers)

        response = self.scrap_newark(partnumber)
        Check_Response("Newark Electronics Corporation", response, suppliers)

        response = self.scrap_festo(partnumber)
        Check_Response("Festo", response, suppliers)
        print(suppliers, "hellooo world bro ")
        return suppliers

# get multi parts number response from csv data. iterate parts on server side
    # ***************************************  Wago data from csv.  ***********************************************
    def scrap_Wagos(self, partnumbers):
        scrapped_data = []
        partnumbers = ['793-501', '870-551', '210-111', '284-317', '284-601', '2006-1301', '2006-1391', '2009-115', '209-112', '282-122', '2006-1307', '282-311', '281-687', '2000-1207', '249-119', '2000-410', '2002-1201', '2000-1291', '2000-405',
                       '2000-403', '2000-404', '210-112', '2000-402', '793-502', '209-113', '2002-1202', '870-553', '249-120', '210-113', '793-503', '249-121', '209-114', '2002-1203', '793-504', '870-554', '210-114', '209-115', '249-122', '2002-1204', '210-115']
        for partnumber in partnumbers:
            print(partnumber)
            url = requests.get("https://smartdata.wago.com/articledata/svhc?articleNr=" +
                               urllib.parse.quote(str(partnumber), safe="") + "&country=Germany")
            print(url)
            soup = BeautifulSoup(url.text, 'lxml')
            try:

                table = soup.find(id="articleList")

                spn_grabbed = table.tbody.tr.td.text
                description = table.tbody.tr.td.find_next('td').text
                reach_substance = table.tbody.tr.td.find_next(
                    'td').find_next('td').text
                scip = table.tbody.tr.td.find_next(
                    'td').find_next('td').find_next('td').text
                cas_no = table.tbody.tr.td.find_next('td').find_next(
                    'td').find_next('td').find_next('td').text
                rohs_status = table.tbody.tr.td.find_next('td').find_next(
                    'td').find_next('td').find_next('td').find_next('td').text
                rohs_exception = table.tbody.tr.td.find_next('td').find_next('td').find_next(
                    'td').find_next('td').find_next('td').find_next('td').text

                scrapped_data.append({"Results": "Found", "Partnumber": partnumber, "PartName": description, "SPN_grabbed": spn_grabbed, "Reach": reach_substance, "Scip": scip, "Cas_no": cas_no,
                                     "ROHS_Exception": rohs_exception, "ROHS_Status": rohs_status, "Declaration": "https://smartdata.wago.com/articledata/svhc/download?articleNr=" + spn_grabbed + "&country=Austria"})

            except Exception as e:
                print(e)
                scrapped_data.append({"status": 404})

        return scrapped_data

    # ***************************************  scrap_Molex data from csv.  ***********************************************
    def scrap_Molexs(self, partnumbers):
        print(partnumbers)
        scrapped_data = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        for partnumber in partnumbers:
            print(partnumber)
            url = "https://www.molex.com/molex/search/partSearch?query=" + \
                urllib.parse.quote(str(partnumber), safe="") + "&pQuery="
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            try:
                partname = soup.find(
                    "div", class_="col-md-10").find("h1").text
                status = soup.find("p", class_="info").find(
                    "span", class_="green").text
                series = soup.find("a", class_='text-link').text
                rohs = soup.find(
                    "div", id="tab-environmental").find_all("p")[1].text
                reach = soup.find(
                    "div", id="tab-environmental").find_all("p")[3].text
                halogen = soup.find(
                    "div", id="tab-environmental").find_all("p")[4].text
                link = soup.find(
                    "div", id="tab-environmental").find_all("p")[8].find("a", href=True)
                declaration = link['href']
                scrapped_data.append(
                    {"Results": "Found",
                     "MPN": "",
                     "PArtname": partname.strip(),
                     "Status": status.strip(),
                        "Series": series.strip(),
                     "ROHS": rohs.strip(),
                     "REACH": reach.strip(),
                     "HALOGEN": halogen.strip(),
                     "Declaration": declaration.strip()}
                )
                print(scrapped_data)
                # return {"Results": "Found", "MPN": mpn, "PArtname": partname, "Status": status, "Series": series, "ROHS": rohs, "REACH": reach, "HALOGEN": halogen, "Declaration": declaration}

            except Exception as e:
                scrapped_data.append(
                    {"Results": "Not Found",
                     "MPN": "",
                     "PArtname": partnumber,
                     "Status": "",
                        "Series": "",
                     "ROHS": "",
                     "REACH": "",
                     "HALOGEN": "",
                     "Declaration": ""}
                )
                # return {"status": 404}
        print(scrapped_data)
        return scrapped_data

    # ***************************************  scrap_yuden data from csv.  ***********************************************

    def scrap_yuden(self, partnumber):
        url = 'https://ds.yuden.co.jp/TYCOMPAS/or/detail?pn='+partnumber+'&u=M'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        result = {}
        try:
            result = {
                "Results": "Found",
                'Part Number': partnumber,
                'Cateogry': soup.find(id="ClassificationSeriesArea").get_text(strip=True),
                'Status': soup.find(string="Status").find_next('td').get_text(strip=True),
                'RoHS': soup.find(string="RoHS Compliance (10 subst.)").find_next('td').get_text(strip=True),
                # 'REACH': soup.find(string="REACH Compliance (233 subst.)").find_next('td').get_text(strip=True),
            }
        except AttributeError as e:
            print('part number is not found on server.', e)
            return {'status': 404}

        return result
    # ***************************************  scrap_semtech data from csv.  ***********************************************

    def scrap_semtech(self, partnumber):
        url = 'https://www.semtech.com/quality/search-pb-lead-free-rohs-green?prodNumbers='+partnumber
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        result = {}
        try:
            result = {
                "Results": "Found",
                'Part Number': partnumber,
                'Part Description': soup.find(string='Part Description').find_next('span').get_text(strip=True),
                # 'REACH SVH C(224) EC1907/2006': soup.find(string='REACH SVH C(224) EC1907/2006 ').find_next('span').get_text(strip=True).replace("Download Report", ""),
                # 'REACH PDF URL': soup.find(string='REACH SVH C(224) EC1907/2006 ').find_next('span').find_next('a')['href'],
                'RoHS 2/3 Amend 2015/863': soup.find(string='RoHS 2/3 Amend 2015/863 ').find_next('span').get_text(strip=True).replace("Download Report", ""),
                'RoHS 2/3 Amend 2015/863 PDF URL': soup.find(string='RoHS 2/3 Amend 2015/863 ').find_next('span').find_next('a')['href'],
                'Halogen Free / Low IEC 61249-2-21/JS709C': soup.find(string='Halogen Free / Low IEC 61249-2-21/JS709C ').find_next('span').get_text(strip=True).replace("Download Report", ""),
                'RoHS Compliant by Exception': soup.find(string='RoHS Compliant by Exception ').find_next('span').get_text(strip=True)
            }
        except AttributeError as e:
            print('part number is not found on server.', e)
            return {'status': 404}

        return result
    # ***************************************  scrap_radiall data from csv.  ***********************************************

    def scrap_radiall(self, partnumber):
        url1 = 'https://www.radiall.com/catalogsearch/advanced/result/?sku='+partnumber
        url2 = 'https://www.radiall.com/rohs?part_number='+partnumber
        url3 = 'https://www.radiall.com/short-size-gps-l1-active-sma-'+partnumber+'.html'
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        response3 = requests.get(url3)
        soup1 = BeautifulSoup(response1.text, 'lxml')
        soup2 = BeautifulSoup(response2.text, 'lxml')
        soup3 = BeautifulSoup(response3.text, 'lxml')
        result = {}
        result['Part Number'] = partnumber
        try:
            result['Part Name'] = soup1.find(
                string=partnumber).find_next('td').get_text(strip=True)
            result['Results'] = 'Found'
        except AttributeError:
            result['Part Name'] = '404 Not Found'
        try:
            result['RoHS directive 2011/65EU & 2015/863EU (Exemption used)'] = soup2.find(
                'td').find_next('td').get_text(strip=True)
        except AttributeError:
            result['RoHS directive 2011/65EU & 2015/863EU (Exemption used)'] = '404 Not Found'
        try:
            result['Non RoHS substance'] = soup2.find('td').find_next(
                'td').find_next('td').get_text(strip=True)
        except AttributeError:
            result['Non RoHS substance'] = '404 Not Found'
        try:
            result['Presence SVHC > 0.1% w/W'] = soup2.find('td').find_next(
                'td').find_next('td').find_next('td').get_text(strip=True)
        except AttributeError:
            result['Presence SVHC > 0.1% w/W'] = '404 Not Found'
        try:
            result['SVHC identification'] = soup2.find('td').find_next('td').find_next(
                'td').find_next('td').find_next('td').get_text(strip=True)
        except AttributeError:
            result['SVHC identification'] = '404 Not Found'
        try:
            result['RoHS Declaration'] = soup3.find(
                'span', class_='rohs-icon').find_next('a')['href']
        except AttributeError:
            result['RoHS Declaration'] = '404 Not Found'
        if (result['Non RoHS substance'] == ''):
            result['Non RoHS substance'] = 'Not Available'
        # try:
        #   result = {
        #       'Part Number': partnumber,
        #       'Part Name': soup1.find(string=partnumber).find_next('td').get_text(strip=True),
        #       'RoHS directive 2011/65EU & 2015/863EU (Exemption used)': soup2.find('td').find_next('td').get_text(strip=True),
        #       'Non RoHS substance': soup2.find('td').find_next('td').find_next('td').get_text(strip=True),
        #       'Presence SVHC > 0.1% w/W': soup2.find('td').find_next('td').find_next('td').find_next('td').get_text(strip=True),
        #       'SVHC identification': soup2.find('td').find_next('td').find_next('td').find_next('td').find_next('td').get_text(strip=True),
        #       'RoHS Declaration': soup3.find('span', class_='rohs-icon').find_next('a')['href']
        #   }
        #   if(result['Non RoHS substance'] == ''):
        #     result['Non RoHS substance'] = 'Not Available'
        # except AttributeError:
        #   result['Error'] = '404 Not Found'
        #   return result

        return result
    # ***************************************  scrap_belfuse data from csv.  ***********************************************

    def scrap_belfuse(self, partnumber):
        url = 'https://www.belfuse.com/product/part-details?partn='+partnumber

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        result = {}
        try:
            result = {
                "Results": "Found",
                'Part Number': partnumber,
                'Part Name': soup.find('p', class_='product-details-description expander-truncate').get_text(strip=True),
                'Category': soup.find(string="Home").find_next("a").get_text(strip=True),
                'Datsheet(pdf)': 'https://www.belfuse.com'+soup.find('a', class_='view-datasheet-button btn btn-blue')["href"],
                # 'RoHS Declaration': 'https://www.belfuse.com'+soup.find('a', class_='Bel_Fuse-Circuit_Protection-Others')["href"]
            }

        except AttributeError:
            print('part number is not found on server.')
            return {'status': 404}

        return result

    # ***************************************  scrap_onsemi data from csv.  ***********************************************
    def scrap_onsemis(self, partnumbers):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        try:
            response = requests.get(
                "https://www.onsemi.com/PowerSolutions/MaterialComposition.do?searchParts=" + urllib.parse.quote(str(partnumber), safe=''), headers=headers)
            data = BeautifulSoup(response.text, 'lxml')
            table = data.find(id="MaterialCompositionTable")
            pn = table.tbody.tr.td.find_next('td').text
            status = table.tbody.tr.td.find_next('td').find_next('td').text
            hf = table.tbody.tr.td.find_next(
                'td').find_next('td').find_next('td').text
            excempt = table.tbody.tr.td.find_next('td').find_next(
                'td').find_next('td').find_next('td').text
            links = table.find_all('a', href=True)
            declaration = "https://www.onsemi.com" + links[5]['href']
            lead = "not found"
            if len(excempt) > 1:
                lead = table.tbody.tr.td.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next(
                    'td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text

            return {"Results": "Found", "SPN_grabbed": pn, "Status": status, "HF": hf, "Excemption": excempt, "Declaration": declaration, "Lead(Cas No:7439-92-1)": lead}

        except Exception as e:
            return {"status": 404}

    # ***************************************  scrap_Maxim data from csv.  ***********************************************
    def scrap_Maxims(self, partnumbers):
        part = re.sub.replace(":", "/", partnumber)
        print(part)
        url = requests.get(
            "https://www.maximintegrated.com/en/qa-reliability/emmi/content-lookup/product-content-info.html?partNumber=" + urllib.parse.quote(str(part)))
        soup = BeautifulSoup(url.text, 'lxml')
        try:
            table = soup.find(id="productcontentinfo")
            Rohs_Compliance = table.tbody.tr.td.find_next('td').text
            Rohs2_compliance = table.tbody.tr.td.find_next(
                'tr').td.find_next('td').text
            Halogen_compliance = table.tbody.tr.find_next(
                'tr').find_next('tr').td.find_next('td').text
            Reach_Compliance = table.tbody.tr.find_next('tr').find_next(
                'tr').find_next('tr').td.find_next('td').text
            print(Rohs_Compliance, Rohs2_compliance,
                  Halogen_compliance, Reach_Compliance)
            return {"Results": "Found", "Partnumber": part, "Rohs_Compliance": Rohs_Compliance, "Rohs2_compliance": Rohs2_compliance, "Halogen_compliance": Halogen_compliance, "Reach_Compliance": Reach_Compliance}
        except Exception as e:
            print(e)
            return {"status": 404}

    # ***************************************  scrap_Phoenix data from csv.  ***********************************************
    def scrap_Phoenixs(self, partnumbers):
        try:
            url = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/products?_locale=en-CA&_realm=ca&offset=0&requestedSize=11"
            reporturl = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/report/guid?_locale=en-CA&_realm=ca"

            # payload = "{\"searchItems\":[\"1084745\"]}"
            payload = '{\"searchItems\":[\"' + \
                urllib.parse.quote(str(partnumber)) + '\"]}'
            headers = {
                'authority': 'www.phoenixcontact.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,de;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://www.phoenixcontact.com',
                'pragma': 'no-cache',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', }

            response = requests.request(
                "POST", url, headers=headers, data=payload)
            report_response = requests.request(
                "POST", reporturl, headers=headers, data=payload)
            link = "https://www.phoenixcontact.com/customer/api/v1/product-compliance/report/guid/" + \
                report_response.text + "?_locale=en-US&_realm=us"

            res = response.json()

            for results in res['items'].values():

                if results["validItem"] == False:
                    return {"status": 404}
                else:
                    return results
        except Exception as e:
            print(e)
            return {"status": 404}
    # ***************************************  scrap_alphawire data from csv.  ***********************************************

    def scrap_alphawire(self, partnumber):
        partnumber = partnumber.replace("&45F", "/")
        url = "https://www.alphawire.com/"
        search_url = f"{url}//sxa/search/results"
        ro_hs_declaration_url = f"{url}/RohsSearch/PrintRoHS?productPartNumber="
        payload = {
            "l": "en",
            "s": "{4A774076-6068-460C-9CC6-A2D8E85E407F}",
            "itemid": "{BF82F58C-EFD9-4D8B-AE3E-097DD12CF7DA}",
            "autoFireSearch": "true",
            'productpartnumber': f"{partnumber}",
            "v": "{B22CD56D-AB95-4048-8AA1-5BBDF2F2D17F}",
            "p": 10,
            "e": 0,
            "o": "ProductPartNumber,Ascending",
        }
        response = requests.get(search_url, params=payload)
        data = response.json()
        if not data["Results"]:
            print('part number is not found on server')
            return {'status': 404}
        for product in data["Results"]:
            soup = BeautifulSoup(product["Html"], "html.parser")

            product_number = soup.find(
                "span", class_="field-productpartnumber"
            ).text
            product_name = soup.find("h5").text
            result = {
                "Results": "Found",
                'Part Number': product_number,
                'Part Name': product_name,
                'RoHS Status': 'Yes',
                'RoHS Declaration': f"{ro_hs_declaration_url}{product_number}"
            }
            return result

         # ***************************************  scrape_sager data from web.  ***********************************************

    def scrap_sager(self, part_number):
        options = uc.ChromeOptions()

        options.add_argument("--headless")
        options.add_argument("--start-maximized")

        base_url = "https://www.sager.com/"

        with uc.Chrome(options=options) as driver:
            try:
                driver.get(base_url)
                sleep(1)

                input_field = driver.find_element(By.ID, "txtPtSearch")

                input_field.send_keys(part_number)

                input_field.send_keys(Keys.ENTER)

                sleep(2)

                part_name = driver.find_element(
                    By.ID,
                    "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_lblShortDescription",
                ).text

                manufacturer = (
                    driver.find_element(
                        By.XPATH, "//th/span[contains(text(), 'Manufacturer')]"
                    )
                    .find_element(By.XPATH, "../following-sibling::td")
                    .text
                )

                manufacturers_part = (
                    driver.find_element(
                        By.XPATH, "//*[contains(text(), 'Manufacturers Part #')]"
                    )
                    .find_element(By.XPATH, "../following-sibling::td")
                    .text
                )
                lead_time = "N/A"
                if driver.find_elements(
                    By.XPATH, "//th/span[contains(text(), 'Lead Time')]"
                ):
                    lead_time = (
                        driver.find_element(
                            By.XPATH, "//th/span[contains(text(), 'Lead Time')]"
                        )
                        .find_element(By.XPATH, "../following-sibling::td")
                        .text
                    )
                sub_category = "N/A"
                if driver.find_elements(
                    By.XPATH, "//th/span[contains(text(), 'Sub-Category')]"
                ):
                    sub_category = (
                        driver.find_element(
                            By.XPATH, "//th/span[contains(text(), 'Sub-Category')]"
                        )
                        .find_element(By.XPATH, "../following-sibling::td")
                        .text
                    )
                elif driver.find_elements(
                    By.XPATH, "//th/span[contains(text(), 'Sub-Categories')]"
                ):
                    sub_category = (
                        driver.find_element(
                            By.XPATH, "//th/span[contains(text(), 'Sub-Categories')]"
                        )
                        .find_element(By.XPATH, "../following-sibling::td")
                        .text
                    )
                brand = "N/A"
                if driver.find_elements(By.XPATH, "//th/span[contains(text(), 'Brand')]"):
                    brand = (
                        driver.find_element(
                            By.XPATH, "//th/span[contains(text(), 'Brand')]"
                        )
                        .find_element(By.XPATH, "../following-sibling::td")
                        .text
                    )
                series = "N/A"
                if driver.find_elements(By.XPATH, "//th/span[contains(text(), 'Series')]"):
                    series = (
                        driver.find_element(
                            By.XPATH, "//th/span[contains(text(), 'Series')]"
                        )
                        .find_element(By.XPATH, "../following-sibling::td")
                        .text
                    )

                rohs = "N/A"
                if driver.find_elements(
                    By.ID,
                    "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconRohs",
                ):
                    rohs = driver.find_element(
                        By.ID,
                        "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconRohs",
                    ).text
                elif driver.find_elements(
                    By.ID,
                    "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconNotRohs",
                ):
                    rohs = driver.find_element(
                        By.ID,
                        "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconNotRohs",
                    ).text

                datasheet = "N/A"

                if driver.find_elements(
                    By.ID,
                    "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_specsURL",
                ):
                    datasheet = driver.find_element(
                        By.ID,
                        "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_specsURL",
                    ).get_attribute("href")

                result = {
                    "Results": "Found",
                    "Part Number": part_number,
                    "Part Name": part_name,
                    "Manufacturer": manufacturer,
                    "Manufacturers Part #": manufacturers_part,
                    "Lead Time": lead_time,
                    "Sub-Category": sub_category,
                    "Brand": brand,
                    "Series": series,
                    "RoHS Compliant": rohs,
                    "Datasheet": datasheet,
                }

                return result
            except Exception as exc:
                print(f"Part {part_number} is not found on server.", exc)
                return {"status": 404}
         # ***************************************  scrap_analog data from web.  ***********************************************

    def scrap_analog(self, part_number):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        columns = [
            "Part Number",
            "Part Name",
            "Category",
            "RoHS Compliant Status",
            "Material Declaration",
            "Datasheet",
        ]
        base_url = "https://www.analog.com"
        print(f"Scraping data for part number: {part_number}")
        url = f"https://www.analog.com/en/products/{part_number}.html#product-overview"

        driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
        driver.implicitly_wait(2)
        driver.get(url)
        try:
            analog_part_number = driver.find_element(
                By.CLASS_NAME, "adi-pdp__product__name__generic"
            ).text

            analog_part_name = driver.find_element(
                By.CLASS_NAME, "adi-pdp__product__description"
            ).text.split("\n")[0]
            categories = driver.find_elements(
                By.XPATH, "//a[@class='category']")

            category = ", ".join(
                [
                    category.accessible_name
                    for category in categories
                ]
            )

            datasheet = 'N/A'
            datasheet_div = driver.find_elements(
                By.XPATH, "//div[@class='datasheet primary dropdown']//a"
            )
            if datasheet_div:
                datasheet = datasheet_div[0].get_attribute('href')

            material_declaration = f"https://quality.analog.com/viewdeclaration.aspx?pkgcode=C272C3%2b1&partNumber={part_number}%2b"

            driver.get(material_declaration)

            rohs_label = driver.find_element(
                By.XPATH, "//*[contains(text(),'RoHS')]")

            rohs_status = rohs_label.find_element(
                By.XPATH, "following-sibling::td").text

            result = {
                "Results": "Found",
                "Part Number": analog_part_number,
                "Part Name": analog_part_name,
                "Category": category,
                "RoHS Compliant Status": rohs_status,
                "Material Declaration": material_declaration,
                "Datasheet": datasheet,
            }
            print(f"Data successfully scraped for part number: {part_number}")
        except Exception as exc:
            print(f"Part {part_number} is not found on server.", exc)
            return {"status": 404}
        return result

 # ***************************************  scrape_littelfuse data from csv.  ***********************************************

    def scrape_littelfuse(self, part_number):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
        base_url = "https://www.littelfuse.com/"
        driver.get(base_url)
        try:
            input_field = driver.find_element(
                By.XPATH, '//div[@class="magic-box-input"]/input'
            )

            input_field.send_keys(part_number)

            input_field.send_keys(Keys.ENTER)

            sleep(2)
            search_results = driver.find_elements(
                By.CLASS_NAME, "CoveoResultLink")

            part_url = search_results[0].get_attribute("href")

            driver.get(part_url)

            part_name = driver.find_element(By.TAG_NAME, "h1").text

            series = driver.find_element(
                By.XPATH, "//span[contains(text(), 'Series: ')]/a"
            ).text

            datasheet = "N/A"

            if driver.find_elements(
                By.XPATH,
                "//div[@class='feaures-benefits-box']//a[contains(text(), 'sheet')]",
            ):
                datasheet = driver.find_element(
                    By.XPATH,
                    "//div[@class='feaures-benefits-box']//a[contains(text(), 'sheet')]",
                ).get_attribute("href")
            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Series": series,
                "DataSheet": datasheet,
            }
        except Exception as exc:
            print(f"Part {part_number} is not found on server.", exc)
            return {"status": 404}

        return result

 # ***************************************  scrap_tti data from csv.  ***********************************************

    def scrap_tti(self, part_number):
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1"}

        url = f"https://www.tti.com/content/ttiinc/en/apps/part-detail.html?partsNumber={part_number}"

        response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            tti_part_number = soup.find(
                "span", string="TTI Part Number: "
            ).next_sibling.get_text(strip=True)

            mfr_part_number = soup.find(
                "span", string="Mfr Part Number: "
            ).next_sibling.get_text(strip=True)

            manufacturer = soup.find(
                "a", {"id": "manufacturerName"}).get_text(strip=True)

            rohs_status = soup.find(
                "span", string="RoHS Compliant").next_sibling.contents[0]

            reach_svhc = soup.find("span", string="REACH SVHC").next_sibling.get_text(
                strip=True
            )

            reach_substance_name = soup.find(
                "span", string="REACH Substance Name"
            ).next_sibling.get_text(strip=True)

            datasheet = soup.find("h3", string="Datasheet")

            if datasheet:
                datasheet_pdf = soup.find("a", string="Datasheet")["href"]
            else:
                datasheet_pdf = "N/A"
            result = {
                "Results": "Found",
                "TTI Part Number": tti_part_number,
                "Mfr Part Number": mfr_part_number,
                "Manufacturer": manufacturer,
                "RoHS Compliant Status": rohs_status,
                "REACH SVHC": reach_svhc,
                "REACH Substance Name": reach_substance_name,
                "Datasheet": datasheet_pdf,
            }
        except AttributeError:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

        return result

    # ***************************************  scrap_pemnet data from csv.  ***********************************************

    def scrap_pemnet(self, part_number):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        url = f"https://www.pemnet.com/eu/products/product-finder/{part_number}/"

        response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            datasheet = 'Not available'
            if soup.find("div", class_="wp-block-button product__button product__sheets"):
                datasheet = soup.find(
                    "div", class_="wp-block-button product__button product__sheets"
                ).find_next("a")["href"]
            brand = 'Not available'
            if soup.find('dt', string='Brand'):
                brand = soup.find(
                    'dt', string='Brand').next_sibling.get_text(strip=True)
            result = {
                "Results": "Found",
                "Part Number": soup.find(
                    "h1", class_="product__sku product__sku--desktop"
                ).get_text(strip=True),
                "Product Category": soup.find(
                    "dt", string="Product Category"
                ).next_sibling.get_text(strip=True),
                "Brand": brand,
                "Datasheet": datasheet,
            }
        except AttributeError:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

        return result

    def scrape_boeing(self, part_number):
        try:
            print(f"Scraping data for part number: {part_number}")
            url = "https://shop.boeing.com/aviation-supply/search?text={part_number}"
            payload = {}
            headers = {
                'authority': 'shop.boeing.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36'
            }

            response = requests.request(
                "GET", url, headers=headers, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            mpn = soup.find(
                'div', class_='product-item-details').find('span').text.strip()
            manufacturer = soup.find(
                'div', class_='product-item-details').find('a', class_='level5').text.strip()
            input_tag = soup.find('input', {'id': 'adobePLPProduct'})
            # Extract the value of the "value" attribute
            pn = input_tag['value']
            print(mpn, manufacturer, pn)
            result = {
                "Results": "Found",
                "Part Number": pn,
                "mpn": mpn,
                "Manufacturer": manufacturer
            }
        except Exception as e:
            print(f"Part {part_number} is not found on server.", e)
            raise ValueError({"Results": "Found"})
        return result
    # ***************************************   scrape_avnet data from csv.  ***********************************************

    def scrape_avnet(self, part_number):
        apiKey = "cad4b7e61ea2ff5bfab980cb8bb888b0"
        print(f"Scraping data for part number: {part_number}")
        payload = {
            "api_key": apiKey,
            "url": f"https://www.avnet.com/shop/us/search/{part_number}",
            "render": "true",
        }
        try:
            resp = requests.get("http://api.scraperapi.com",  # here this api request is not responding (BUG).
                                params=payload, timeout=160)
            soup = BeautifulSoup(resp.content, "html.parser")
            if "Search Result" in soup.title.get_text():
                product_name_divs = soup.find_all("div", class_="product-name")

                for product_name_div in product_name_divs:
                    product_name_link = product_name_div.find("a", href=True)
                    manufacturer_part = product_name_div.find_next(
                        "strong", string="Avnet Manufacturer Part #:"
                    )
                    if (
                        manufacturer_part
                        and manufacturer_part.next_sibling.get_text(strip=True)
                        == part_number
                    ):
                        payload["url"] = product_name_link["href"]
                        print("------here------")
                        resp = requests.get(
                            "http://api.scraperapi.com", params=payload, timeout=60
                        )
                        soup = BeautifulSoup(resp.content, "html.parser")
                        break
            part_name = soup.find(
                "h2", class_="black regular").get_text(strip=True)
            manufacturer = "N/A"
            if soup.find("strong", string="Manufacturer:"):
                manufacturer = soup.find(
                    "strong", string="Manufacturer:"
                ).next_sibling.get_text(strip=True)

            product_category = "N/A"

            if soup.find("div", {"class": "product-category"}):
                categories = [
                    el.get_text(strip=True)
                    for el in soup.find("div", {"class": "product-category"}).find_all("a")
                ]
                product_category = ", ".join(categories)

            life_cycle = "N/A"

            if soup.find("span", string="Lifecycle"):
                life_cycle = "Yes"

            rohs = "N/A"
            if soup.select('span:-soup-contains("RoHS")'):
                rohs = soup.select(
                    'span:-soup-contains("RoHS")')[0].get_text(strip=True)

            datasheet = "N/A"

            if soup.find("a", {"id": "WC_TechnicalSpecification_Image_2_"}):
                datasheet = soup.find(
                    "a", {"id": "WC_TechnicalSpecification_Image_2_"}
                ).get("href")

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Manufacturer": manufacturer,
                "Product Category": product_category,
                "RoHS": rohs,
                "Lifecycle": life_cycle,
                "Datasheet": datasheet,
            }
        except Exception as e:
            print(f"Part {part_number} is not found on server.", e)
            return {"status": 404}
        return result
    # ***************************************  scrape distrelec data from csv.  ***********************************************

    def scrape_distrelec(self, part_number):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        driver = uc.Chrome(options=options)
        base_url = "https://www.distrelec.de/"
        print(f"Scraping data for part number: {part_number}")
        try:
            driver.implicitly_wait(2)
            driver.get(base_url)  # unable to connect with this (BUG)
            print("hello world---")
            accept_cookies_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ensCloseBanner"))
            )
            accept_cookies_button.click()

            # looking for input to enter part number to look for
            input_field = driver.find_element(By.ID, "metahd-search")

            input_field.send_keys(part_number)

            submit_button = driver.find_element(By.CLASS_NAME, "btn-search")

            submit_button.click()

            article_number = "N/A"
            if driver.find_elements(By.ID, "article-number-text"):
                article_number = (
                    driver.find_element(By.ID, "article-number-text")
                    .find_element(By.XPATH, "following-sibling::span")
                    .text
                )

            manufacturer = "N/A"
            if driver.find_elements(By.XPATH, "//span[text()='Manufacturer']"):
                manufacturer = (
                    driver.find_element(
                        By.XPATH, "//span[text()='Manufacturer']")
                    .find_element(By.XPATH, "following-sibling::span")
                    .text
                )

            brand = "N/A"

            if driver.find_elements(By.CLASS_NAME, "elem--brand"):
                brand = driver.find_element(By.CLASS_NAME, "elem--brand").text.lstrip(
                    "Brand: "
                )

            rohs_status = "N/A"
            if driver.find_elements(By.ID, "ROHS-title"):
                rohs_status = driver.find_element(By.ID, "ROHS-title").text

            rohs_declaration = "N/A"
            if driver.find_elements(By.ID, "ROHS-pdf-link"):
                onclick_text = driver.find_element(By.ID, "ROHS-pdf-link").get_attribute(
                    "onclick"
                )

                # Use regex to extract the URL part inside window.open()
                url_match = re.search(r"window\.open\('(.+?)'", onclick_text)
                if url_match:
                    rohs_declaration = f'{base_url.rstrip("/")}{url_match.group(1)}'
            reach_status = "N/A"
            if driver.find_elements(By.ID, "REACH-title-id"):
                reach_status = driver.find_element(
                    By.ID, "REACH-title-id").text
            reach_declaration = "N/A"
            if driver.find_elements(By.XPATH, "//a[text()='REACH Regulation Statement']"):
                reach_declaration = driver.find_element(
                    By.XPATH, "//a[text()='REACH Regulation Statement']"
                ).get_attribute("href")
            result = {
                "Results": "Found",
                "Distrelec Article Number": article_number,
                "Manufacturer": manufacturer,
                "Manufacturer Part Number": part_number,
                "Brand": brand,
                "RoHS Status": rohs_status,
                "RoHS Declaration": rohs_declaration,
                "REACH Regulation Status": reach_status,
                "REACH Regulation Declaration": reach_declaration,
            }
        except Exception:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}
        return result
    # ***************************************  scrape harwin data from csv.  ***********************************************

    def scrape_harwin(self, part_number):
        base_url = "https://www.harwin.com"
        product_url = f"{base_url}/products"
        form_data = {
            "action": "product_documents",
            "documents": "Array,REACH,CMRT-C,CRT-C,HF333",
            "document_keys": "rohs_compliant,reach,cmrt_0,cmrt_1,cmrt_2",
            "security": "39dcdf9c43",
        }
        admin_url = f"{base_url}/wp-admin/admin-ajax.php"
        print(f"Scraping data for part number: {part_number}")
        try:
            resp = requests.get(f"{product_url}/{part_number}", timeout=15)

            soup = BeautifulSoup(resp.content, "html.parser")

            details_div = soup.find("div", class_="product-page__details")
            part_name = "N/A"
            description = "N/A"
            if details_div:
                part_name = details_div.find_next("h2").get_text(strip=True)
                description = details_div.find_next("h3").get_text(strip=True)

            product_status = "N/A"
            if soup.find("span", class_="product-page__status"):
                product_status = soup.find("span", class_="product-page__status").get_text(
                    strip=True
                )

            rohs_status = "N/A"
            rohs_pdf = "N/A"
            reach_pdf = "N/A"
            if soup.find("h3", string="EU RoHS Status:"):
                rohs_status = (
                    soup.find("h3", string="EU RoHS Status:")
                    .find_next_sibling()
                    .get_text(strip=True)
                )
                rohs_pdf = (
                    soup.find("h3", string="EU RoHS Status:")
                    .find_next_sibling()
                    .find("a")["href"]
                )

            # fetching data from post request to get reach statment pdf

            resp1 = requests.post(admin_url, data=form_data, timeout=10)
            if resp1.status_code == 200:
                soup1 = BeautifulSoup(resp1.content, "html.parser")

                reach_href = soup1.select(
                    'h3:-soup-contains("REACH")')[0].find("a")["href"]
                reach_pdf = json.loads(reach_href.replace("\\", ""))

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Description": description,
                "Product Status": product_status,
                "EU RoHS Status": rohs_status,
                "RoHS Compliant(PDF)": rohs_pdf,
                "REACH statement(PDF)": reach_pdf,
            }
        except Exception:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

        return result
    # ***************************************  scrape index corp data from csv.  ***********************************************

    def scrape_index_corp(self, part_number):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        driver = uc.Chrome(options=options)
        print(f"Scraping data for part number: {part_number}")
        base_url = (
            f"https://www.idex-hs.com/store/search-results/1/?searchCriteria={part_number}"
        )
        try:
            # Error found .WebDriverException: Message: unknown error: cannot connect to chrome at 127.0.0.1:58569 (BUG)
            driver.get(base_url)
            print("---hellow--")
            product_link = None

            # close cookie modal
            if driver.find_elements(By.ID, "onetrust-close-btn-container"):
                close_btn = driver.find_element(
                    By.ID, "onetrust-close-btn-container")
                close_btn.click()

            # look for product with part_number from search results
            if driver.find_elements(
                By.XPATH,
                f"//span[. = '{part_number}']/ancestor::div[2]",
            ):
                product = driver.find_element(
                    By.XPATH,
                    f"//span[. = '{part_number}']/ancestor::div[2]",
                )
                product_link = product.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )

            if product_link is None:
                print(f"Part {part_number} is not found on server.")
                return {"status": 404}

            driver.get(product_link)

            part_name = "N/A"

            if driver.find_elements(By.TAG_NAME, "h1"):
                part_name = driver.find_element(By.TAG_NAME, "h1").text

            description = "N/A"
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.ID, "scj-html-content-ctl00-Container-C017")
                    )
                )
                description = element.text
            finally:
                pass

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Description": description,
            }
            print(f"Data successfully scraped for part number: {part_number}")
        except Exception:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}
        return result
    # ***************************************  scrape_st data from csv.  ***********************************************

    def scrape_st(self, part_number):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        # options.binary_location = '/usr/bin/chromedriver'
        options.add_argument("--window-size=1920,1080")
        base_url = "https://www.st.com"
        print(f"Scraping data for part number: {part_number}")
        driver = uc.Chrome(options=options)
        # with uc.Chrome(options=options) as driver:
        try:
            driver.implicitly_wait(2)
            # WebDriverException: Message: unknown error: cannot connect to chrome at 127.0.0.1:63951 (BUG)
            driver.get(base_url)

            search_form_button = driver.find_element(
                By.XPATH, '//form[@id="form-search"]/div'
            )
            search_form_button.click()

            input_field = driver.find_element(By.ID, "widgetSearchBar")

            input_field.send_keys(part_number)

            input_field.send_keys(Keys.ENTER)

            sleep(2)
            el = driver.find_element(
                By.XPATH, '//*[@id="search-table-products"]/tbody/tr'
            ).find_element(By.TAG_NAME, "a")
            el.click()

            quality_and_reliability = driver.find_element(
                By.XPATH, "//span[contains(text(), ' Quality & Reliability ')]"
            )
            quality_and_reliability.click()
            part_name = driver.find_element(
                By.CLASS_NAME, "st-stage-product__copy"
            ).text

            product = driver.find_element(
                By.XPATH, f"//tr/td[contains(text(), '{part_number}')]"
            )
            product_row = product.find_elements(By.XPATH, "../td")
            product_status = product_row[1].text
            rohs_compliance_grade = product_row[-2].text
            material_declaration = "N/A"
            mat_declaration_tag = product_row[-1].find_elements(
                By.TAG_NAME, "a")
            if mat_declaration_tag:
                material_declaration = mat_declaration_tag[0].get_attribute(
                    "href")

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Status": product_status,
                "RoHS Compliant Status": product_status,
                "RoHS Compliance Grade": rohs_compliance_grade,
                "Material Declaration": material_declaration,
            }
            print(
                f"Data successfully scraped for part number: {part_number}")
        except Exception as exc:
            print(exc)
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}
        return result
    # ***************************************  scrape_skywork data from csv.  ***********************************************

    def scrape_skywork(self, part_number):
        base_url = "https://www.skyworksinc.com"
        print(f"Scraping data for part number: {part_number}")
        try:
            payload = {"SearchText": part_number}

            resp = requests.post(
                f"{base_url}/api/feature/search/searchitems",
                params=payload,
                timeout=10,
            )

            res = resp.json()
            part_url = "N/A"
            for item in res["GlobalResultItems"]:
                if item["Title"] == part_number:
                    part_url = f"{base_url}{item['ItemUrl']}"

            resp = requests.get(part_url, timeout=10)

            soup = BeautifulSoup(resp.content, "html.parser")

            part_name = (
                soup.find("div", class_="row product-details-description")
                .find("h4")
                .get_text(strip=True)
            )
            product_lifecycle = "N/A"
            if soup.find("span", string="Product Lifecycle"):
                product_lifecycle = soup.find(
                    "span", string="Product Lifecycle"
                ).next_sibling.get_text(strip=True)

            datasheet = "N/A"

            if (
                soup.find(
                    "div", class_="btns-container-new").find("a").get_text(strip=True)
                == "Data Sheets"
            ):
                datasheet = f'{base_url}"{soup.find("div", class_="btns-container-new").find("a")["href"]}'

            certificate_of_conf = f"{base_url}/EnvironmentalProductCertificatePrint.aspx?PartNumber={part_number}"

            cert_resp = requests.get(certificate_of_conf, timeout=10)

            cert_soup = BeautifulSoup(cert_resp.content, "html.parser")
            if cert_soup.find("h2", string="Part number not found."):
                certificate_of_conf = "N/A"

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Product Lifecycle": product_lifecycle,
                "Certificate of Conformance": certificate_of_conf,
                "Datasheet": datasheet,
            }
        except Exception:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

        return result

    # ***************************************  scrape_mcmaster data from csv.  ***********************************************

    def scrape_mcmaster(self, part_number):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--ignore-ssl-errors')
        driver = uc.Chrome(options=options)
        print(f"Scraping data for part number: {part_number}")
        url = f"https://www.mcmaster.com/{part_number}/"

        driver.implicitly_wait(1)
        driver.get(url)
        try:
            part_name = driver.find_elements(
                By.CLASS_NAME, "header-secondary--pd")
            part_name = 'N/A' if not part_name else part_name[0].text
            category = driver.find_element(
                By.CLASS_NAME, "header-primary--pd").text

            status = driver.find_element(By.CLASS_NAME, "stock-status").text

            rohs = (
                driver.find_element(By.XPATH, "//*[contains(text(), 'RoHS')]")
                .find_element(By.XPATH, "following-sibling::td")
                .text
            )

            reach = (
                driver.find_element(By.XPATH, "//*[contains(text(), 'REACH')]")
                .find_element(By.XPATH, "following-sibling::td")
                .text
            )

            result = {
                "Results": "Found",
                "Part Number": part_number,
                "Part Name": part_name,
                "Status": status,
                "Category": category,
                "RoHS": rohs,
                "REACH": reach,
            }
            print(f"Data successfully scraped for part number: {part_number}")
            return result
        except Exception as exc:
            print(f"Part {part_number} is not found on server.")
            return {"status": 404}

    # ***************************************  scrap_Rscomponents data from csv.  ***********************************************

    def scrap_Rscomponentss(self, partnumbers):
        try:
            url = "https://export.rsdelivers.com/productlist/search?query=" + \
                urllib.parse.quote(str(partnumbers))

            r = requests.get(url)
            data = BeautifulSoup(r.text, 'lxml')
            partName = data.find(
                "h1", class_='product-detail-page-component_title__HAXxV').text

            manufacturerName = data.find("div", class_='pill-component-module_grey__38ctb').find_next(
                "div", class_='pill-component-module_grey__38ctb').text

            mpn = data.find("div", class_='pill-component-module_grey__38ctb').find_next(
                "div", class_='pill-component-module_grey__38ctb').find_next("div", class_='pill-component-module_grey__38ctb').text

            return {"Results": "Found", "Partnumber": partnumbers, "mpn": mpn, "partName": partName, "manufacturerName": manufacturerName}
        except Exception as e:
            print(e)
            return {"status": 404}

    # ***************************************  scrap_Te data from csv.  ***********************************************
    # def scrap_Tes(self, partnumbers):
    #     try:
    #         url = "https://www.te.com/commerce/alt/ValidateParts.do"

    #         payload = 'partNumber=' + partnumber
    #         headers = {
    #             'authority': 'www.te.com',
    #             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #             'accept-language': 'en-US,en;q=0.9',
    #             'cache-control': 'max-age=0',
    #             'content-type': 'application/x-www-form-urlencoded',
    #             'referer': 'https://www.te.com/commerce/alt/product-compliance.do',
    #             'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    #             'sec-ch-ua-mobile': '?1',
    #             'sec-ch-ua-platform': '"Android"',
    #             'sec-fetch-dest': 'document',
    #             'sec-fetch-mode': 'navigate',
    #             'sec-fetch-site': 'same-origin',
    #             'sec-fetch-user': '?1',
    #             'upgrade-insecure-requests': '1',
    #             'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
    #             'Access-Control-Request-Method': '*',
    #             'x-requested-with': 'XMLHttpRequest'

    #         }

    #         response = requests.request(
    #             "POST", url, headers=headers, data=payload)
    #         soup = BeautifulSoup(response.text, 'lxml')
    #         tePartNum = soup.find('div', class_='product_description').text
    #         status = soup.find('table').find('tbody').find('tr').find(
    #             'td').find('a').find_next('a').find_next('a').text
    #         rohsInfo = soup.find('table').find('tbody').find('tr').find(
    #             'td').find_next('td').find('div', class_='compliance').find('a').text
    #         # try:
    #         rohsExcemption = soup.find('table').find('tbody').find('tr').find(
    #             'td').find_next('td').find('div', class_='compliance').find('div', style='margin-top:8px;').text

    #         # except Exception:
    #         # pass
    #         current_reach_candidate = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
    #             'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').text
    #         current_reach_declaration = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
    #             'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').text
    #         svhc = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
    #             'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').find_next('span').text
    #         return {"Results": "Found", "Status": status, "TE-PartNum": tePartNum, "rohsInfo": rohsInfo,
    #                 "rohs-excemption": rohsExcemption, "reach-candidate": current_reach_candidate, "rewach-declaration": current_reach_declaration, "svhc": svhc, "declaration-link": 'https://www.te.com/commerce/alt/SinglePartSearch.do?PN='+tePartNum+'&dest=stmt'}
    #     except Exception as e:
    #         print(e)
    #         return {"status": 404}

    # # ***************************************  scrap_omron data from csv.  ***********************************************
    # def scrap_omrons(self, partnumber):
    #     try:
    #         url = "https://industrial.omron.eu/en/api/rohs_reach/search.json?q=" + \
    #             str(partnumber) + "&page=1"
    #         payload = {}
    #         headers = {
    #             'authority': 'industrial.omron.eu',
    #             'accept': 'application/json, text/javascript, */*; q=0.01',
    #             'accept-language': 'en-US,en;q=0.9',
    #             # 'cookie': 'OMR_USER_LANG=EU-en; _gcl_au=1.1.1823097155.1661233578; _ga=GA1.3.1108793817.1661233578; _gid=GA1.3.1802832004.1661233578; nQ_cookieId=6a1bd137-c19e-3e85-c194-42f967dcb5dc; nQ_userVisitId=516dbf5b-534c-5333-a722-578b538d38a0; AMCVS_7FCC6D075DDD2B730A495C72%40AdobeOrg=1; AMCV_7FCC6D075DDD2B730A495C72%40AdobeOrg=-432600572%7CMCIDTS%7C19228%7CMCMID%7C51015238740838683563499486990667075736%7CMCAAMLH-1661838380%7C6%7CMCAAMB-1661838380%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1661240780s%7CNONE%7CvVersion%7C4.5.2; tracking_enabled=true; updated_bar=true; s_cc=true; ELOQUA=GUID=6255A7F231D5496BB717432E9D0FC266; _navigation=60ba1233651a71dfcde6938d71ca7b99db31fc7c; stat_track_u_id=uid%3D915270800%26f%3D5373%253A1022%26st%3D1%26sy%3D%26ls%3D1661244382%26off%3D%26noacts%3D%26dg%3D%26hs%3D1; _stat_track_s_id=_si%3D1661233584%26_sid%3D1661244382%26_inew%3D1%26_ls%3D1661244382%26_lurl%3D1785484693%26_lrfr%3D1785484693%26_la%3D1661244760%26_so%3D%26_pp%3D%26_bh%3D382%26_ane%3D%26_te%3D%26_nay%3D%26_nae%3D%26_nac%3D; s_ips=1077; s_sq=%5B%5BB%5D%5D; _session=4Mc37rGQbTiSFsNImDbzzfBBcl7%2FHA%2Bykdok08VY0UZaAJ8skC95teMB6tLb0sI0bVCgHTDiBnAZX9Jor%2BC2Xnho%2BDZbmCw%2FljXDYjr6HgTVl%2FJdvaxQT%2Fxd8nO5X5JCxq78INmknLPReBPmBA8RpxYx8X3xY3XLJnl3qStDxFO%2BDEN8I9EsmBrFbP4kA4u0j7bS%2BaI0FXnzwEVGJaTvd6dNbcR8gNwwidTmgVZCwanIt9XH6zX8ouKcwGzuVBPiSZmjiu3y5t7HHTozmFnwQtE8s2hbhoeUs0ZZoco4FK3AKNUL0sstxxZ9PXKelr6VSZjSWuir9yjknLDrstu1RD2i95ok4w2i%2Bb%2FsfDbWlmWprJlpW3IYLRl3380cupSkoyPbeRKHFL6ipi1Mwh%2BvfFJ8t77g9hFkuFcFKcrZw3qk0y2TstGcghfNYB5rKhj2vL9cA%2BKS0DkKbfyTSlqqq7cG7xlYoysXR19V7TlivLiqK%2Fyc3cXvoo7xMJVC4xKhP6qZtK5z9XuWArE8b8VGksKg6efm46Lh2SC8Bi8MsIb%2FGA9TgpItsQw%2BzZFRIeYNMh13OmuaHdNWfHzaO845hw%2B0ozKxa7VS8qY%2Fm4dTv0qKV%2BJL2SJFM2uRTpEVqKae6gMq5TL%2FGt1He9%2BnCgAOyuR8NTVTDISjrvMQM1TY5%2BfSsmRZB%2F807Ac1Cvf5%2FjOFwhEGgIznaX3onDA3h0WZc7UZDafiGRfGIEvBy1m8t%2BZbqt8dc9uTE68w3hlBQB8%2BW1iC7KmhQwb7ouRdXFIZSqMMeX5QxLrNY4JsfoQ5TpQfu%2Bup0YhI4ZZFm%2Fc0xhS76POOhiTq4NvwlhAJ%2BriJwbWWTXEp9lSbKfGiuEXksHG9w3rW%2Fc4lXA02kxBAbGFlKPGWPLr%2B1CEw8Xd4sGketj1p2lS%2F5lb9uMopYTMa5CreQwoqcM3s%2FgS757fcVb3HPBRbYHlhhc6vpVOSqEeP1uP1oPweP6FWa06nBKM8ONCbrbADxptRnOP6FYwDtLXYLrrU9cqWZCfGi8f6%2BC5vkWot--58sY8NsqHgQGAEqy--%2Bw6DkPGXRivhoeQC4nY%2FvA%3D%3D; s_tp=1814; s_ppv=industrialeu%253Aen%253Aservices-support%253Asupport%253Aenvironmental-product-information%2C59%2C59%2C1077%2C1%2C3; OMR_USER_LANG=EU-en; _session=00ggeX7geMnlgzhSKJVrc6vSmgZ%2FABN7AjFjMWql%2Bij2ceMyV2twQDMNEv8ppUZBgPUTB4AXjnRVoapzOAMR61e1%2BY3yTamB0PWMkXOwlJi6DbrQkJpeaUTPJi40wb2cdll%2FJFrKS%2FHQJ6WGnQySdW5odvgtGqUy8tXAx4UlWymkyAM8nFlKc5xOS2RMtTBavRUXv5vzaBH3NfzjmN5u39fmq0ikB0fhCZ7sNblEPf66aWidyDTlMtgF5nLQseulUFTXhXXgwubm0HmR9Ve1uSby7AqvmGiGpjgoiiPfzTiZcbRt7H0QPHA8SDZlVSIg3oriUTsMg%2Frwybdo3oetZnedOLqxhWrciS8Nx20g7FN1zttKDuaeEQTyA%2BrW85C0GflqNlx47j%2BtvjmfsIT1janrBVNDagM4aokkZW8R34StPWAy9mobfDatKZ1nfbsp29pXL4ZjdEe6WuajCirv4VaRU2a%2BCgoGkP%2ByiQh%2BCT%2FU9Vxk29aQfVqRyFJ7iFqehnIN67S89janEs0vIxziCsW8KFVLge4tdMBBfQeL6IDi%2BQkcNO6GoMOLM5fKkm0tEW3pspRWzUwLAiYqGA3yY%2FgxsuZpqDlAw9KUlNviIsQuXDifXVb4I7%2FvOWBwR%2BkXuLJJojGh0XeZadH6oXpclq576gc%2Ffq3ZO8rxafNX8cfxAtd1tD5AAZMUBkWmw9jJzCGuyToMe%2FhFB08rAUNVpPOiKCroW8mbUJKI3n%2ByekEeyAv1EAXEzbyLYJhA6NcGukl5UQAHfx9rjn648w46n9OCk5c9wrk97nAF4SLU5AAszWSa8uCfs0TSfpRs%2FQEhi0d2zSzRHZvHqw6pRK6ZNiI9qkDujl%2FbXZFZBdwIPhZFwqabd2nrBBR9U6XCi6LsdWuagX8SJb5W8ow47o0vRyEJEPSlXUuOmHEuybjMUtWGy8LiTp9Wrje7lL8vasDB1PytQb132gLCyvv4d1C%2B55CXS%2Bh8eK0biImvxhlLP66QiC%2FUlwjRqOuPwh5HRM3%2BAXvRnSzPFTbsXiqgVQDU5MbE--2k1eRLZg0nZy9lF2--bjMe8r7ZjAp%2FsNfp%2BQzrTA%3D%3D',
    #             'if-none-match': 'W/"78c252489f63d35938e4b3b08d94af48"',
    #             'referer': 'https://industrial.omron.eu/en/services-support/support/environmental-product-information',
    #             'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    #             'sec-ch-ua-mobile': '?1',
    #             'sec-ch-ua-platform': '"Android"',
    #             'sec-fetch-dest': 'empty',
    #             'sec-fetch-mode': 'cors',
    #             'sec-fetch-site': 'same-origin',
    #             'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
    #             'x-csrf-token': 'sffvsIpH2eIPkz3qwj0Knx3QXlaKcnHsr0incPTXMqs7H0QW7RepIWyVv2qZGFz3RbCcijjDu/YKX5YeL0phFw==',
    #             'x-requested-with': 'XMLHttpRequest'}
    #         r = requests.request("GET", url, headers=headers, data=payload)
    #         response = r.json()
    #         for res in response['results']:
    #             if res['description'] == str(partnumber) or res['description'] == str(partnumber).replace("-", ""):
    #                 item_code = res['short_item_code']
    #                 return {"Results": "Found", "GrabbedSPN": res['description'], "RoHS 2011/65/EU": res['rohs6_compliant'], "RoHS (EU)2015/863": res['rohs10_compliant'], "SVHC contained": res['reach_substances'], "rohs-link": 'https://industrial.omron.eu/en/pdf/rohs/' + str(item_code) + '.pdf?directive=10', "reach-link": 'https://industrial.omron.eu/en/pdf/reach/' + str(item_code) + '.pdf'}
    #         return {"status": 404}
    #     except Exception as e:
    #         print(e)
    #         return {"status": 404}

    # ***************************************  scrap_abracon data from csv.  ***********************************************

    def scrap_abracon(self, partnumber):
        try:
            url = "https://abracon.com/parametric/oscillators/"+partnumber
            payload = {}
            headers = {
                'authority': 'abracon.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'cookie': 'msd365mkttr=eZzKTCwJwsVZKbxpGmG6kFYcK7X1U6WuqkImWkp2; _ga=GA1.1.1208419317.1668778594; s_fid=2AABAF8836FC9DBE-04379C4085190E18; poptin_user_id=0.ih61vkykgw; poptin_user_ip=41.72.215.154; poptin_user_country_code=false; __utmz=73986242.1668779192.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); poptin_d_a_x_v_265c22a6224ac=2023-02-07; poptin_session_account_dbe72b3615145=true; poptin_c_visitor=true; ln_or=eyIyNTUwNTAwIjoiZCJ9; __utmc=73986242; poptin_old_user=true; msd365mkttrs=4L4femqD; poptin_d_a_x_v_16715513259e6=2023-02-13; poptin_o_a_d_16715513259e6=a7baa09650e13; poptin_c_p_o_x_c_16715513259e6=16715513259e6; poptin_d_a_x_v_54316880c9ee4=2023-02-13; poptin_o_a_d_54316880c9ee4=9fe6ade0176b3; poptin_c_p_o_x_c_54316880c9ee4=54316880c9ee4; poptin_d_a_x_v_a8d9a08f8c613=2023-02-13; poptin_o_a_d_a8d9a08f8c613=ae6931e0deb78; __utma=73986242.1208419317.1668778594.1676359490.1676365743.18; __utmt=1; poptin_session=true; _ga_LTFVKW811Z=GS1.1.1676365762.16.1.1676365785.0.0.0; _iub_cs-14915140=%7B%22consent%22%3Atrue%2C%22timestamp%22%3A%222022-11-18T13%3A36%3A33.603Z%22%2C%22version%22%3A%221.42.4%22%2C%22id%22%3A14915140%2C%22cons%22%3A%7B%22rand%22%3A%22805536%22%7D%7D; __utmb=73986242.4.10.1676365743; poptin_referrer=',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36'
            }

            response = requests.request(
                "GET", url, headers=headers, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            rohs = soup.find(class_='check').find(
                'p').find_next('p').text.strip()
            lead = soup.find(class_='check').find(
                'p').find_next('p').find_next('p').text.strip()
            status = soup.find(class_='details').find('ul').find_next(
                'ul').find_next('ul').find('li').find_next('li').text.strip()  # here any find fails (BUG)
            print(rohs, lead, status)
            series = soup.find(class_='details').find('ul').find_next('ul').find_next('ul').find_next('ul').find_next('ul').find_next(
                'ul').find_next('ul').find_next('ul').find_next('ul').find_next('ul').find('li').find_next('li').text.strip()
            return {"Results": "Found", "rohs": rohs, "lead": lead, "status": status, "series": series}
        except Exception as e:
            print(e)
            return {"status": 404}

     # ***************************************  scrap_panasonic data from csv.  ***********************************************

    def scrap_panasonic(self, partnumber):
        try:
            url = "https://industrial.panasonic.com/ww/products/pt/"+partnumber+"/lineup"

            payload = {}
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"'
            }

            response = requests.request(
                "GET", url, headers=headers, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            # 'NoneType' object has no attribute 'text' (BUG)
            totalPage = soup.find(class_='search-header-result').text
            page = round(int(totalPage.split('of ')[1].split('F')[0])/50)
            for i in soup.find('tbody').find_all('tr'):
                try:
                    partNum = i.find(class_='model').text
                    series = i.find(
                        'td', class_='cad-data').find_next('td').find_next('td').text
                    print(partNum, series)
                    return {"Results": "Found", "partNumber": partNum, "series": series}
                except Exception:
                    pass
        except Exception as e:
            print(e)
            return {"status": 404}

    # ***************************************  scrap_Arrow data from csv.  ***********************************************
    def scrap_Arrows(self, partnumbers):
        url = "http://api.arrow.com/itemservice/v4/en/search/token?login=assent1&apikey=e91ee2fc20668093198daaf7252a7208e06a428b551ac2e652c83ed5671aaaee&search_token=" + \
            str(partnumber)
        payload = {}
        headers = {}
        response = requests.request(
            "GET", url, headers=headers, data=payload).json()
        results = response['itemserviceresult']['data']
        for res in results:
            try:
                for r in res['PartList']:

                    return {"Results": "Found", "MPN": r['partNum'], "Manufacturer": r['manufacturer']['mfrName']}
            except Exception as e:
                print(e)
                return {"status": 404}


if __name__ == '__main__':
    scraper = Scrapper()
    print(scraper.scrap_festo("8046265"))
