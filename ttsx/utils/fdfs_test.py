# coding=utf-8
#python连接FastDFS服务器的驱动
from fdfs_client.client import Fdfs_client
#根据配置文件创建连接的客户端
client=Fdfs_client()
#调用方法上传文件
result=client.upload_by_file('01.jpg')
#上传成功后返回结果，结果结构如下：
'''
{'Local file name': '01.jpg', 'Storage IP': '192.168.187.132', 'Remote file_id': 'group1/M00/00/00/wKi7hFq4qTmAHIgLAAA2pLUeB60114.jpg', 'Status': 'Upload successed.', 'Group name': 'group1', 'Uploaded size': '13.00KB'}
'''
print(result)