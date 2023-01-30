import requests

class Mouser:
    def scrap_mouser(self, partnumber, API_Key='c8cc8913-3363-4547-a4f6-d48218731924'):

        # normal search
        url = 'https://api.mouser.com/api/v1/search/partnumber'
        requestbody = {"SearchByPartRequest": { "mouserPartNumber": partnumber, "partSearchOptions": 2}}
        parameters = {'apiKey': API_Key}

        headers = {
            'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.post(url, headers=headers, params=parameters,json=requestbody).json()
        searchresults = response["SearchResults"]

        if searchresults.get('NumberOfResult', 0) > 0:
            listofparts = searchresults["Parts"]

        else:
            print('part SPN is not found on server')
            return {"status":404}

        results = []
        for result in listofparts:
            results.append({
                'Results': 'Found',
                'Partnumber': partnumber,
                'partName': result.get('Description'),
                'Description': result.get('ProductDetailUrl'),
                'MouserPartNumber': result.get('MouserPartNumber'),
                'Manufacturer': result.get('Manufacturer'),
                'ManufacturerPartNumber': result.get('ManufacturerPartNumber'),
                'RoHSStatus': result.get('ROHSStatus'),
                'DataSheetURL': result.get('DataSheetUrl')
            })

        return results[0]
