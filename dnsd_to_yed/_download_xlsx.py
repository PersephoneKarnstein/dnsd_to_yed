"""This is the updated photon script I wrote, minus the image download."""

import re, requests
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from alive_progress import alive_bar

def set_profile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference( "network.cookie.lifetimePolicy", 2 )
    profile.set_preference( "network.dns.disablePrefetch", True )
    profile.set_preference( "network.http.sendRefererHeader", 0 )
    profile.set_preference( "permissions.default.image", 2 )
    profile.update_preferences()
    options = Options()
    options.headless = True
    browser=webdriver.Firefox(profile, options=options)
    return browser

def dnsdumpster(domain, output_dir="."):
    """Query dnsdumpster.com.
    for reasons known only to Python Jesus, the xsl download consistently failed 
    using pure requests and succeeded using selenium, so after two days of trying
    and failing to make it work in requests I just rewrote the whole script using
    a headless selenium browser."""

    print('Fetching DNS information from DNSdumpster...')
    with alive_bar(total=4) as bar:
        browser=set_profile()
        bar()
        browser.get('https://dnsdumpster.com/')
        csrf_token = re.search(r'name=\"csrfmiddlewaretoken\" value=\"(.*?)\"', browser.page_source).group(1)
        cookies = {'name':'csrftoken', 'value': csrf_token}    
        browser.add_cookie(cookies)
        bar()

        def interceptor(request):
            """this is the only part that is somewhat sneaky - selenium is fiddly about
            adding headers programmatically so we here use an extension called Selenium-
            Wire to add that functionality, and then assert that for every request made
            using this browser instance, we want to intercept it and add a Referrer
            header."""
            request.headers['Referer'] = 'https://dnsdumpster.com/'

        browser.request_interceptor = interceptor

        searchBar = browser.find_element_by_xpath('//*[@id="regularInput"]')
        searchBar.send_keys(domain)
        searchButton = browser.find_element_by_xpath('/html/body/div/div/section/div[1]/div[2]/div[1]/div/form/div[2]/button')
        searchButton.click()
        bar()
        soup = BeautifulSoup(browser.page_source, features="lxml")
        spreadsheet = soup.find_all(href=re.compile(".xls"))[0]
        uri = spreadsheet.attrs["href"]
        s = requests.session()
        s.cookies.update( {c['name']:c['value'] for c in browser.get_cookies()})
        xlsx = s.get('https://dnsdumpster.com/'+uri)
        bar()
        if xlsx.status_code == 200:
            with open('%s/%s.xlsx' % (output_dir, domain), 'wb') as f:
                f.write(xlsx.content)
        return '%s/%s.xlsx' % (output_dir, domain)