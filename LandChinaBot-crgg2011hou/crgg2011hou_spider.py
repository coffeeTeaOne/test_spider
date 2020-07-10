import binascii
import requests_html
from urllib.parse import unquote
from win32api import GetSystemMetrics
from requests_html import AsyncHTMLSession
import re

from retrying import retry

from log_script.data_log import Logger
from parseFont import replace_content
import os, time
from scrapy.selector import Selector
import requests

from selenium_chrome import ChromeGetResponse


class LandChinaBot:
    info_all = []
    url = 'https://www.landchina.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Cookie':"security_session_verify=62bb2af78e556df058bf2a48e8030835; security_session_high_verify=1a7d921d5da823c091d0b0786ff3002e; ASP.NET_SessionId=raswqv40wxbjnh2myp1oo1ex; Hm_lvt_83853859c7247c5b03b527894622d3fa=1594001191,1594104087,1594256998,1594345952; Hm_lpvt_83853859c7247c5b03b527894622d3fa=1594346524"
    }
    data = None

    def __init__(self, city_code, city_name,province_name):
        self.city_name = city_name
        self.province_name = province_name
        self.getCityInfo(city_code, city_name)
        self.async_session = AsyncHTMLSession()
        self.logger = Logger().logger

    def getCityInfo(self, city_code, city_name):
        # 894e12d9-6b0f-46a2-b053-73c49d2f706d：出让公告2011后
        # 894e12d9-6b0f-46a2-b053-73c49d2f706d
        city_info = unquote(f'894e12d9-6b0f-46a2-b053-73c49d2f706d:{city_code}' + u"▓~" + city_name)
        city_info = city_info.encode("gb18030")
        self.data = {
            'TAB_QuerySubmitConditionData': city_info,
        }

    def to_csv(self, datas):
        """
        存储csv文件逻辑
        :param data:
        :return:
        """
        import csv
        file_name = f'./中国土地市场-出让公告2011后-{self.province_name}.csv'
        if not os.path.exists(file_name):
            names = [name for name in datas.keys()]
            with open(file_name, 'a', newline='') as f:
                writer = csv.writer(f)
                if isinstance(names, list):
                    # 单行存储
                    if names:
                        writer.writerow(names)
                        f.close()
        # 存数据
        data = [i for i in datas.values()]
        try:
            with open(file_name, 'a', newline='') as f:
                writer = csv.writer(f)
                if isinstance(data, list):
                    # 单行存储
                    if data:
                        writer.writerow(data)
                        f.close()
                        return True
                    else:
                        return False
                else:
                    # print(type(data))
                    return False
        except Exception as e:
            raise e.args

    def to_csv_content(self, datas):
        """
        存储大文本
        :param data:
        :return:
        """
        import csv
        file_name_content = f'./content_data/中国土地市场-出让公告2011后大文本-{self.province_name}.csv'
        if not os.path.exists(file_name_content):
            names = [name for name in datas.keys()]
            with open(file_name_content, 'a', newline='') as f:
                writer = csv.writer(f)
                if isinstance(names, list):
                    # 单行存储
                    if names:
                        writer.writerow(names)
                        f.close()
        # 存数据
        data = [i for i in datas.values()]
        try:
            with open(file_name_content, 'a', newline='') as f:
                writer = csv.writer(f)
                if isinstance(data, list):
                    # 单行存储
                    if data:
                        writer.writerow(data)
                        f.close()
                        return True
                    else:
                        return False
                else:
                    # print(type(data))
                    return False
        except Exception as e:
            raise e.args


    async def getCookie(self):
        response = await self.async_session.get(self.url, headers=self.headers)

    @retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
    def my_request_post(self, link):
        response = requests.post(link, data=self.data, headers=self.headers)
        info = Selector(text=response.content.decode('gbk')).xpath('//*[@id="TAB_contentTable"]/tbody/tr')
        if not info:
            self.headers['Cookie'] = ChromeGetResponse().run_request(link)
            response = requests.post(link, data=self.data, headers=self.headers)
            info = Selector(text=response.content.decode('gbk')).xpath('//*[@id="TAB_contentTable"]/tbody/tr')
            if not info:
                raise Exception('error')
        return response

    @retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
    def my_request_get(self, link):
        response = requests.get(link, headers=self.headers, timeout=60)
        if response.status_code not in [200]:
            time.sleep(1)
            raise Exception('error')
        return response

    async def getInfo(self, session):
        # detail_link = []
        # link = f'{self.url}default.aspx?tabid=263'
        link = f'{self.url}default.aspx?tabid=261'
        for page in range(1, 201):
            self.data['TAB_QuerySubmitPagerData'] = str(page)
            self.logger.info(str(self.city_name) + '页数：' + str(page))
            info = []
            try:
                try:
                    response = self.my_request_post(link)
                except:
                    self.headers['Cookie'] = ChromeGetResponse().run_request(link)
                    response = requests.post(link, data=self.data, headers=self.headers)

                info = Selector(text=response.content.decode('gbk')).xpath('//*[@id="TAB_contentTable"]/tbody/tr')
                for sub_raw in info[1:]:
                    info_basic = {}
                    basic_value = []
                    sub_list = sub_raw.xpath('td')
                    for i, info_sub in enumerate(sub_list):
                        if i == 0:
                            info_sub = info_sub.xpath('text()').extract()[0][:-1]
                            basic_value.append(info_sub)
                        elif i > 0 and i != 2:
                            info_sub = info_sub.xpath('text()').extract()[0]
                            basic_value.append(info_sub)
                        else:
                            link_sub = info_sub.xpath('a/@href').extract()[0]
                            try:
                                info_sub = info_sub.xpath('a/text()').extract()[0]
                                # info_sub = info_sub.xpath('a/span/@title').extract()[0]
                            except IndexError:
                                info_sub = info_sub.xpath('a/span/@title').extract()[0]
                            basic_value.append(info_sub)
                    try:
                        details = await self.getDetail(link_sub, self.async_session)
                    except Exception as e:
                        print(e.args)
                        continue

                    info_basic['省市'] = self.province_name
                    info_basic['城市'] = self.city_name
                    info_basic['行政区'] = basic_value[1]

                    info_basic['供应公告标题'] = basic_value[2]
                    ggbh = ''.join(re.findall(r'[\(|（]([\s|\S]*)[\)|）]',str(basic_value[2])))
                    print(ggbh)
                    info_basic['公告类型'] = basic_value[3]
                    info_basic['发布时间'] = basic_value[4]
                    info_basic['网上创建时间'] = basic_value[5]

                    # info_basic['地块公示信息'] = details
                    for det in details:
                        info_ba = {}

                        info_ba = {**info_basic, **det}
                        all_data = {'省市': '','城市': '', '行政区': '', '行政区详情': '', '供应公告标题': '', '公告编号': '', '公告类型': '', '发布时间': '',
                                    '网上创建时间': '',
                                    '宗地编号：': '', '宗地总面积：': '', '宗地面积':'', '宗地坐落：': '', '出让年限：': '', '容积率：': '', '建筑密度(%)：': '',
                                    '绿化率(%)：': '', '建筑限高(米)：': '', '土地用途明细：': '', '主要用途：': '', '用途名称': '', '面积': '',
                                    '投资强度：': '', '保证金：': '', '估价报告备案号': '', '场地平整': '', '现状土地条件': '',
                                    '起始价：': '', '加价幅度：': '', '挂牌开始时间：': '',
                                    '挂牌截止时间：': '', '备注：': '', '地块位置': '', '土地用途：': '',
                                    '土地面积(公顷)': '',
                                    '招标开始时间：': '', '招标截止时间：': '', '拍卖时间': '',
                                    '拍卖地点': '', '挂牌地点': '', '招标地点': '',
                                    '开标时间': '', '开标地点': '',
                                    '获取出让文件开始时间': '', '获取出让文件截止时间': '', '获取出让文件地点': '', '提交书面申请开始时间': '',
                                    '提交书面申请截止时间': '',
                                    '提交书面申请地点': '', '竞买保证金截止时间': '', '确认竞买资格时间': '', '确认投标资格时间': '',
                                    '活动时间': '', '活动地点': '',
                                    '联系地址': '', '联系人': '', '联系电话': '', '开户单位': '', '开户银行': '', '银行账号': ''}
                        info_all = {**all_data, **info_ba}

                        if ggbh:
                            info_basic['公告编号'] = ggbh
                        info_all_last = {}
                        for k, v in info_all.items():
                            if k in ['估价报告备案号', '银行账号', '联系电话', '宗地编号：']:
                                info_all_last[k] = '\t' + str(v).replace(',','，')
                            else:
                                info_all_last[k] = str(v).replace(',','，')
                        print(info_all_last)
                        self.to_csv(info_all_last)
                if info and len(info) < 30:
                    break
            except Exception as e:
                self.logger.info('地址页数错误:' + str(page))
                self.logger.error(e.args)
                if info and len(info) < 30:
                    break
                else:
                    continue

    async def getDetail(self, link, session):
        link = f'{self.url}{link}'
        print(link)
        # link = 'https://www.landchina.com//DesktopModule/BizframeExtendMdl/workList/bulWorkView.aspx?wmguid=20aae8dc-4a0c-4af5-aedf-cc153eb6efdf&recorderguid=c192ff32-c530-4989-9f8f-cc579bec4865&sitePath='
        try:
            # time.sleep(1)
            # response = requests.get(link, headers=self.headers)
            response = self.my_request_get(link)
        except:
            self.headers['Cookie'] = ChromeGetResponse().run_request('http://www.landchina.com/default.aspx?tabid=261')
            response = self.my_request_get(link)

        ttf_url = re.findall(r"truetype[\s|\S]*styles/fonts/([\s|\S]*?)'[\s|\S]*woff'\)", response.content.decode('gb18030'))[0]
        ttf_content = requests.get(f'{self.url}/styles/fonts/{ttf_url}', headers=self.headers)
        new_font_name = f"{link.split('recorderguid=')[1]}.ttf"
        with open(new_font_name, 'wb') as f:
            f.write(ttf_content.content)
        sele_xpath = Selector(text=response.content.decode('gb18030'))
        # 行政区
        xzq = sele_xpath.xpath('//*[@id="lblXzq"]/text()').extract_first()
        gonggaobianhao = sele_xpath.xpath('//*[@id="tdContent"]/table/tr[2]/td/text()').extract_first()
        info_text_all = sele_xpath.xpath('//*[@id="tdContent"]//td/div')
        other_text = sele_xpath.xpath('//*[@id="tdContent"]//td/p//text()').extract()
        bg_all = []
        for info_t in info_text_all:
            info_text = info_t.xpath('table//text()').extract()
            info_temp = '#'.join(list(filter(None, [str(ir).replace(' ', '').replace('\t', '') for ir in info_text])))
            bg_all.append(info_temp)
        info = '$$$$'.join(bg_all)
        gonggaobianhao = str(gonggaobianhao).replace('\t', '')
        other = list(filter(None, [str(ot).replace('\t', '') for ot in other_text]))
        other = '&'.join(other)
        # 替换繁体字
        info_all = replace_content(f'{gonggaobianhao}||||{info}****{other}', link.split('recorderguid=')[1])

        # 存储大文本
        self.to_csv_content({'内容链接':link,'内容文本':info_all,'主键MD5':self.to_md5(str(link))})
        if not info_all:
            return False
        # print(info_all)
        names = ['行政区详情', '宗地编号：', '宗地总面积：','宗地面积', '宗地坐落：', '出让年限：', '容积率：', '建筑密度(%)：',
                 '绿化率(%)：', '建筑限高(米)：', '土地用途明细：', '主要用途：', '用途名称', '面积',
                 '投资强度：', '保证金：', '估价报告备案号', '场地平整', '现状土地条件', '起始价：', '加价幅度：',
                 '备注：', '地块位置', '土地用途：', '土地面积(公顷)',

                 '挂牌开始时间：', '挂牌截止时间：', '招标开始时间：', '招标截止时间：', '拍卖时间',
                 '拍卖地点', '挂牌地点', '招标地点',
                 '开标时间', '开标地点',
                 '获取出让文件开始时间', '获取出让文件截止时间', '获取出让文件地点', '提交书面申请开始时间', '提交书面申请截止时间',
                 '提交书面申请地点', '竞买保证金截止时间', '确认竞买资格时间', '确认投标资格时间',
                 '活动时间', '活动地点',

                 '联系地址', '联系人', '联系电话', '开户单位', '开户银行', '银行账号']
        gonggaobianhao = info_all.split('||||')[0].split(' ')[0]
        info_all = info_all.split('||||')[1]
        info = info_all.split('****')[0]  # 表格信息
        other = info_all.split('****')[1]  # 其他内容信息

        infos = list(filter(None, info.split('$$$$')))

        # 多表格解析逻辑
        content_all = []
        for info in infos:
            result_info = info.split('#')
            # 添加一个空元素，防止后面解析报错
            result_info.append('')

            # 解析表格逻辑
            content_dict = dict()
            for i, inf in enumerate(result_info):
                if inf in names:
                    if inf in ['用途名称', '面积']:
                        if inf == '用途名称':
                            yt = '#'.join(
                                re.findall(r'[\u4E00-\u9FA5]+', re.findall(r'用途名称#面积#([\s|\S]+)#投资强度', info)[0]))
                            if yt:
                                content_dict[inf] = yt
                            else:
                                content_dict[inf] = ''
                        else:
                            mj = '#'.join(re.findall(r'[\d|\.]+', re.findall(r'用途名称#面积#([\s|\S]+)#投资强度', info)[0]))
                            if mj:
                                content_dict[inf] = mj
                            else:
                                content_dict[inf] = ''
                    elif result_info[i + 1] in names or '场地平整' in result_info[i + 1] or '现状土地条件' in result_info[i + 1]:
                        content_dict[inf] = ''

                    else:
                        content_dict[inf] = str(result_info[i + 1])

                elif '现状土地条件' in inf:
                    content_dict['现状土地条件'] = inf

                elif '场地平整' in inf:
                    content_dict['场地平整'] = inf
                else:
                    pass

            # 非表格信息
            # print(other)
            content_dict['联系电话'] = ''.join(re.findall(r'&[\s|\S]*?联系电话：([\s|\S]*?)&', other))
            content_dict['银行账号'] = ''.join(re.findall(r'&[\s|\S]*?银行帐号：([\s|\S]*)', other))
            content_dict['联系人'] = ''.join(re.findall(r'&[\s|\S]*?[联系人|联 系 人]：([\s|\S]*?)&', other))
            content_dict['联系地址'] = ''.join(re.findall(r'&[\s|\S]*?联系地址：([\s|\S]*?)&', other))
            content_dict['开户单位'] = ''.join(re.findall(r'&[\s|\S]*?开户单位：([\s|\S]*?)&', other))
            content_dict['开户银行'] = ''.join(re.findall(r'&[\s|\S]*?开户银行：([\s|\S]*?)&', other))

            # print(content_dict)

            other_content = other.replace(' ','')
            content_dict['招标开始时间'] = ''.join(re.findall(r'六、本次国有土地使用权招标活动定于&([\s|\S]*?)&至&[\s|\S]*&在&', other_content))
            content_dict['招标截止时间'] = ''.join(re.findall(r'六、本次国有土地使用权招标活动定于&[\s|\S]*&至&([\s|\S]*?)&在&', other_content))
            content_dict['拍卖时间'] = ''.join(re.findall(r'六、本次国有土地使用权拍卖活动定于&([\s|\S]*?)&在&[\s|\S]*&进行', other_content))
            content_dict['拍卖地点'] = ''.join(re.findall(r'六、本次国有土地使用权拍卖活动定于&[\s|\S]*&在&([\s|\S]*?)&进行', other_content))
            content_dict['挂牌地点'] = ''.join(re.findall(r'挂牌活动&在&([\s|\S]*?)&进行', other_content))
            content_dict['招标地点'] = ''.join(re.findall(r'六、本次国有土地使用权招标活动定于&[\s|\S]*&在&([\s|\S]*?)&进行[\s|\S]*&开标', other_content))
            content_dict['开标时间'] = ''.join(
                re.findall(r'六、本次国有土地使用权招标活动定于&[\s|\S]*&进行。&([\s|\S]*?)&在&[\s|\S]*&开标', other_content))
            content_dict['开标地点'] = ''.join(re.findall(r'六、本次国有土地使用权招标活动定于[\s|\S]*&在&([\s|\S]*?)&开标', other_content))
            content_dict['获取出让文件开始时间'] = ''.join(re.findall(r'出让文件。申请人可于&([\s|\S]*?)&至[\s|\S]*&到&', other_content))

            content_dict['获取出让文件截止时间'] = ''.join(
                re.findall(r'出让文件。申请人可于&[\s|\S]*&至&([\s|\S]*?)&到&', re.findall(r'四([\s|\S]*?)五', other_content)[0]))

            content_dict['获取出让文件地点'] = ''.join(re.findall(r'出让文件。申请人可于&[\s|\S]*&到&([\s|\S]*?)&获取', other_content))
            content_dict['提交书面申请开始时间'] = ''.join(re.findall(r'五、申请人可于&([\s|\S]*?)&至&[\s|\S]*&向我局提交书面申请', other_content))
            content_dict['提交书面申请截止时间'] = ''.join(
                re.findall(r'五、申请人可于&[\s|\S]*&至&([\s|\S]*?)&到&[\s|\S]*&向我局提交书面申请', other_content))
            content_dict['提交书面申请地点'] = ''.join(re.findall(r'五、申请人可于&[\s|\S]*&到&([\s|\S]*?)&向我局提交书面申请', other_content))
            content_dict['竞买保证金截止时间'] = ''.join(re.findall(r'保证金的截止时间为&([\s|\S]*?)&', other_content))

            content_dict['确认竞买资格时间'] = ''.join(re.findall(r'我局将在&([\s|\S]*?)&前确认其[\s|\S]*资格', other_content))
            content_dict['确认投标资格时间'] = ''.join(re.findall(r'我局将在&([\s|\S]*?)&前确认其投标资格', other_content))

            content_dict['活动时间'] = ''.join(re.findall(r'公开公告活动定于&([\s|\S]*?)&在&[\s|\S]*进行', other_content))
            content_dict['活动地点'] = ''.join(re.findall(r'公开公告活动定于&[\s|\S]*&在&([\s|\S]*?)进行', other_content))

            content_dict['联系地址'] = ''.join(re.findall(r'联系地址：([\s|\S]*?)&', other_content))

            content_dict['开户单位'] = ''.join(re.findall(r'&开户单位：([\s|\S]*?)&', other_content))
            content_dict['开户银行'] = ''.join(re.findall(r'&开户银行：([\s|\S]*?)&', other_content))
            content_dict['行政区详情'] = xzq
            content_dict['公告编号'] = gonggaobianhao

            content_dict['内容链接'] = link
            content_dict['主键MD5'] = self.to_md5(str(link))
            content_dict['爬取时间'] = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
            content_all.append(content_dict)
            # 每个表格返回一条数据

        return content_all

    async def run(self):
        # await self.getCookie()
        await self.getInfo(self.async_session)

    def to_md5(self, txt):
        import hashlib
        m = hashlib.md5()
        m.update(txt.encode())
        return m.hexdigest()

    def main(self):
        self.async_session.run(self.run)


if __name__ == '__main__':
    # bot = LandChinaBot('1301', '石家庄市','河北省')
    bot = LandChinaBot('31', '上海市','上海市')
    bot.main()


