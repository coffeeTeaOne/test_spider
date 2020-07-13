# import re
#
#
# # s = """联系电话：
# #
# # 湖州市自然资源和规划局湖州南太湖新区分局          褚女士    0572-2218610
# #
# # 湖州市自然资源和规划局
# #
# # 2020年06月17日"""
#
#
# s = """
# 八、联系方式：
#
# 1.湖州市土地储备中心                谢先生0572-2697712
#
# 南浔开发区自然资源所              沈先生0572-3707582
#
# 南浔镇自然资源所                  冯先生0572-3910977
#
# 2.浙江省土地使用权网上交易系统：http://www.zjgtjy.cn"""
#
# temp = re.findall(r'联系[电|方][话|式]：[\s|\S]*?([\s|\S]*?[女|先][士|生])',s)
# other_temp = re.findall(r'\d[\s|\S]*?([\s|\S]*?[女|先][士|生])',s)
# other_temp = [i.split('\n\n')[1] if '\n\n' in i else i for i in other_temp]
# print(other_temp)
# a = temp[0].split(' ')[0] if temp else ''
# b = temp[0][-3:] if temp else ''
# c = re.findall(r'[\d|-]+',s)[0]
#
# print(temp)
# print(other_temp)
# print(a)
# print(b)
# print(c)
from retrying import retry


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
def n():
    print(1)
    return int('a')

try:
    a = int('')
except:
    try:
        n()
    except:
        print('aaaa')