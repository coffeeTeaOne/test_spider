import requests
import re
import os
import time
# import pymongo
import random
import csv
from urllib.parse import unquote
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from fontTools.ttLib import TTFont
from hashlib import md5
from requests.exceptions import ReadTimeout, ConnectionError
from retrying import retry
from scrapy.selector import Selector
from fonts import font_md5_list_dict
from keyword_list import *
from selenium_chrome import ChromeGetResponse


class LandChina:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.landchina.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.landchina.com/default.aspx?tabid=226&ComName=default',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': 'security_session_verify=f5b69eb6f3f6ed83887197f42c0ae1d9; security_session_high_verify=725ac9c3017a8717dc14e35bb48788ce; ASP.NET_SessionId=0fw00blfy4grmdt5qdu3vhub; Hm_lvt_83853859c7247c5b03b527894622d3fa=1593570627,1593670031,1593743742,1594001191; Hm_lpvt_83853859c7247c5b03b527894622d3fa=1594002390',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        }

        # client = pymongo.MongoClient()
        # db = client['中国土地市场网']
        # self.collection = db['供地计划']

        self.md5_list = []

    def get_total_page(self, city_code, city_name):
        print(f'正在获取【{city_name}】总页数')

        url = 'http://www.landchina.com/default.aspx?tabid=226'
        city_info = f'6506735a-523d-4bde-9674-121656045ed1:{city_code}' + u"▓~" + city_name
        city_info = city_info.encode('gbk')

        data = {
            '__VIEWSTATE': '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6IzAwMDAwMDtCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2dkamhfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfA2QWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwF/gY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHBzOi8vd3d3LmxhbmRjaGluYS5jb20vIj48aW1nIGJvcmRlcj0iMCIgYWx0PSIiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjEiIHNyYz0iL1VzZXIvZGVmYXVsdC9VcGxvYWQvZmNrL2ltYWdlL3Rkc2N3X2xvZ2UucG5nIiAvPjwvYT4mbmJzcDs8YnIgLz4NCiZuYnNwOzxzcGFuIHN0eWxlPSJjb2xvcjogI2ZmZmZmZiI+Q29weXJpZ2h0IDIwMDgtMjAyMCBEUkNuZXQuIEFsbCBSaWdodHMgUmVzZXJ2ZWQmbmJzcDsmbmJzcDsmbmJzcDsgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPg0KdmFyIF9iZGhtUHJvdG9jb2wgPSAoKCJodHRwczoiID09IGRvY3VtZW50LmxvY2F0aW9uLnByb3RvY29sKSA/ICIgaHR0cHM6Ly8iIDogIiBodHRwczovLyIpOw0KZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOw0KPC9zY3JpcHQ+Jm5ic3A7PGJyIC8+DQrniYjmnYPmiYDmnIkmbmJzcDsg5Lit5Zu95Zyf5Zyw5biC5Zy6572RJm5ic3A7Jm5ic3A75oqA5pyv5pSv5oyBOua1meaxn+iHu+WWhOenkeaKgOiCoeS7veaciemZkOWFrOWPuCZuYnNwOzxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcxMjAzOTQxNOWPty00IOS6rOWFrOe9keWuieWkhzExMDEwMjAwMDY2NigyKSZuYnNwOzxiciAvPg0KPC9zcGFuPiZuYnNwOyZuYnNwOyZuYnNwOzxiciAvPg0KJm5ic3A7PC9zcGFuPjwvcD4fAQVkQkFDS0dST1VORC1JTUFHRTp1cmwoaHR0cDovL3d3dy5sYW5kY2hpbmEuY29tL1VzZXIvZGVmYXVsdC9VcGxvYWQvc3lzRnJhbWVJbWcveF90ZHNjdzIwMTNfeXdfMS5qcGcpO2RkDTfk3zy3/OKpCBCHbgi05UJMweySkuvcGrSSXAHoHng=',
            '__EVENTVALIDATION': '/wEdAAI65TLpQ2C6xZ3whmfpo+XfCeA4P5qp+tM6YGffBqgTjcX/m5nZ5kWXKYerzB3dqLF6mr6MhytJDh9cYNm5x51G',
            'hidComName': 'default',
            'TAB_QuerySortItemList': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
            'TAB_QuerySubmitConditionData': city_info,
            'TAB_QuerySubmitOrderData': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
            'TAB_RowButtonActionControl': '',
            'TAB_QuerySubmitPagerData': 1,
            'TAB_QuerySubmitSortData': ''
        }

        try:
            try:
                response = requests.post(url, headers=self.headers, data=data, timeout=60)
            except:
                self.headers['Cookie'] = ChromeGetResponse().run_request(url)
                response = requests.post(url, headers=self.headers, data=data, timeout=60)

            if response.status_code == 200:
                doc = pq(response.text)
                page = re.search(r'共(\d+)页', doc('*[align="right"].pager').text())
                if page:
                    print(f'【{city_name}】总页数：', int(page.group(1)))
                    return int(page.group(1))
                else:
                    print(f'【{city_name}】总页数：', 1)
                    return 1
            else:
                print('Status code:', response.status_code)

        except (ReadTimeout, ConnectionError) as e:
            print('连接异常，重试', e.args)
            self.get_total_page(city_code, city_name)

    @retry(stop_max_attempt_number=5,wait_random_min=1000,wait_random_max=2000)
    def parse_index(self, page, city_code, city_name):
        print(f'正在爬取【{city_name}】第【{page}】页')

        url = 'http://www.landchina.com/default.aspx?tabid=226'
        city_info = unquote(f'6506735a-523d-4bde-9674-121656045ed1:{city_code}' + u"▓~" + city_name)
        city_info = city_info.encode('gb18030')

        data = {
            # '__VIEWSTATE': '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6IzAwMDAwMDtCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2dkamhfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfA2QWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwF/gY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHBzOi8vd3d3LmxhbmRjaGluYS5jb20vIj48aW1nIGJvcmRlcj0iMCIgYWx0PSIiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjEiIHNyYz0iL1VzZXIvZGVmYXVsdC9VcGxvYWQvZmNrL2ltYWdlL3Rkc2N3X2xvZ2UucG5nIiAvPjwvYT4mbmJzcDs8YnIgLz4NCiZuYnNwOzxzcGFuIHN0eWxlPSJjb2xvcjogI2ZmZmZmZiI+Q29weXJpZ2h0IDIwMDgtMjAyMCBEUkNuZXQuIEFsbCBSaWdodHMgUmVzZXJ2ZWQmbmJzcDsmbmJzcDsmbmJzcDsgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPg0KdmFyIF9iZGhtUHJvdG9jb2wgPSAoKCJodHRwczoiID09IGRvY3VtZW50LmxvY2F0aW9uLnByb3RvY29sKSA/ICIgaHR0cHM6Ly8iIDogIiBodHRwczovLyIpOw0KZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOw0KPC9zY3JpcHQ+Jm5ic3A7PGJyIC8+DQrniYjmnYPmiYDmnIkmbmJzcDsg5Lit5Zu95Zyf5Zyw5biC5Zy6572RJm5ic3A7Jm5ic3A75oqA5pyv5pSv5oyBOua1meaxn+iHu+WWhOenkeaKgOiCoeS7veaciemZkOWFrOWPuCZuYnNwOzxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcxMjAzOTQxNOWPty00IOS6rOWFrOe9keWuieWkhzExMDEwMjAwMDY2NigyKSZuYnNwOzxiciAvPg0KPC9zcGFuPiZuYnNwOyZuYnNwOyZuYnNwOzxiciAvPg0KJm5ic3A7PC9zcGFuPjwvcD4fAQVkQkFDS0dST1VORC1JTUFHRTp1cmwoaHR0cDovL3d3dy5sYW5kY2hpbmEuY29tL1VzZXIvZGVmYXVsdC9VcGxvYWQvc3lzRnJhbWVJbWcveF90ZHNjdzIwMTNfeXdfMS5qcGcpO2RkDTfk3zy3/OKpCBCHbgi05UJMweySkuvcGrSSXAHoHng=',
            # '__EVENTVALIDATION': '/wEdAAI65TLpQ2C6xZ3whmfpo+XfCeA4P5qp+tM6YGffBqgTjcX/m5nZ5kWXKYerzB3dqLF6mr6MhytJDh9cYNm5x51G',
            'hidComName': 'default',
            'TAB_QuerySortItemList': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
            'TAB_QuerySubmitConditionData': city_info,
            'TAB_QuerySubmitOrderData': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
            'TAB_RowButtonActionControl': '',
            'TAB_QuerySubmitPagerData': page,
            'TAB_QuerySubmitSortData': ''
        }

        try:
            try:
                response = requests.post(url, headers=self.headers, data=data, timeout=60)
                t_xpath = Selector(text=response.text).xpath('//img[@class="verifyimg"]').extract()
                if t_xpath or response.status_code not in [200] :
                    self.headers['Cookie'] = ChromeGetResponse().run_request(url)
                    response = requests.post(url, headers=self.headers, data=data, timeout=60)
            except:
                self.headers['Cookie'] = ChromeGetResponse().run_request(url)
                response = requests.post(url, headers=self.headers, data=data, timeout=60)


            doc = pq(response.text)
            gts = doc('#TAB_contentTable > tbody > tr:gt(0)').items()
            for gt in gts:
                yield {
                    '行政区代码': gt('td:nth-child(2)').text().strip(),
                    'url': 'http://www.landchina.com/' + gt('td:nth-child(3) > a').attr('href')
                }


        except (ReadTimeout, ConnectionError) as e:
            print('连接异常，重试', e.args)
            # self.parse_index(page, city_code, city_name)

    def parse_detail(self, index, failed_time=0):
        if index:
            url = index.get('url')
            print('爬取详情页', url)
            try:
                try:
                    response = requests.get(url, headers=self.headers, timeout=60)
                    t_xpath = Selector(text=response.text).xpath('//img[@class="verifyimg"]').extract()
                    if t_xpath:
                        self.headers['Cookie'] = ChromeGetResponse().run_request(url)
                        response = requests.get(url, headers=self.headers, timeout=60)
                except:
                    self.headers['Cookie'] = ChromeGetResponse().run_request(url)
                    response = requests.get(url, headers=self.headers, timeout=60)
                if response.status_code == 200:
                    response.encoding = 'gbk'
                    doc = pq(response.text)
                    font_filename = self.download_woff(url, response.text)

                    detail = {
                        '文件标题': doc('#lblTitle').text().strip(),
                        '发布时间': doc('#lblCreateDate').text().strip()[5:],
                        '行政区': doc('#lblXzq').text().strip()[4:],
                        '行政区代码': index.get('行政区代码'),
                        '城市': '',
                        '供应计划年度': '',
                    }

                    region = re.search(r'>(.*?)>', detail['行政区'])
                    detail['城市'] = region.group(1).strip() if region else ''

                    for pattern in [r'(\d+)年', r'(\d+-\d+)年']:
                        year = re.search(pattern, detail['文件标题'])
                        if year:
                            detail['供应计划年度'] = year.group(1).strip()
                            break
                    else:
                        year = re.search(r'(\d+)年', detail['发布时间'])
                        if year:
                            detail['供应计划年度'] = year.group(1)
                    # 替换繁体字
                    raw_content = self.parse_font(doc('#tdContent').remove('table').text(), font_filename)

                    content_except_table = raw_content.replace('\n', '')

                    supply_gross = self.get_supply_gross(content_except_table)
                    detail['供应总量_总量'] = supply_gross if supply_gross else ''

                    new_construction = self.get_part_area(content_except_table, NEW_CONSTRUCTION_KEYWORD)
                    detail['供应总量_增量'] = new_construction if new_construction else ''

                    stock = self.get_part_area(content_except_table, STOCK_KEYWORD)
                    detail['供应总量_存量'] = stock if stock else ''

                    commercial_service = self.get_part_area(content_except_table, COMMERCIAL_SERVICE_KEYWORD)
                    detail['商服用地'] = commercial_service if commercial_service else ''

                    industrial_mining = self.get_part_area(content_except_table, INDUSTRIAL_MINING_KEYWORD)
                    detail['工矿仓储用地'] = industrial_mining if industrial_mining else ''

                    residence = self.get_part_area(content_except_table, RESIDENCE_KEYWORD)
                    detail['住宅用地_总量'] = residence if residence else ''

                    indemnificatory_housing = self.get_part_area(content_except_table, INDEMNIFICATORY_HOUSING_KEYWORD)
                    detail['住宅用地_保障性住房用地'] = indemnificatory_housing if indemnificatory_housing else ''

                    small_medium_housing = self.get_part_area(content_except_table, SMALL_MEDIUM_HOUSING_KEYWORD)
                    detail['住宅用地_中小套型商品房用地'] = small_medium_housing if small_medium_housing else ''

                    other_housing = self.get_part_area(content_except_table, OTHER_HOUSING_KEYWORD)
                    detail['住宅用地_普通商品房用地'] = other_housing if other_housing else ''

                    shanty_town_housing = self.get_part_area(content_except_table, SHANTY_TOWN_HOUSING_KEYWORD)
                    detail['住宅用地_棚户区改造住房用地'] = shanty_town_housing if shanty_town_housing else ''

                    transportation = self.get_part_area(content_except_table, TRANSPORTATION_KEYWORD)
                    detail['交通运输用地'] = transportation if transportation else ''

                    public_administration_service = self.get_part_area(content_except_table, PUBLIC_ADMINISTRATION_SERVICE_KEYWORD)
                    detail['公共管理与公共服务用地'] = public_administration_service if public_administration_service else ''

                    water_area_conservancy = self.get_part_area(content_except_table, WATER_AREA_CONSERVANCY_KEYWORD)
                    detail['水域及水利设施用地'] = water_area_conservancy if water_area_conservancy else ''

                    eduction = self.get_part_area(content_except_table, EDUCATION_KEYWORD)
                    detail['教育用地'] = eduction if eduction else ''

                    industrial = self.get_part_area(content_except_table, INDUSTRIAL_KEYWORD)
                    detail['工业用地'] = industrial if industrial else ''

                    public_welfare = self.get_part_area(content_except_table, PUBLIC_WELFARE_KEYWORD)
                    detail['公益事业用地'] = public_welfare if public_welfare else ''

                    special = self.get_part_area(content_except_table, SPECIAL_KEYWORD)
                    detail['特殊用地'] = special if special else ''

                    other = self.get_part_area(content_except_table, OTHER_KEYWORD)
                    detail['其他用地'] = other if other else ''
                    # 大文本
                    # detail['content'] = raw_content

                    self.save(detail, url)

                    # doc = pq(response.text)
                    # if doc('#tdContent table'):
                    #     for table in doc('#tdContent table > tbody'):
                    #         table_doc = pq(table)
                    #         if table_doc.text():
                    #             new_detail = detail.copy()
                    #             table_html = self.parse_font(table_doc.html(), font_filename)
                    #             # new_detail.update({'table': table_html})
                    #             # self.save(new_detail, url)
                    #
                    #             for table_detail in self.parse_table(table_html):
                    #                 terminal_detail = new_detail.copy()
                    #                 # terminal_detail.update(table_detail)
                    #                 self.save(terminal_detail, url)

                    # else:
                    #     detail.update({'table': ''})
                    #     self.save(detail, url)

                    os.remove(font_filename)

            except (ReadTimeout, ConnectionError) as e:
                failed_time += 1

                if failed_time <= 5:
                    print(f'失败次数{failed_time}，重试', e.args)
                    self.parse_detail(index, failed_time)
                else:
                    print('失败次数超过5次，放弃请求')
        else:
            pass

    def download_woff(self, url, html):
        try:
            woff = re.search(r"url\('(.*?\.woff\?fdipzone)'\) format", html)
            if woff:
                font_url = urljoin(url, woff.group(1))
                font_filename = re.search(r'fonts/(.*?)\?fdipzone', font_url).group(1)

                if not os.path.exists(font_filename):
                    print('下载字体文件', font_url)
                    response = requests.get(font_url, headers=self.headers, timeout=60)
                    if response.status_code == 200:
                        with open(font_filename, 'wb') as f:
                            f.write(response.content)
                        # time.sleep(2)
                        return font_filename
                else:
                    print('字体文件已存在', font_filename)
                    return font_filename
            else:
                print('找不到字体文件url')
        except (ReadTimeout, ConnectionError) as e:
            print('连接异常，重试', e.args)
            self.download_woff(url, html)

    @staticmethod
    def parse_font(text, font_filename):
        new_text = ''
        font = TTFont(font_filename)
        for each in text:
            each_unicode = each.encode('unicode_escape').decode('utf8').upper().replace(r'\U', 'uni')
            glyf = font['glyf'].glyphs.get(each_unicode)
            if glyf:
                content = glyf.data
                each_md5 = md5(content).hexdigest()
                for key, value in font_md5_list_dict.items():
                    if each_md5 == value:
                        each = key
            new_text += each

        return new_text

    @staticmethod
    def extract_sentence(text, keyword):
        """
        提取关键词所在片段（，或。）
        """
        sen_list = re.findall(r'.*?[,，;；。]', text)
        if sen_list:
            for sen in sen_list:
                if keyword in sen:
                    yield sen

    def get_supply_gross(self, text):
        for keyword in SUPPLY_GROSS_KEYWORD:
            for sen in self.extract_sentence(text, keyword):
                pattern = keyword + r'.*?(\d+(\.\d+)?\s?(公顷|亩|平方)(以内|以上)?)'
                matching = re.search(pattern, sen)
                if matching:
                    return re.sub(r'\s', '', matching.group(1))

    def get_part_area(self, text, keyword_list):
        for keyword in keyword_list:
            for sen in self.extract_sentence(text, keyword):
                pattern = keyword + r'.*?(\d+(\.\d+)?\s?(公顷|亩|平方)(以内|以上)?)'
                matching = re.search(pattern, sen)
                if matching:
                    return re.sub(r'\s', '', matching.group(1))

    def parse_table(self, html):
        doc = pq(html)

        first_row_list = []
        tr_index = 1
        for tr in doc('tr').items():
            if len(tr('td')) > 3 and re.sub(r'\s', '', tr.text()):
                first_row_list.append(tr_index)
                break
            tr_index += 1

        first_row_count = first_row_list[0]

        first_row_css = f'tr:nth-child({first_row_count}) > td'
        second_row_css = f'tr:nth-child({first_row_count + 1}) > td'

        first_row_text = doc(first_row_css).text().replace('M2', '㎡').replace('m2', '㎡').strip()
        # 表格第一行没有数字，代表是竖向表格
        if not re.search(r'\d', first_row_text):

            for td in doc(first_row_css).items():
                if td.attr('colspan'):
                    colspan = True
                    break
            else:
                colspan = False

            table_fields_first = []

            try:
                # 第一行有合并单元格
                if colspan:
                    colspan_index = 0
                    # 第一行字段
                    for td in doc(first_row_css).items():
                        if not td.attr('colspan'):
                            if td.text():
                                table_fields_first.append(self.handle_field_text(td.text()))
                            else:
                                table_fields_first.append('空白')
                        if td.text() and td.attr('colspan'):
                            # {合并单元格索引: 合并单元格个数}
                            table_fields_first.append(int(td.attr('colspan')))
                        colspan_index += 1

                    # 第二行字段
                    table_fields_second = []
                    for td in doc(second_row_css).items():
                        if td.text():
                            table_fields_second.append(self.handle_field_text(td.text()))
                        else:
                            table_fields_second.append('空白')

                    # 用第二行字段替换第一行合并单元格位置
                    for field in table_fields_first:
                        if isinstance(field, int):
                            index = table_fields_first.index(field)
                            for _ in range(field):
                                table_fields_first.insert(index, table_fields_second[0])
                                table_fields_second.pop(0)
                                index += 1
                            table_fields_first.remove(field)

                    # 遍历第二行之后的每一行
                    for tr in doc('tbody > tr:gt(1)').items():
                        if len(tr('td')) == len(table_fields_first):
                            for td in tr('td').items():
                                # 如果有一行全部为空，则抛弃这一行
                                if re.sub(r'\s', '', td.text()):
                                    table_detail = {}
                                    td_index = 0
                                    for each_td in tr('td').items():
                                        table_detail[table_fields_first[td_index]] = each_td.text().replace('\xa0', '')
                                        td_index += 1

                                    yield table_detail
                                    break

                # 第一行没有合并单元格
                else:
                    for td in doc(first_row_css).items():
                        if td.text():
                            table_fields_first.append(self.handle_field_text(td.text()))
                        else:
                            table_fields_first.append('空白')

                    # 遍历第一行之后的每一行
                    for tr in doc('tbody > tr:gt(0)').items():
                        if len(tr('td')) == len(table_fields_first):
                            for td in tr('td').items():
                                # 如果有一行全部为空，则抛弃这一行
                                if re.sub(r'\s', '', td.text()):
                                    table_detail = {}
                                    td_index = 0
                                    for each_td in tr('td').items():
                                        table_detail[table_fields_first[td_index]] = each_td.text().replace('\xa0', '')
                                        td_index += 1

                                    yield table_detail
                                    break
            except IndexError:
                yield {}

        # 第一行有数字，代表是横向表格
        else:
            table_detail = {}
            odd_list = []
            even_list = []

            # 奇数列
            for each_odd_td in doc('tbody td:nth-child(odd)').items():
                odd_list.append(self.handle_field_text(each_odd_td.text()))

            # 偶数列
            for each_even_td in doc('tbody td:nth-child(even)').items():
                even_list.append(each_even_td.text())

            # 一个表格中分多个字典
            if odd_list.count(odd_list[0]) > 1:
                try:
                    table_detail_list = []
                    index = 0
                    for odd in odd_list:
                        if odd in table_detail:
                            table_detail_list.append(table_detail)
                            table_detail = {odd: even_list[index]}
                        else:
                            table_detail[odd] = even_list[index]
                        index += 1
                    table_detail_list.append(table_detail)

                    for each_table_detail in table_detail_list:
                        if '' in each_table_detail:
                            each_table_detail.pop('')
                        yield each_table_detail

                except IndexError:
                    yield {}

            else:
                # 长度一致再合并成字典
                if len(odd_list) == len(even_list):
                    table_detail.update(dict(zip(odd_list, even_list)))
                    if '' in table_detail:
                        table_detail.pop('')
                    yield table_detail

    @staticmethod
    def handle_field_text(field):
        """
        处理字段文本
        """
        text = re.sub(r'[\s:：;；]', '', field).lower().replace('(', '（').replace(')', '）').replace('％', '%').replace('\\', '/').replace('m2', '㎡').replace('（㎡', '（㎡）') \
            .replace('（平方米）', '（㎡）').replace('（米）', '（m）')
        if text.count('（') > 1:
            text = text.replace('（', '', 1)
        if text.count('）') > 1:
            text = text.replace('）', '', 1)
        return text

    def save(self, detail, url):
        if detail:
            m = md5(str(detail).encode('utf8')).hexdigest()
            detail['md5'] = m
            if m not in self.md5_list:
                self.md5_list.append(m)
                detail['url'] = url
                detail['crawling_time'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))

                filename = '中国土地市场_供地计划.csv'
                if not os.path.exists(filename):
                    with open(filename, 'a', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=list(detail.keys()))
                        writer.writeheader()
                        writer.writerow(detail)
                else:
                    with open(filename, 'a', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=list(detail.keys()))
                        writer.writerow(detail)

                print(detail)
                # self.collection.insert_one(detail)

    def run(self, city_code, city_name):
        total_page = self.get_total_page(city_code, city_name)
        time.sleep(1)

        for page in range(1, total_page + 1):
        # for page in range(1, 10):
            for index in self.parse_index(page, city_code, city_name):
                time.sleep(random.uniform(5, 8))
                try:
                    self.parse_detail(index)
                except:
                    continue


if __name__ == '__main__':
    landchina = LandChina()
    landchina.run('13', '河北省')