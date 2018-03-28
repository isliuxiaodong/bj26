# coding=utf-8
#这是django中提供的文件存储类的基类
from django.core.files.storage import Storage
from django.conf import settings

# python连接FastDFS服务器的驱动
from fdfs_client.client import Fdfs_client


#自定义存储类，将内容存储到fastdfs
class FdfsStorage(Storage):
    def save(self, name, content, max_length=None):
        #content=requset.FILES.get('')表示文件对象
        #从网络流中读取文件数据
        buffer=content.read()

        # 根据配置文件创建连接的客户端
        client = Fdfs_client(settings.FDFS_CLIENT)
        # 调用方法上传文件，上传本地文件
        # result = client.upload_by_file('01.jpg')
        #上传文件数据，因为这个文件的内容是从浏览器上传过来的，本地不存在这个文件
        try:
            result=client.upload_by_buffer(buffer)
        except:
            raise
        # 上传成功后返回结果，结果结构如下：
        '''
        {'Local file name': '01.jpg', 'Storage IP': '192.168.187.132', 'Remote file_id': 'group1/M00/00/00/wKi7hFq4qTmAHIgLAAA2pLUeB60114.jpg', 'Status': 'Upload successed.', 'Group name': 'group1', 'Uploaded size': '13.00KB'}
        '''
        if result.get('Status')=='Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('上传文件失败')

    #参数name表示文件的名称
    #当ImageField类型的对象image，调用属性url时，会调用对应的存储类的url()方法
    def url(self, name):
        return settings.FDFS_SERVER+name
