import requests
import hashlib
import hmac
import uuid
import csv
class Get_CubeAndUid(object):
    def __init__(self,serverip):
        self.__url = serverip
        self.appVersion = '1.2.459'  # 客户端app版本号
        self.osName = 'windows'  # 系统版本号

    def PC_login(self, userName, pwd):
        pwd = self.md5_encryption(pwd)  # md5加密
        api = '/s10/auth/login'  # api
        data = {'userName': userName, 'pwd': pwd, 'appVersion': self.appVersion, 'osName': self.osName}  # 请求参数
        re = self.login_func(api, data)
        return re

    def login_func(self, api, data):
        data = self.add_sign_uuid(data)

        re = self.post_requtest(api, data)  # 发送请求
        re_data = re.json()
        # 获取ticket并给ticket重新赋值
        self.ticket = re_data.get('data').get('ticket')
        # 获取token并给token重新赋值
        self.token = re_data.get('data').get('tokenInfo').get('token')
        assert re.status_code == 200, '接口%s请求失败' % api  # 断言请求状态
        return re

    def post_requtest(self, api, json_data):
        response = requests.post(self.__url + api, json_data)
        return response

    def add_sign_uuid(self,data,ticket=''):
        data['uuid'] = self.create_uuid()  # 添加uuid
        if ticket:
            data['sign'] = self.create_signData(data, ticket)  # 添加sign
        else:
            data['sign'] = self.create_signData(data)  # 添加sign
        return data

    def md5_encryption(self, value):
        src = value.encode()
        m2 = hashlib.md5()
        m2.update(src)
        md5_value = m2.hexdigest()
        return md5_value

    def create_uuid(self):
        uid = uuid.uuid4()
        c_uuid = str(uid)
        return c_uuid

    def joint_string(self,dict_data):
        '''
        将字典型数据按照'='和‘&’进行拼接
        :param dict_data:字典型数据
        :return:按照'='和‘&’进行拼接后的数据
        '''
        AZ = sorted(dict_data)#字典序排序
        newdata = []
        for i in AZ:
            for j in dict_data.keys():
                if i == j:
                    newdata.append((i, str(dict_data.get(i))))
        d = []
        for i in newdata:
            c = '='.join(i)
            d.append(c)
        joint_data = '&'.join(d)
        return joint_data


    def create_signData(self,vadict_datalue,ticket = 'spap_2018_go'):
        '''
        输入字典型的数据后返回处理后的sign数据
        :param vadict_datalue:字典型数据
        :return:处理后的sign数据
        '''
        re = self.joint_string(vadict_datalue)
        sign = self.sha256_encrption(ticket,re)
        return sign

    def sha256_encrption(self, key,msg):
        '''
        生成sha256sign
        :param key:ticket值
        :param msg:需要加密的参数
        :return:加密后生成的sign值
        '''
        secret = bytes(key, encoding='utf-8')
        message = bytes(msg, encoding='utf-8')
        sign = hmac.new(secret, message, digestmod=hashlib.sha256).digest()
        HEX = sign.hex()
        lowsign = HEX.lower()
        return lowsign

    def get_cube(self,userName,pwd):
        re = self.PC_login(userName, pwd)
        cube = re.json().get("data").get("user").get("cube")
        return cube

    def get_uid(self,userName,pwd):
        re = self.PC_login(userName, pwd)
        uid = re.json().get("data").get("user").get("uid")
        return uid


if __name__ == '__main__':
    login = Get_CubeAndUid("http://test-restful-spap.shixincube.cn")
    csv_file = csv.reader(open("F:/work/testMessage/userParams2.csv","r"))
    out = open("F:/work/testMessage/usercubss2.csv", 'a', newline='')
    csv_write = csv.writer(out, dialect='excel')
    for stu in csv_file:
        c = login.get_cube(stu[0], stu[1])
        cubs_pwd = [c, stu[1]]
        csv_write.writerow(cubs_pwd)


