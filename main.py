# import statements
import gspread
import requests
import json
import urllib3
import PyPDF2
import io
from PyPDF2 import PdfFileReader
import re

# connecting to google sheets via gspread library
def connect_gspread():
    from oauth2client.service_account import ServiceAccountCredentials


    # use creds to create a client to interact with the Google sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    return client

# to populate a sheet with new data
def update_fda_screening_sheet(processed_data):
    # connecting to google sheets
    client = connect_gspread()
    # Find a workbook by name and opening a sheet
    sheet = client.open("FDA manual screening sheet").worksheet("Sheet4")

    print(processed_data)

    # testing inserting to the sheet. Replace this with real data
    row = ["I'm", "inserting", "a", "row", "into", "a,", "Spreadsheet", "with", "Python"]
    index = 1
    # increment index via a look to insert multiple rows
    sheet.insert_row(processed_data, index)

    return 0

#function to get the data from FDA website
def process_json():
    #    api_key = 'XBgNq4paVBWNzus06AgwdZxj2XxJMAcJDbErSKlT'
    api_link = "https://api.fda.gov/drug/drugsfda.json?search=submissions.submission_status_date:[2020-04-01+TO+2020-04-27]&limit=5"
    # open link
    response = requests.get(api_link)
    # accessing json data
    data = json.loads(response.content)
    return data

# Action Date	Drug Name	NDA	Submission	Active Ingredients	Company	Submission Classification *
# Submission Status	Comments	STATUS (accepted/rejected)	Peer Review Status	Peer Reviewer
# Review comments

# process the data and parsing the PDF received from FDA
def process_data(data):
    # read json file line by line
    # final_string contains all the data acquired from the for loops
    final_string = []
    # looping through data to find results
    for result in data['results']:
        # print(result["openfda"])

        # try is used since the json file is inconsistent
        try:
            # looping through results to find products
            for product in result['products']:
                # print(product['active_ingredients'])
                # looping through products to find ingredients
                for ingr in product['active_ingredients']:
                    # to concatenate final_string and drug name
                    final_string.append(ingr['name'])
                    # terminating loop to find ingredients
                    break
                # terminating loop to find products
                break

            # print("$$$$" + final_string)
            # print("$$$$$$$openfda start: ")

            # finding brand name in openfda
            openfda_value = result['openfda']
            # concatenating final_string and brand_name
            final_string.append(openfda_value['brand_name'][0])

            # print("$$$$$$$openfda end: ")
            # try is used since the json file is inconsistent
            try:
                # looping through results to find submissions
                for submission in result['submissions']:
                    try:
                        # looping through submissions to find application_docs
                        for app_doc in submission['application_docs']:
                            # print(app_doc['url'])
                            # pdfFileObj = http.request('GET', app_doc['url'])
                            # print(pdfFileObj.data)
                            # print(app_doc['date'])
                            # finding date in application_docs
                            year = (app_doc['date'])
                            # # finding year
                            first_chars = year[0:4]
                            # print(first_chars)
                            # # finding month
                            month = (app_doc['date'])
                            second_chars = month[4:6]
                            # print(second_chars)
                            # # finding day
                            day = (app_doc['date'])
                            third_chars = day[6:9]
                            # print(third_chars)
                            # # concatenating month, day and year
                            pretty_date = (second_chars + "/" + third_chars + "/" + first_chars)
                            # # concatenating final_string and beautified date
                            final_string.append(pretty_date)
                            r = requests.get(app_doc['url'])
                            f = io.BytesIO(r.content)

                            # reading through pdf
                            reader = PdfFileReader(f)
                            # navigating through the first page only
                            contents = reader.getPage(0).extractText()
                            # print(contents)
                            # result = contents.find("DOSAGE")
                            # print(result)
                            # # starting at indications
                            start = contents.find("INDICATIONS") + len("INDICATIONS")
                            # ending at dosage
                            end = contents.find("DOSAGE")
                            # parsing from indications to dosage
                            substring = contents[start:end]
                            # matching keywords
                            matches = ["cancer", "non-small cell lung cancer", "breast cancer",
                                       "gastric or gastroesophageal junction adenocarcinoma", "urothelial carcinoma",
                                       "colorectal cancer", "pancreatic adenocarcinoma", "Solid tumors", "prostate cancer"]
                            # accepting drug if keywords matched
                            if any(x in substring for x in matches):
                                final_string.append("Accepted")

                            # rejecting drug if no keywords matched
                            else:
                                final_string.append("Rejected")
                    # if pdf is not found
                    except:
                        final_string.append("Not a label")
                print(final_string)
            # if submission is not found
            except:
                print("submission not found")
            # if name is not found
        except:
            print("submission_name not found")
    return 0






# getting json data via process_json
json_data = process_json()

# getting acquired data from the parsed json and pdf
processed_data = process_data(json_data)

# updates fda screening sheet with the acquired data from the parsed json and pdf
update_fda_screening_sheet(processed_data)
