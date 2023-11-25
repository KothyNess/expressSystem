# 快递管理系统
- 南京信息工程大学 软件工程作业

## 本系统使用的框架

1. 本系统使用Django框架进行搭建
2. 数据库使用Mysql8.0
3. 前端使用H5+Js+CSS并加入DJango的前端模版语法

## 如何使用
1. clon 此项目至你的本地文件。
2. 使用pycharm打开此项目
3. 使用含有Django库及musqlclient库的python解释器进行运行此项目
4. 数据库部分
   1. 首先在项目的settings.py文件中设置你的数据库信息
   ```
   DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'express',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
   }
   ```
   3. 然后执行一下步骤
   ```
   //先在项目文件夹内使用终端运行这两条命令将数据库创建好
   python manage.py makemigrations
   python manage.py migrate
   ```
   ```
   //此项目的运行指令
   python manage.py runserver
   //或直接使用Pyharm Professional版本进行直接运行
   ```
   
