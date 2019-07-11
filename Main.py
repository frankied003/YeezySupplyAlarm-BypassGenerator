from bs4 import BeautifulSoup as soup
import json
import pprint
from colorama import init, Fore, Back, Style
import requests
import time
import datetime
from pygame import mixer

# grabs all the data from the json file
def getData():
    with open('config.json') as f:
        data = json.load(f)
    return data

#getting data, setting up text formats
data = getData()
pp = pprint.PrettyPrinter(indent=3)
init(convert=True)

session = requests.session()
r = session.get(data['ProductLink'])

def checkPasswordPage():
    if "password" in r.url:
        print(Fore.RED + "Password page is up!")
        mixer.init()
        mixer.music.load('Kanye West  Gold Digger ft. Jamie Foxx.mp3')
        mixer.music.play()
        time.sleep(10000)
    else:
        print("Password page down, continuing processes...")
    return r

def addToCart():
    r = session.get(data['ProductLink'])
    bs = soup(r.text, "html.parser")
    scripts = bs.findAll('script')
    jsonObj = None

    variantArray = []

    for s in scripts:
        if 'var meta' in s.text:
            script = s.text
            script = script.split('var meta = ')[1]
            script = script.split(';\nfor (var attr in meta)')[0]

            jsonStr = script
            jsonObj = json.loads(jsonStr)

    for value in jsonObj['product']['variants']:
        variantID = value['id']
        variantArray.append(variantID)

    print(variantArray)
    atcLink = data['Store'] + '/cart/' + str(variantArray[0]) + ':1'
    r = session.get(atcLink)

    inqueue = True
    while inqueue == True:
        if "queue" in r.url:
            time.sleep(10)
            print("In Queue...")
        else:
            break

    # remove it from cart, but url with item in cart is still available (named url)
    qurl = r.url
    url = "/".join(qurl.split("/")[:6])
    bs2 = soup(r.text, "html.parser")
    authToken = bs2.find('input', {"name": "authenticity_token"})['value']
    checkoutId = bs2.find('input', {"name": "checkout[line_items][0][id]"})['value']
    payload1 = {
        "utf8": u'\u2713',
        "_method": "patch",
        "authenticity_token": authToken,
        "checkout[line_items][0][quantity]": '0',
        "checkout[line_items][0][id]": checkoutId,
        "commit": "Continue"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }
    r = session.post(url, headers=headers, data=payload1)
    return url

def generateBypassLink():
    checkPasswordPage()
    i = 0
    while i <= data['NumberOfLinks']:
        url = addToCart()
        confirmedCheckoutLink = url + '?step=contact_information'
        print(Fore.YELLOW + confirmedCheckoutLink)
        time1 = datetime.datetime.now()
        f = open("checkoutLinks.txt", "a")
        f.write(confirmedCheckoutLink)
        f.write("  ")
        f.write(str(time1))
        f.write("\n")
        f.close()
        i = i + 1
        time.sleep(data['Delay'])

generateBypassLink()
