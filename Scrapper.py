from urllib.parse import quote_plus
from bs4.element import NavigableString
import requests
from bs4 import BeautifulSoup
import urllib
from sites.mouser import Mouser
import re
import json
from sites.Festo import Festo


class Scrapper(Mouser):

    def scrap_newark(self, partNumber):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
        print(partnumber)
        url = 'https://www.ti.com/product/' + str(partnumber)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        datasheet = soup.find('a', navtitle="data sheet") or ''
        try:
            result = {
                'Results': 'Found',
                'status': soup.find('ti-product-status').find('a').text,
                'Partnumber': soup.find('ti-main-panel').attrs["gpn"],
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
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
            return {"Results": "Found", "PArtname": partname, "Status": status, "Series": series, "ROHS": rohs, "REACH": reach, "HALOGEN": halogen, "Declaration": declaration}
        except Exception as e:

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
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'referer': 'https://www.te.com/commerce/alt/product-compliance.do',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
                'Access-Control-Request-Method': '*',
                'x-requested-with': 'XMLHttpRequest',
            }

            response = requests.request(
                "POST", url, headers=headers, timeout=200, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            tePartNum = soup.find('div', class_='product_description').text
            status = soup.find('table').find('tbody').find('tr').find(
                'td').find('a').find_next('a').find_next('a').text
            rohsInfo = soup.find('table').find('tbody').find('tr').find(
                'td').find_next('td').find('div', class_='compliance').find('a').text
            # try:
            rohsExcemption = soup.find('table').find('tbody').find('tr').find(
                'td').find_next('td').find('div', class_='compliance').find('div', style='margin-top:8px;').text

            # except Exception:
            # pass
            current_reach_candidate = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').text
            current_reach_declaration = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').text
            svhc = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').find_next('span').text
            return {"Results": "Found", "Status": status, "TE-PartNum": tePartNum, "rohsInfo": rohsInfo,
                    "rohs-excemption": rohsExcemption, "reach-candidate": current_reach_candidate, "rewach-declaration": current_reach_declaration, "svhc": svhc, "declaration-link": 'https://www.te.com/commerce/alt/SinglePartSearch.do?PN='+tePartNum+'&dest=stmt'}
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
        except (IndexError, AttributeError):
            print('part number is not found on server')
            return {"status": 404}

        return result

    def scrap_tdk(self, partNumber):
        try:
            url = 'https://product.tdk.com/pdc_api/en/search/list/search_result'
            response = requests.post(url,
                                     headers={
                                         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
                                     },
                                     params={'part_no': partNumber, '_l': 20,
                                             '_p': 1, '_c': 'part_no-part_no', '_d': 0}
                                     )

            soup = BeautifulSoup(response.json()['results'], 'lxml')
            table = soup.find('table', id="table_result")
            tr = table.find('tbody').find_all('tr')[0]
            part_detail = tr.find('td', {'data-label': "Part No."})
            part_no = part_detail.find('a').text

            result = {
                'Results': 'Found',
                'status': part_detail.find('img').attrs['title'],
                'partNumber': part_no,
                'partName': part_no,
                'dataSheet': 'https://product.tdk.com' + tr.find('td', {'data-label': "Catalog / Data Sheet"}).find('a').attrs['href'],
                'brand': tr.find('td', {'data-label': "Brand"}).text.strip()
            }
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
        except (IndexError, AttributeError, requests.exceptions.MissingSchema):
            print('part number is not found on server')
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
        except (IndexError, AttributeError):
            print('part number is not found on server')
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
        try:
            url = "https://industrial.omron.eu/en/api/rohs_reach/search.json?q=" + \
                str(partnumber) + "&page=1"
            payload = {}
            headers = {
                'authority': 'industrial.omron.eu',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                # 'cookie': 'OMR_USER_LANG=EU-en; _gcl_au=1.1.1823097155.1661233578; _ga=GA1.3.1108793817.1661233578; _gid=GA1.3.1802832004.1661233578; nQ_cookieId=6a1bd137-c19e-3e85-c194-42f967dcb5dc; nQ_userVisitId=516dbf5b-534c-5333-a722-578b538d38a0; AMCVS_7FCC6D075DDD2B730A495C72%40AdobeOrg=1; AMCV_7FCC6D075DDD2B730A495C72%40AdobeOrg=-432600572%7CMCIDTS%7C19228%7CMCMID%7C51015238740838683563499486990667075736%7CMCAAMLH-1661838380%7C6%7CMCAAMB-1661838380%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1661240780s%7CNONE%7CvVersion%7C4.5.2; tracking_enabled=true; updated_bar=true; s_cc=true; ELOQUA=GUID=6255A7F231D5496BB717432E9D0FC266; _navigation=60ba1233651a71dfcde6938d71ca7b99db31fc7c; stat_track_u_id=uid%3D915270800%26f%3D5373%253A1022%26st%3D1%26sy%3D%26ls%3D1661244382%26off%3D%26noacts%3D%26dg%3D%26hs%3D1; _stat_track_s_id=_si%3D1661233584%26_sid%3D1661244382%26_inew%3D1%26_ls%3D1661244382%26_lurl%3D1785484693%26_lrfr%3D1785484693%26_la%3D1661244760%26_so%3D%26_pp%3D%26_bh%3D382%26_ane%3D%26_te%3D%26_nay%3D%26_nae%3D%26_nac%3D; s_ips=1077; s_sq=%5B%5BB%5D%5D; _session=4Mc37rGQbTiSFsNImDbzzfBBcl7%2FHA%2Bykdok08VY0UZaAJ8skC95teMB6tLb0sI0bVCgHTDiBnAZX9Jor%2BC2Xnho%2BDZbmCw%2FljXDYjr6HgTVl%2FJdvaxQT%2Fxd8nO5X5JCxq78INmknLPReBPmBA8RpxYx8X3xY3XLJnl3qStDxFO%2BDEN8I9EsmBrFbP4kA4u0j7bS%2BaI0FXnzwEVGJaTvd6dNbcR8gNwwidTmgVZCwanIt9XH6zX8ouKcwGzuVBPiSZmjiu3y5t7HHTozmFnwQtE8s2hbhoeUs0ZZoco4FK3AKNUL0sstxxZ9PXKelr6VSZjSWuir9yjknLDrstu1RD2i95ok4w2i%2Bb%2FsfDbWlmWprJlpW3IYLRl3380cupSkoyPbeRKHFL6ipi1Mwh%2BvfFJ8t77g9hFkuFcFKcrZw3qk0y2TstGcghfNYB5rKhj2vL9cA%2BKS0DkKbfyTSlqqq7cG7xlYoysXR19V7TlivLiqK%2Fyc3cXvoo7xMJVC4xKhP6qZtK5z9XuWArE8b8VGksKg6efm46Lh2SC8Bi8MsIb%2FGA9TgpItsQw%2BzZFRIeYNMh13OmuaHdNWfHzaO845hw%2B0ozKxa7VS8qY%2Fm4dTv0qKV%2BJL2SJFM2uRTpEVqKae6gMq5TL%2FGt1He9%2BnCgAOyuR8NTVTDISjrvMQM1TY5%2BfSsmRZB%2F807Ac1Cvf5%2FjOFwhEGgIznaX3onDA3h0WZc7UZDafiGRfGIEvBy1m8t%2BZbqt8dc9uTE68w3hlBQB8%2BW1iC7KmhQwb7ouRdXFIZSqMMeX5QxLrNY4JsfoQ5TpQfu%2Bup0YhI4ZZFm%2Fc0xhS76POOhiTq4NvwlhAJ%2BriJwbWWTXEp9lSbKfGiuEXksHG9w3rW%2Fc4lXA02kxBAbGFlKPGWPLr%2B1CEw8Xd4sGketj1p2lS%2F5lb9uMopYTMa5CreQwoqcM3s%2FgS757fcVb3HPBRbYHlhhc6vpVOSqEeP1uP1oPweP6FWa06nBKM8ONCbrbADxptRnOP6FYwDtLXYLrrU9cqWZCfGi8f6%2BC5vkWot--58sY8NsqHgQGAEqy--%2Bw6DkPGXRivhoeQC4nY%2FvA%3D%3D; s_tp=1814; s_ppv=industrialeu%253Aen%253Aservices-support%253Asupport%253Aenvironmental-product-information%2C59%2C59%2C1077%2C1%2C3; OMR_USER_LANG=EU-en; _session=00ggeX7geMnlgzhSKJVrc6vSmgZ%2FABN7AjFjMWql%2Bij2ceMyV2twQDMNEv8ppUZBgPUTB4AXjnRVoapzOAMR61e1%2BY3yTamB0PWMkXOwlJi6DbrQkJpeaUTPJi40wb2cdll%2FJFrKS%2FHQJ6WGnQySdW5odvgtGqUy8tXAx4UlWymkyAM8nFlKc5xOS2RMtTBavRUXv5vzaBH3NfzjmN5u39fmq0ikB0fhCZ7sNblEPf66aWidyDTlMtgF5nLQseulUFTXhXXgwubm0HmR9Ve1uSby7AqvmGiGpjgoiiPfzTiZcbRt7H0QPHA8SDZlVSIg3oriUTsMg%2Frwybdo3oetZnedOLqxhWrciS8Nx20g7FN1zttKDuaeEQTyA%2BrW85C0GflqNlx47j%2BtvjmfsIT1janrBVNDagM4aokkZW8R34StPWAy9mobfDatKZ1nfbsp29pXL4ZjdEe6WuajCirv4VaRU2a%2BCgoGkP%2ByiQh%2BCT%2FU9Vxk29aQfVqRyFJ7iFqehnIN67S89janEs0vIxziCsW8KFVLge4tdMBBfQeL6IDi%2BQkcNO6GoMOLM5fKkm0tEW3pspRWzUwLAiYqGA3yY%2FgxsuZpqDlAw9KUlNviIsQuXDifXVb4I7%2FvOWBwR%2BkXuLJJojGh0XeZadH6oXpclq576gc%2Ffq3ZO8rxafNX8cfxAtd1tD5AAZMUBkWmw9jJzCGuyToMe%2FhFB08rAUNVpPOiKCroW8mbUJKI3n%2ByekEeyAv1EAXEzbyLYJhA6NcGukl5UQAHfx9rjn648w46n9OCk5c9wrk97nAF4SLU5AAszWSa8uCfs0TSfpRs%2FQEhi0d2zSzRHZvHqw6pRK6ZNiI9qkDujl%2FbXZFZBdwIPhZFwqabd2nrBBR9U6XCi6LsdWuagX8SJb5W8ow47o0vRyEJEPSlXUuOmHEuybjMUtWGy8LiTp9Wrje7lL8vasDB1PytQb132gLCyvv4d1C%2B55CXS%2Bh8eK0biImvxhlLP66QiC%2FUlwjRqOuPwh5HRM3%2BAXvRnSzPFTbsXiqgVQDU5MbE--2k1eRLZg0nZy9lF2--bjMe8r7ZjAp%2FsNfp%2BQzrTA%3D%3D',
                'if-none-match': 'W/"78c252489f63d35938e4b3b08d94af48"',
                'referer': 'https://industrial.omron.eu/en/services-support/support/environmental-product-information',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
                'x-csrf-token': 'sffvsIpH2eIPkz3qwj0Knx3QXlaKcnHsr0incPTXMqs7H0QW7RepIWyVv2qZGFz3RbCcijjDu/YKX5YeL0phFw==',
                'x-requested-with': 'XMLHttpRequest'}
            r = requests.request("GET", url, headers=headers, data=payload)
            response = r.json()
            for res in response['results']:
                if res['description'] == str(partnumber) or res['description'] == str(partnumber).replace("-", ""):
                    item_code = res['short_item_code']
                    return {"Results": "Found", "GrabbedSPN": res['description'], "RoHS 2011/65/EU": res['rohs6_compliant'], "RoHS (EU)2015/863": res['rohs10_compliant'], "SVHC contained": res['reach_substances'], "rohs-link": 'https://industrial.omron.eu/en/pdf/rohs/' + str(item_code) + '.pdf?directive=10', "reach-link": 'https://industrial.omron.eu/en/pdf/reach/' + str(item_code) + '.pdf'}
            return {"status": 404}
        except Exception as e:
            print(e)
            return {"status": 404}

    def scrap_sager(self, partNumber):
        Service = Service('chromedriver')
        driver = webdriver.Chrome(options=options, service=Service)
        driver.get("https://www.sager.com/")
        # Info needed: Part Number, Part Name,RoHS Status, Manufacturer, Sub Category, Brand, Datasheet
        # wait for the input with id txtPtSearch
        # get the input element
        input = driver.find_element(By.ID, "txtPtSearch")
        # send the part number to the input
        input.send_keys(partNumber)
        # send the enter key to the input
        input.send_keys("\ue007")
        # if captcha then wait for it to be solved
        # detect if captcha is present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
            )
            # wait for the captcha to be solved
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtPtSearch"))
            )
        except:
            pass

        # get the H1 element

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1")))
        # part name ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_lblMfgr
        part_name = driver.find_element(
            By.ID, "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_lblMfgr"
        ).text
        # part_number ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_lblTitle
        part_number = driver.find_element(
            By.ID, "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_lblTitle"
        ).text

        # RoHS Status ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconRohs
        try:
            rohs_status = driver.find_element(
                By.ID, "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_iconRohs"
            ).text
        except:
            rohs_status = "Not Found"

        # td which is sibling of th that has span that has text "Manufacturer"
        manufacturer = driver.find_element(
            By.XPATH,
            "//th/span[contains(text(),'Manufacturer')]/../following-sibling::td[1]",
        ).text
        # sub category  td which is sibling of th that has span that has text "Sub Category"

        sub_category = driver.find_element(
            By.XPATH,
            "//th/span[contains(text(),'Sub-Category')]/../following-sibling::td[1]",
        ).text

        # brand td which is sibling of th that has span that has text "Brand"
        try:
            brand = driver.find_element(
                By.XPATH, "//th/span[contains(text(),'Brand')]/../following-sibling::td[1]"
            ).text
        except:
            brand = "Not Found"

        #

        # sheet_link = ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_specsURL
        sheet_link = driver.find_element(
            By.ID, "ctl00_ContentPlaceHolder_PageContent1_PowerProductDetail1_specsURL"
        ).get_attribute("href")
        print(partNumber)
        print(part_number)
        if part_number == partNumber:
            return {
                "Results": "Found",
                "partNumber": part_number,
                "partName": part_name,
                "manufacturer": manufacturer,
                "subCategory": sub_category,
                "brand": brand,
                "RoHSStatus": rohs_status,
                "sheetLink": sheet_link,

            }

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

        driver = webdriver.Chrome(options=options, service=Service)
        driver.get("https://www.rshughes.com/search.html?q=" + partNumber)
        # wait for the H1 WITH class called h2 to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "h2")))
        # get the H1 element
        part_name = driver.find_element(By.XPATH, "//h1[@class='h2']").text
        part_number = driver.find_element(
            By.XPATH, "//h2[contains(@class,'text-gray')]").text
        brand = driver.find_element(
            By.XPATH, "//li[./div[1]/span[contains(text(),'Brand')]]/div[2]").text
        item = {
            "Results": "Found",
            'partNumber': part_number,
            'partName': part_name,
            'Brand': brand
        }
        return item

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

        def Check_Response(supplier, response, foundlist):
            try:
                if response["Results"] == "Found":
                    foundlist.append(supplier)
            except Exception as e:
                pass

        suppliers = []

        # Checking the response of the scraped data from the two websites.
        response = self.scrap_festo(partnumber)
        Check_Response("festo", response, suppliers)

        response = self.scrap_Arrow(partnumber)
        Check_Response("arrow", response, suppliers)

        response = self.scrap_omron(partnumber)
        Check_Response("omron", response, suppliers)

        response = self.scrap_Rscomponents(partnumber)
        Check_Response("RS-components", response, suppliers)

        response = self.scrap_Maxim(partnumber)
        Check_Response("maxim", response, suppliers)

        response = self.scrap_Molex(partnumber)
        Check_Response("molex", response, suppliers)

        response = self.scrap_Wago(partnumber)
        Check_Response("wago", response, suppliers)

        response = self.scrap_Te(partnumber)
        Check_Response("Te", response, suppliers)

        response = self.scrap_Phoenix(partnumber)
        Check_Response("phoenix", response, suppliers)

        response = self.scrap_onsemi(partnumber)
        Check_Response("onsemi", response, suppliers)

        response = self.scrap_mouser(partnumber)
        Check_Response("mouser", response, suppliers)

        response = self.scrap_3m(partnumber)
        Check_Response("scrap_3m", response, suppliers)

        response = self.scrap_ti(partnumber)
        Check_Response("scrap_ti", response, suppliers)

        response = self.scrap_murata(partnumber)
        Check_Response("scrap_murata", response, suppliers)

        response = self.scrap_newark(partnumber)
        Check_Response("scrap_newark", response, suppliers)

        response = self.scrap_festo(partnumber)
        Check_Response("scrap_festo", response, suppliers)

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
            return {status: 404}

    # ***************************************  scrap_Rscomponents data from csv.  ***********************************************
    def scrap_Rscomponentss(self, partnumbers):
        try:
            url = "https://export.rsdelivers.com/productlist/search?query=" + \
                urllib.parse.quote(str(partnumber))

            r = requests.get(url)
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

    # ***************************************  scrap_Te data from csv.  ***********************************************
    def scrap_Tes(self, partnumbers):
        try:
            url = "https://www.te.com/commerce/alt/ValidateParts.do"

            payload = 'partNumber=' + partnumber
            headers = {
                'authority': 'www.te.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'referer': 'https://www.te.com/commerce/alt/product-compliance.do',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
                'Access-Control-Request-Method': '*',
                'x-requested-with': 'XMLHttpRequest'

            }

            response = requests.request(
                "POST", url, headers=headers, data=payload)
            soup = BeautifulSoup(response.text, 'lxml')
            tePartNum = soup.find('div', class_='product_description').text
            status = soup.find('table').find('tbody').find('tr').find(
                'td').find('a').find_next('a').find_next('a').text
            rohsInfo = soup.find('table').find('tbody').find('tr').find(
                'td').find_next('td').find('div', class_='compliance').find('a').text
            # try:
            rohsExcemption = soup.find('table').find('tbody').find('tr').find(
                'td').find_next('td').find('div', class_='compliance').find('div', style='margin-top:8px;').text

            # except Exception:
            # pass
            current_reach_candidate = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').text
            current_reach_declaration = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').text
            svhc = soup.find('table').find('tbody').find('tr').find('td').find_next('td').find('div', class_='compliance').find_next(
                'div', class_='compliance').find_next('div', class_='compliance').find_next('div', class_='compliance').find('span').find_next('span').find_next('span').text
            return {"Results": "Found", "Status": status, "TE-PartNum": tePartNum, "rohsInfo": rohsInfo,
                    "rohs-excemption": rohsExcemption, "reach-candidate": current_reach_candidate, "rewach-declaration": current_reach_declaration, "svhc": svhc, "declaration-link": 'https://www.te.com/commerce/alt/SinglePartSearch.do?PN='+tePartNum+'&dest=stmt'}
        except Exception as e:
            print(e)
            return {"status": 404}

    # ***************************************  scrap_omron data from csv.  ***********************************************
    def scrap_omrons(self, partnumbers):
        try:
            url = "https://industrial.omron.eu/en/api/rohs_reach/search.json?q=" + \
                str(partnumber) + "&page=1"
            payload = {}
            headers = {
                'authority': 'industrial.omron.eu',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                # 'cookie': 'OMR_USER_LANG=EU-en; _gcl_au=1.1.1823097155.1661233578; _ga=GA1.3.1108793817.1661233578; _gid=GA1.3.1802832004.1661233578; nQ_cookieId=6a1bd137-c19e-3e85-c194-42f967dcb5dc; nQ_userVisitId=516dbf5b-534c-5333-a722-578b538d38a0; AMCVS_7FCC6D075DDD2B730A495C72%40AdobeOrg=1; AMCV_7FCC6D075DDD2B730A495C72%40AdobeOrg=-432600572%7CMCIDTS%7C19228%7CMCMID%7C51015238740838683563499486990667075736%7CMCAAMLH-1661838380%7C6%7CMCAAMB-1661838380%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1661240780s%7CNONE%7CvVersion%7C4.5.2; tracking_enabled=true; updated_bar=true; s_cc=true; ELOQUA=GUID=6255A7F231D5496BB717432E9D0FC266; _navigation=60ba1233651a71dfcde6938d71ca7b99db31fc7c; stat_track_u_id=uid%3D915270800%26f%3D5373%253A1022%26st%3D1%26sy%3D%26ls%3D1661244382%26off%3D%26noacts%3D%26dg%3D%26hs%3D1; _stat_track_s_id=_si%3D1661233584%26_sid%3D1661244382%26_inew%3D1%26_ls%3D1661244382%26_lurl%3D1785484693%26_lrfr%3D1785484693%26_la%3D1661244760%26_so%3D%26_pp%3D%26_bh%3D382%26_ane%3D%26_te%3D%26_nay%3D%26_nae%3D%26_nac%3D; s_ips=1077; s_sq=%5B%5BB%5D%5D; _session=4Mc37rGQbTiSFsNImDbzzfBBcl7%2FHA%2Bykdok08VY0UZaAJ8skC95teMB6tLb0sI0bVCgHTDiBnAZX9Jor%2BC2Xnho%2BDZbmCw%2FljXDYjr6HgTVl%2FJdvaxQT%2Fxd8nO5X5JCxq78INmknLPReBPmBA8RpxYx8X3xY3XLJnl3qStDxFO%2BDEN8I9EsmBrFbP4kA4u0j7bS%2BaI0FXnzwEVGJaTvd6dNbcR8gNwwidTmgVZCwanIt9XH6zX8ouKcwGzuVBPiSZmjiu3y5t7HHTozmFnwQtE8s2hbhoeUs0ZZoco4FK3AKNUL0sstxxZ9PXKelr6VSZjSWuir9yjknLDrstu1RD2i95ok4w2i%2Bb%2FsfDbWlmWprJlpW3IYLRl3380cupSkoyPbeRKHFL6ipi1Mwh%2BvfFJ8t77g9hFkuFcFKcrZw3qk0y2TstGcghfNYB5rKhj2vL9cA%2BKS0DkKbfyTSlqqq7cG7xlYoysXR19V7TlivLiqK%2Fyc3cXvoo7xMJVC4xKhP6qZtK5z9XuWArE8b8VGksKg6efm46Lh2SC8Bi8MsIb%2FGA9TgpItsQw%2BzZFRIeYNMh13OmuaHdNWfHzaO845hw%2B0ozKxa7VS8qY%2Fm4dTv0qKV%2BJL2SJFM2uRTpEVqKae6gMq5TL%2FGt1He9%2BnCgAOyuR8NTVTDISjrvMQM1TY5%2BfSsmRZB%2F807Ac1Cvf5%2FjOFwhEGgIznaX3onDA3h0WZc7UZDafiGRfGIEvBy1m8t%2BZbqt8dc9uTE68w3hlBQB8%2BW1iC7KmhQwb7ouRdXFIZSqMMeX5QxLrNY4JsfoQ5TpQfu%2Bup0YhI4ZZFm%2Fc0xhS76POOhiTq4NvwlhAJ%2BriJwbWWTXEp9lSbKfGiuEXksHG9w3rW%2Fc4lXA02kxBAbGFlKPGWPLr%2B1CEw8Xd4sGketj1p2lS%2F5lb9uMopYTMa5CreQwoqcM3s%2FgS757fcVb3HPBRbYHlhhc6vpVOSqEeP1uP1oPweP6FWa06nBKM8ONCbrbADxptRnOP6FYwDtLXYLrrU9cqWZCfGi8f6%2BC5vkWot--58sY8NsqHgQGAEqy--%2Bw6DkPGXRivhoeQC4nY%2FvA%3D%3D; s_tp=1814; s_ppv=industrialeu%253Aen%253Aservices-support%253Asupport%253Aenvironmental-product-information%2C59%2C59%2C1077%2C1%2C3; OMR_USER_LANG=EU-en; _session=00ggeX7geMnlgzhSKJVrc6vSmgZ%2FABN7AjFjMWql%2Bij2ceMyV2twQDMNEv8ppUZBgPUTB4AXjnRVoapzOAMR61e1%2BY3yTamB0PWMkXOwlJi6DbrQkJpeaUTPJi40wb2cdll%2FJFrKS%2FHQJ6WGnQySdW5odvgtGqUy8tXAx4UlWymkyAM8nFlKc5xOS2RMtTBavRUXv5vzaBH3NfzjmN5u39fmq0ikB0fhCZ7sNblEPf66aWidyDTlMtgF5nLQseulUFTXhXXgwubm0HmR9Ve1uSby7AqvmGiGpjgoiiPfzTiZcbRt7H0QPHA8SDZlVSIg3oriUTsMg%2Frwybdo3oetZnedOLqxhWrciS8Nx20g7FN1zttKDuaeEQTyA%2BrW85C0GflqNlx47j%2BtvjmfsIT1janrBVNDagM4aokkZW8R34StPWAy9mobfDatKZ1nfbsp29pXL4ZjdEe6WuajCirv4VaRU2a%2BCgoGkP%2ByiQh%2BCT%2FU9Vxk29aQfVqRyFJ7iFqehnIN67S89janEs0vIxziCsW8KFVLge4tdMBBfQeL6IDi%2BQkcNO6GoMOLM5fKkm0tEW3pspRWzUwLAiYqGA3yY%2FgxsuZpqDlAw9KUlNviIsQuXDifXVb4I7%2FvOWBwR%2BkXuLJJojGh0XeZadH6oXpclq576gc%2Ffq3ZO8rxafNX8cfxAtd1tD5AAZMUBkWmw9jJzCGuyToMe%2FhFB08rAUNVpPOiKCroW8mbUJKI3n%2ByekEeyAv1EAXEzbyLYJhA6NcGukl5UQAHfx9rjn648w46n9OCk5c9wrk97nAF4SLU5AAszWSa8uCfs0TSfpRs%2FQEhi0d2zSzRHZvHqw6pRK6ZNiI9qkDujl%2FbXZFZBdwIPhZFwqabd2nrBBR9U6XCi6LsdWuagX8SJb5W8ow47o0vRyEJEPSlXUuOmHEuybjMUtWGy8LiTp9Wrje7lL8vasDB1PytQb132gLCyvv4d1C%2B55CXS%2Bh8eK0biImvxhlLP66QiC%2FUlwjRqOuPwh5HRM3%2BAXvRnSzPFTbsXiqgVQDU5MbE--2k1eRLZg0nZy9lF2--bjMe8r7ZjAp%2FsNfp%2BQzrTA%3D%3D',
                'if-none-match': 'W/"78c252489f63d35938e4b3b08d94af48"',
                'referer': 'https://industrial.omron.eu/en/services-support/support/environmental-product-information',
                'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
                'x-csrf-token': 'sffvsIpH2eIPkz3qwj0Knx3QXlaKcnHsr0incPTXMqs7H0QW7RepIWyVv2qZGFz3RbCcijjDu/YKX5YeL0phFw==',
                'x-requested-with': 'XMLHttpRequest'}
            r = requests.request("GET", url, headers=headers, data=payload)
            response = r.json()
            for res in response['results']:
                if res['description'] == str(partnumber) or res['description'] == str(partnumber).replace("-", ""):
                    item_code = res['short_item_code']
                    return {"Results": "Found", "GrabbedSPN": res['description'], "RoHS 2011/65/EU": res['rohs6_compliant'], "RoHS (EU)2015/863": res['rohs10_compliant'], "SVHC contained": res['reach_substances'], "rohs-link": 'https://industrial.omron.eu/en/pdf/rohs/' + str(item_code) + '.pdf?directive=10', "reach-link": 'https://industrial.omron.eu/en/pdf/reach/' + str(item_code) + '.pdf'}
            return {"status": 404}
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
