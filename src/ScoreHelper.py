# -*- coding: utf-8 -*-
# @author: mdmbct
# @data:   2019/9/3 11:28
# @last modified by: 
# @last modified time: 2019/9/3 14:49

import re
import urllib.request
import urllib.parse
import http.cookiejar
import pandas as pd
import sys
import platform
import subprocess
from bs4 import BeautifulSoup
from PIL import Image
import configparser
import os
import glob
import csv


class Course(object):

    def __init__(self, year, term, code, name,
                 nature, attribution, credit, point, score, minor_flag,
                 make_up_score, restudy_score, belong, remarks, restudy_flag):
        """
        :param year: 学年
        :param term: 学期
        :param code: 课程代码
        :param name: 课程名
        :param nature: 课程性质
        :param attribution: 课程归属
        :param credit: 学分
        :param point: 绩点
        :param score: 成绩
        :param minor_flag: 辅修标记
        :param make_up_score: 补考成绩
        :param restudy_score: 重修成绩
        :param belong: 开课学院
        :param remarks: 备注
        :param restudy_flag: 重修标记
        """
        self.year = year
        self.term = term
        self.code = str(code)
        self.name = name
        self.nature = nature
        self.attribution = attribution
        self.credit = eval(credit)
        self.point = point
        if score == "良好":
            self.score = 80
        elif score == "优秀":
            self.score = 90
        elif score == "及格":
            self.score = 60
        elif score == "中等":
            self.score = 70
        else:
            self.score = eval(score)
        self.minor_flag = False if (minor_flag == 0 or minor_flag is None) else True
        self.make_up_score = make_up_score
        self.restudy_score = restudy_score
        self.belong = belong
        self.remarks = remarks
        self.restudy_flag = restudy_flag


class BasicScoreCalculator(object):
    # 必修课百分比
    R_C_PERC = 0.7
    # 选修课百分比
    E_C_PERC = 0.3
    # 所有课程百分比
    A_C_PERC = 0.9

    def __init__(self, courses):
        """
        :param courses: 所有课的列表
        """
        self.courses = courses

    def get_total_credits(self):
        """
        总学分
        """
        total_credits = 0
        for course in self.courses:
            total_credits += course.credit
        return total_credits

    def get_elective_courses_credits(self):
        """
        选修课总学分
        """
        elective_courses_credits = 0
        for course in self.courses:
            if "选修课" in course.nature:
                elective_courses_credits += course.credit
        return elective_courses_credits

    def get_required_courses_credits(self):
        """
        必修课总学分
        """
        required_courses_credits = 0
        for course in self.courses:
            if "必修课" in course.nature:
                required_courses_credits += course.credit
        return required_courses_credits

    def cal_basic_score(self):
        """
        基本分
        计算方法：（必修课总成绩 / 总学分 * 0.7 + 选修课总成绩 / 总学分 * 0.3）* 0.9
        其中：必修课总成绩 = (成绩 * 学分)之和， 选修课总成绩 = (成绩 * 学分)之和
        """
        # 必修课总成绩
        r_c_total_scores = 0
        # 必修课总学分
        r_c_total_credits = 0
        # 选修课总成绩
        e_c_total_scores = 0
        # 选修课总学分
        e_c_total_credits = 0
        for course in self.courses:
            # 必修课
            if "必修课" in course.nature:
                r_c_total_scores += (course.score * course.credit)
                r_c_total_credits += course.credit
            else:
                e_c_total_scores += (course.score * course.credit)
                e_c_total_credits += course.credit
            print(course.name, end="\t")
            print(course.credit, end="\t\t")
            print(course.score)

        print("必修课总成绩：" + str(r_c_total_scores))
        print("选修课总成绩：" + str(e_c_total_scores))
        print("必修课总学分：" + str(r_c_total_credits))
        print("选修课总学分：" + str(e_c_total_credits))
        total_credits = r_c_total_credits + e_c_total_credits
        print("总学分：" + str(total_credits))
        print("计算方法1：（必修课总成绩 / 必修总学分 * 0.7 + 选修课总成绩 / 选修总学分 * 0.3）* 0.9")
        basic_scores = (
                               r_c_total_scores / r_c_total_credits * self.R_C_PERC + e_c_total_scores / e_c_total_credits * self.E_C_PERC) * self.A_C_PERC
        print("计算方法2：（必修课总成绩 / 总学分 * 0.7 + 选修课总成绩 / 总学分 * 0.3）* 0.9")
        basic_scores2 = (
                                r_c_total_scores / total_credits * self.R_C_PERC + e_c_total_scores / total_credits * self.E_C_PERC) * self.A_C_PERC
        print("基本分2：" + str(basic_scores2))
        return basic_scores


# 准备Cookie和opener，因为cookie存于opener中，所以以下所有网页操作全部要基于同一个opener
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))


# 判断操作系统类型
def get_system_type():
    return platform.system()


# 判断是否联网
def is_net_useable():
    user_os = get_system_type()
    if user_os == "Windows":
        subprocess.check_call(["ping", "-n", "2", "www.baidu.com"], stdout=subprocess.PIPE)
    else:
        subprocess.check_call(["ping", "-c", "2", "www.baidu.com"], stdout=subprocess.PIPE)


# 登陆
def login():
    # 构造表单
    params = {
        'txtUserName': sid,
        'Textbox1': '',
        'Textbox2': pwd,
        'RadioButtonList1': '学生',
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': '',
    }
    # 获取验证码
    res = opener.open(VERIFICATION_CODE_URL).read()
    with open(r'data/code.jpg', 'wb') as file:
        file.write(res)
    img = Image.open(r'data/code.jpg')
    img.show()
    code = input("请输入验证码(看不清直接回车)：")
    if code == "":
        print("看不清验证码...")
        return False
    img.close()
    params['txtSecretCode'] = code
    # 获取ViewState
    response = urllib.request.urlopen(ROOT_URL)
    html = response.read().decode('gb2312')
    view_state = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"', html)
    params['__VIEWSTATE'] = view_state.group(1)
    # 尝试登陆
    data = urllib.parse.urlencode(params).encode('gb2312')
    response = opener.open(LOGIN_URL, data)
    if response.geturl() == ROOT_URL:
        print('登陆失败，可能是姓名、学号、密码、验证码填写错误！')
        return False
    else:
        return True


# 获取成绩
def get_score_info():
    # 构造url
    url = ''.join([
        SCORE_PAGE_URL,
        '?xh=',
        sid,
        '&xm=',
        urllib.parse.quote(stu_name),
        '&gnmkdm=N121604',
    ])

    # 构建查询全部成绩表单 '\" + study_year + \"'

    params = {
        'ddlXN': study_year,
        'hidLanguage': "",
        'ddlXQ': "",
        "ddl_kcxz": "",
        "btn_xn": "学年成绩",
    }
    # 构造Request对象，填入Header，防止302跳转，获取新的View_State
    req = urllib.request.Request(url)
    req.add_header('Referer', LOGIN_URL)
    req.add_header('Origin', ROOT_URL)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36')
    response = opener.open(req)
    html = response.read().decode('gb2312')
    view_state = re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)"', html)
    params['__VIEWSTATE'] = view_state.group(1)
    # 查询所有成绩
    req = urllib.request.Request(url, urllib.parse.urlencode(params).encode('gb2312'))
    req.add_header('Referer', LOGIN_URL)
    req.add_header('Origin', ROOT_URL)
    response = opener.open(req)
    soup = BeautifulSoup(response.read().decode('gb2312'), 'html.parser')
    try:
        html = soup.find('table', class_='datelist')
        df = pd.read_html(str(html), header=0)[0]
        result = list(df.T.to_dict().values())  # 转换成列表嵌套字典的格式
    except Exception as e:
        # traceback.print_exc()
        print(e)
        print("查询失败...")
        sys.exit(0)
    print(result)
    if len(result) > 0:
        csv_target = os.path.join("data", stu_name + "_" + study_year + "_" + "scores.csv")
        df.to_csv(csv_target, index=False)
        print("成绩单保存到 " + csv_target + " ...")
        # return csv_target
        return result


if __name__ == '__main__':

    cf = configparser.ConfigParser()
    cf.read("data/config.conf", encoding="utf-8")
    ROOT_URL = cf.get("eas url", "root_url")
    LOGIN_URL = cf.get("eas url", "login_url")
    VERIFICATION_CODE_URL = cf.get("eas url", "verification_code_url")
    SCORE_PAGE_URL = cf.get("eas url", "score_page_url")
    study_year = cf.get("scores", "year")
    stu_name = cf.get("account", "name")
    files = glob.glob("data/*.csv")
    scores_saved = []
    for file in files:
        scores_saved.append(file.split("\\")[1].split("_s")[0])
    print(scores_saved)
    if (stu_name + "_" + study_year) not in scores_saved:
        print('检查网络...')
        is_net_useable()
        # if not os.path.exists("data"):
        #     os.mkdir(r'data')
        sid = cf.get("account", "id")
        pwd = cf.get("account", "password")
        while not login():
            print("登录失败，重试...")
            continue
        print("登录成功...")
        scores = []
        for score in get_score_info():
            # print(score)
            values = list(score.values())
            scores.append(Course(values[0], values[1], values[2], values[3], values[4],
                                 values[5], str(values[6]), values[7], values[8], values[9],
                                 values[10], values[11], values[12], values[13], values[14]))
    else:
        print("从已经存在的文件中计算基本分")
        file_name = "data/" + stu_name + "_" + study_year + "_scores.csv"
        scores = []
        with open(file_name, encoding="utf-8") as csv_file:
            data = csv.reader(csv_file)
            for index, rows in enumerate(data):
                if index != 0:
                    # print(rows[4], end="\t")
                    # print(rows[8])
                    scores.append(
                        Course(rows[0], rows[1], rows[2], rows[3], rows[4],
                               rows[5], rows[6], rows[7], rows[8], rows[9],
                               rows[10], rows[11], rows[12], rows[13], rows[14])
                    )
    bsc = BasicScoreCalculator(scores)
    print("基本分：" + str(bsc.cal_basic_score()))
