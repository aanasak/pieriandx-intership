import gspread
import requests
import json
import urllib3
import PyPDF2
import io
from PyPDF2 import PdfFileReader
import re


def connect_gspread():
    from oauth2client.service_account import ServiceAccountCredentials


    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    return client

def update_fda_screening_sheet(processed_data):
    client = connect_gspread()
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("FDA manual screening sheet").worksheet("Sheet4")

    print(processed_data)
    row = ["I'm", "inserting", "a", "row", "into", "a,", "Spreadsheet", "with", "Python"]
    index = 1
    sheet.insert_row(processed_data, index)
    # # Extract and print all of the values
    # list_of_hashes = sheet.get_all_records()
    # print(list_of_hashes)
    # with open('DrugsFDA FDA-Approved Drugs.csv', 'r') as file_obj:
    #     content = file_obj.read()
    # sheet.insert_row(processed_data, 1)
    return 0


def process_json():
    #    api_key = 'XBgNq4paVBWNzus06AgwdZxj2XxJMAcJDbErSKlT'
    api_link = "https://api.fda.gov/drug/drugsfda.json?search=submissions.submission_status_date:[2020-04-01+TO+2020-04-27]&limit=5"
    response = requests.get(api_link)
    data = json.loads(response.content)
    return data

# Action Date	Drug Name	NDA	Submission	Active Ingredients	Company	Submission Classification *
# Submission Status	Comments	STATUS (accepted/rejected)	Peer Review Status	Peer Reviewer
# Review comments

def process_data(data):
    # read json file line by line
    final_string = []
    for result in data['results']:
        # print(result["openfda"])


        try:
            for product in result['products']:
                # print(product['active_ingredients'])
                for ingr in product['active_ingredients']:
                    final_string.append(ingr['name'])
                    break
                break

            # print("$$$$" + final_string)

            # print("$$$$$$$openfda start: ")
            openfda_value = result['openfda']
            final_string.append(openfda_value['brand_name'][0])

            # print("$$$$$$$openfda end: ")
            try:
                for submission in result['submissions']:
                    try:
                        for app_doc in submission['application_docs']:
                            # print(app_doc['url'])
                            # pdfFileObj = http.request('GET', app_doc['url'])
                            # print(pdfFileObj.data)
                            # print(app_doc['date'])
                            year = (app_doc['date'])
                            first_chars = year[0:4]
                            # print(first_chars)
                            month = (app_doc['date'])
                            second_chars = month[4:6]
                            # print(second_chars)
                            day = (app_doc['date'])
                            third_chars = day[6:9]
                            # print(third_chars)
                            pretty_date = (second_chars + "/" + third_chars + "/" + first_chars)
                            final_string.append(pretty_date)
                            r = requests.get(app_doc['url'])
                            f = io.BytesIO(r.content)

                            reader = PdfFileReader(f)
                            contents = reader.getPage(0).extractText()
                            # print(contents)
                            # result = contents.find("DOSAGE")
                            # print(result)
                            start = contents.find("INDICATIONS") + len("INDICATIONS")
                            end = contents.find("DOSAGE")
                            substring = contents[start:end]
                            matches = ["cancer", "non-small cell lung cancer", "breast cancer",
                                       "gastric or gastroesophageal junction adenocarcinoma", "urothelial carcinoma",
                                       "colorectal cancer", "pancreatic adenocarcinoma", "Solid tumors", "prostate cancer"]

                            if any(x in substring for x in matches):
                                final_string.append("Accepted")
                            else:
                                final_string.append("Rejected")
                    except:
                        final_string.append("Not a label")
                print(final_string)
            except:
                print("submission not found")
        except:
            print("submission_name not found")
    return 0







# connect_gspread()


json_data = process_json()
processed_data = process_data(json_data)
update_fda_screening_sheet(processed_data)





# process_pdf(json_data)


# processed_pdf = StringIO(pdfFileObj.data)
# pdfReader = PyPDF2.PdfFileReader(processed_pdf)
# print(pdfReader.numPages)
# # pageObj = pdfReader.getPage(0)
# # print(pageObj.extractText)
