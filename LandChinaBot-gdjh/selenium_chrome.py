import time
import requests,os,urllib.request
import json
import re
import csv
import sys
import base64
from retrying import retry
from lxml import etree
from time import sleep
import urllib3
import pandas as pd
from aip import AipOcr
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# from SpiderTools.tool import SpiderException,ResponseHTML, wash_url

# from SpiderTools.chrome_ip import create_proxyauth_extension
# from SpidersLog.icrwler_log import ICrawlerLog
# from proxy_ip import get_ip


class ChromeGetResponse(object):

    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}

    def __init__(self, ):
        # 浏览器初始化
        option = webdriver.ChromeOptions()
        option.add_argument("--start-maximized")
        # 暂时不用代理
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')  # 禁用 GPU 硬件加速，防止出现bug
        # 禁止图片加载
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # option.add_experimental_option("prefs", prefs)
        option.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"')
        # self.proxy = get_ip(False)
        # self.proxy = '49.68.187.125:4243'
        # print(self.proxy)

        # 设置代理方式一：
        # option.add_argument('--proxy-server=http://{}'.format(self.proxy))
        # /home/spiderjob/domain/tools/chromedriver
        # self.browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=option)  # 创建实例
        # self.browser = webdriver.Chrome(executable_path="/home/spiderjob/domain/tools/chromedriver", chrome_options=option)  # 创建实例
        # self.browser = webdriver.Chrome(executable_path=r"C:\Users\lyial\Desktop\coffee\venv/chromedriver", chrome_options=option)  # 创建实例
        self.browser = webdriver.Chrome( chrome_options=option)  # 创建实例

        # 设置代理方式二：
        # proxyauth_plugin_path = create_proxyauth_extension(
        #     proxy_host="XXXXX.com",
        #     proxy_port=9020,
        #     proxy_username="XXXXXXX",
        #     proxy_password="XXXXXXX"
        # )
        # option.add_extension(proxyauth_plugin_path)  # 设置代理
        # self.browser = webdriver.Chrome(chrome_options=option)
        self.wait = WebDriverWait(self.browser, 60)
        # self.wait = wait.WebDriverWait(self.browser, 60)
        # self.browser.get('https://www.baidu.com/?tn=22073068_3_oem_dg')
        # self.browser.get('https://per.spdb.com.cn')

    def read_image(self,path):
        """ APP_ID API_KEY SECRET_KEY，"""
        APP_ID = '16776610'
        API_KEY = 'LjOdMkuUHsHwb2YH89IGHiRL'
        SECRET_KEY = 'xns1EfjMD3uaNoSo9pqggFbfLS6FfIwW'
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        pic = open(path, 'rb')
        # 读取图片
        pic_text = pic.read()
        # 通用字识别
        message = client.basicGeneral(pic_text)
        code_image = message.get('words_result')[0].get("words")
        return code_image

    # 保存验证码图片
    def save_image(self,image_data, dir_path):
        image_data = base64.b64decode(image_data)  # 生成验证码
        with open(os.path.join(dir_path, "code.jpg"), 'wb')as f:
            f.write(image_data)

    #判断是否加载异常
    def driver_error(self,driver):
        num =0
        while num < 5:
            if "An error occurred" in driver.page_source or "500 Internal Server Error" in driver.page_source:
                driver.refresh()
                num += 1
                sleep(5)
            else:
                return True

    def run_request(self,  url, code_='0', page='0'):
        '''
        下载网页, 只要返回HTTPResponse就不再执行其他下载中间件
        :param request: scrapy整合的全局参数
        :param spider: spiders里的爬虫对象
        :return:
        '''
        # log_script = ICrawlerLog(name='spider').save
        # 新打开一个标签页, 访问新网址, 跳到当前页, 获取数据, 关闭当前页面, 回到原始页
        try:
            # view_url = wash_url(url)
            view_url = url
            # 访问目标网页
            js = 'window.open("{}");'.format(view_url)
            # time.sleep(2)
            self.browser.execute_script(js)

            handles = self.browser.window_handles
            if len(handles) > 4:
                raise Exception('网络错误, 请重启')
                # log_script.error('浏览器请求异常,请检查网络')
                # raise SpiderException('网络错误, 请重启')

            # for handle in handles:  # 切换窗口
            #     if handle != self.browser.current_window_handle:
            #         self.browser.switch_to_window(handle)
            #         break
            self.browser.implicitly_wait(3)
            self.browser.switch_to_window(self.browser.window_handles[-1])

            if self.driver_error(self.browser):
                num = 0
                while num < 5:
                    if "请输入验证码后继续访问" in self.browser.page_source:  # 验证码
                        num += 1
                        html_obj = etree.HTML(self.browser.page_source)
                        yzm_src = html_obj.xpath('/html/body/div/div[2]/table/tbody/tr[1]/td[3]/img/@src')[0]
                        image_data = yzm_src.split(',')[1]
                        dir_path = os.path.abspath(os.path.abspath(os.path.join(os.getcwd(), "image")))
                        self.save_image(image_data, dir_path)
                        image_path = os.path.join(dir_path, "code.jpg")
                        yzm_word = self.read_image(image_path)  # 识别验证码图片
                        os.remove(image_path)  # 删除图片
                        self.browser.find_element_by_id('intext').clear()
                        self.browser.find_element_by_id('intext').send_keys(yzm_word)  # 输入验证码
                        self.browser.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr[2]/td/input').click()
                        sleep(5)
                    # elif self.driver_error(self.browser):
                    #     self.browser.find_element_by_id('TAB_QueryConditionItem270').click()  # 签订日期
                    #     sleep(5)
                    else:
                        break
                        # return self.browser

            # 获取cookies
            target_cookie = {}
            cookies = self.browser.get_cookies()
            for cookie in cookies:
                target_cookie[cookie["name"]] = cookie["value"]

            # 获取url
            html_url = self.browser.current_url
            # 获取response
            response_result = self.browser.page_source
            self.browser.close()
            self.browser.quit()
            s = ''
            for k,v in target_cookie.items():
                s += f'{k}={v};'
            return s
            # return target_cookie
        except Exception as e:
            # self.run_request(url)
            if len(handles) > 4:
                # log_script.error('浏览器请求异常,请检查网络')
                # raise SpiderException('网络错误, 请重启')
                raise Exception('网络错误, 请重启')
            # log_script.error('响应超时')


if __name__ == '__main__':
    target_cookie = ChromeGetResponse().run_request('http://www.landchina.com/default.aspx?tabid=261')
    print(target_cookie)

