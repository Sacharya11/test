from datetime import datetime
from datetime import date
from datetime import time
import jaydebeapi
import time
from selenium import webdriver
from itertools import cycle
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
#from decimal import Decimal as D

start_time = time.time()

#Parameters to be changed
Marketid = 1
Begin_date = date(2019,01,01)
End_date = date(2019,9,01)
Crawldate = datetime.today().strftime('%Y-%m-%d')

#external = 98.6.238.11
#internal =192.168.1.153:5480
Connection = jaydebeapi.connect("org.netezza.Driver",
                               'jdbc:netezza://192.168.1.153:5480/RESEARCH',
                               {'user': "sacharya", 'password': "Research789"},
                               jars = "/Users/sarmilaacharya/Documents/Library/nzjdbc3.jar")
cursor = Connection.cursor()

outputfile = "%s_ZacksEarnings_1.csv" %(Crawldate)

with open(outputfile, "wb") as ofile:
    ofile.write("Earnings Date, Stocks Symbol, MarketCap, Time, Estimate ,Reported, Surprise, %Surp, Price Change,Crawl Date, Company Namen")

Query_1 = """SELECT MARKETID, RPTDAY, REGULAR_CLOSETOCLOSEPNL
             FROM ADMIN.MARKETDAILYPNL
             WHERE marketid = %s AND rptday >='%s' and rptday <='%s'
             ORDER BY rptday asc""" %(Marketid,Begin_date,End_date)

cursor.execute(Query_1)

Data = cursor.fetchall()

def Earnings_data(browser):
    Even_Earning = []
    Odd_Earning = []
    Total_Earning = []
    #time.sleep(3)

    #First Evenclass and first Oddclass lines are fine, other are test cases
    Evenclass = browser.find_elements_by_class_name('even')

    Oddclass = browser.find_elements_by_class_name('odd')

    for (ab, cd) in zip(Evenclass, Oddclass):
        Odd_Earning.append((cd.text))
        Even_Earning.append((ab.text))
        Total_Earning = Odd_Earning + Even_Earning
    return Total_Earning

def WriteEarnings():

    Earning = Earnings_data(browser)
    for val in Earning:
        try:
            valsplit = val.split(' ')
            #name = ''.join([''.join([n, ' ']) for n in valsplit[1:-4]])
            name = ''.join([''.join([n, ' ']) for n in valsplit[1:-4]])
            name = name.replace(',','')
            symbol = valsplit[0]
            MKCap = valsplit[-4].replace(',','')
            AnnounceTime = valsplit[-3]
            Estimate = valsplit[-2].replace(',','')
            Reported = valsplit[-1].split("\n")[0]
            Surprise = valsplit[-1].split("\n")[1]
            Surp_percentage = valsplit[-1].split("\n")[2].replace(',','')
            PriceChange = valsplit[-1].split("\n")[3]

            with open(outputfile, "a") as ofile:
                ofile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (str(StartDate), symbol, MKCap, AnnounceTime, Estimate,
                                                                    Reported, Surprise,Surp_percentage, PriceChange, Crawldate, name))
    ##Put database upload code here
        except IndexError:
            continue
    time.sleep(3)
    return
try:
    for row in Data:
        StartDate = datetime.strptime(row[1], '%Y-%m-%d').date()

        browser = webdriver.Chrome(executable_path="/Users/sarmilaacharya/Desktop/files/Prediction/HedgeFund/Chromedriver")
        browser.get('https://www.zacks.com/earnings/earnings-calendar?date=%s&event_type=1'%(time.mktime(StartDate.timetuple())))

        time.sleep(4)
        try:
            Pagenumber = [int(n.text.encode('utf-8')) for n in browser.find_elements_by_class_name('paginate_button') if str.isdigit(n.text.encode('utf-8'))]
            Maxnum = sorted(Pagenumber)[-1]
        except IndexError:
            continue

        count = 0
        while count<Maxnum:
            Answer = WriteEarnings()
            Even_Earning = []
            Odd_Earning = []

            time.sleep(4)
            count = count + 1
            if count<Maxnum:
                #browser.execute_script("window.scrollTo(0,1500);")
                #button = browser.find_element_by_xpath('//*[@id="earnings_rel_data_all_table_next"]')
                #button = browser.find_element_by_xpath('//*[@id="earnings_rel_data_all_table_next"]')
                #browser.execute_script('arguments[0].scrollIntoView();', button)

                try:
                    disclosure = browser.find_element_by_id('accept_cookie')
                    disclosure.click()
                except NoSuchElementException as ex:
                    print "no cookie"
                time.sleep(5)
                button = browser.find_element_by_id("earnings_rel_data_all_table_next")
                actions = ActionChains(browser)
                actions.move_to_element(button).perform()

                time.sleep(5)
                button.click()
            else:
                continue
        browser.quit()

#except Exception as e:
except StaleElementReferenceException:
    pass
    #    raise e
    #     print "Stale"

finally:
    browser.quit()
    print "time taken is", (time.time()-start_time)/60


""""###Database part####

Query_insert = INSERT INTO TABLE ........
                (RPTDAY, SYMBOL,MARKETCAP,TIME,ESTIMATE,REPORTED,SURPRISE,SURPRISEPERCENT,PRICECHANGE,CRAWLDATE,COMPANYNAME)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);% (str(StartDate), symbol, MKCap, AnnounceTime, Estimate,
                                                                    Reported, Surprise,Surp_percentage, PriceChange, Crawldate, name))"""

