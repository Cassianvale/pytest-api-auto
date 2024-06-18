## 框架介绍

本框架主要是基于 Python + pytest + allure + log + yaml + mysql + redis + 飞书/钉钉/企微/Email通知 + Jenkins 实现的接口自动化框架

本仓库仅作二次开发库，具体使用请移步原作者仓库git地址: [https://gitee.com/yu_xiao_qi/pytest-auto-api2](https://gitee.com/yu_xiao_qi/pytest-auto-api2)

**环境配置**  

1. 配置环境Python 3.8  

2. 下载并配置jdk环境变量  
https://www.injdk.cn/?utm_source=testingpai.com  

3. 下载allure放在`C:\Program Files\allure-2.29.0`，然后配置环境变量PATH=`C:\Program Files\allure-2.29.0\bin`  
https://github.com/allure-framework/allure2/releases  

4. 先检查allure命令是否能正常运行，如果编辑器无法识别allure命令，可以使用管理员方式打开编辑器  

Allure显示乱码相关问题:  
https://blog.csdn.net/weixin_43865008/article/details/124332793  


**执行步骤**  

```
# 创建并配置python环境
python -m venv .venv
source .venv/Scripts/activate

# 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 执行run文件
python run.py
```

**实现功能**

测试数据隔离, 实现数据驱动  
支持多接口数据依赖: 如A接口需要同时依赖B、C接口的响应数据作为参数  
数据库断言: 直接在测试用例中写入查询的sql即可断言，无需编写代码  
动态多断言: 如接口需要同时校验响应数据和sql校验，支持多场景断言  
自动生成用例代码: 测试人员在yaml文件中填写好测试用例, 程序可以直接生成用例代码，纯小白也能使用  
代理录制: 支持代理录制，生成yaml格式的测试用例  
统计接口的运行时长: 拓展功能，订制开关，可以决定是否需要使用  
日志模块: 打印每个接口的日志信息，同样订制了开关，可以决定是否需要打印日志  
钉钉、企业微信通知: 支持多种通知场景，执行成功之后，可选择发送钉钉、或者企业微信、邮箱通知  
自定义拓展字段: 如用例中需要生成的随机数据，可直接调用  
多线程执行  
支持swagger接口文档转成yaml用例，节省用例编写时间  
+多个项目同时运行
+飞书测试报告同时@多人
+堆栈跟踪日志&飞书通知优化

## 目录结构


    ├── common                         // 配置
    │   ├── conf.yaml                  // 公共配置
    │   ├── setting.py                 // 环境路径存放区域
    ├── data                           // 测试用例数据
    ├── File                           // 上传文件接口所需的文件存放区域
    ├── logs                           // 日志层
    ├── report                         // 测试报告层
    ├── test_case                      // 测试用例代码
    ├── utils                          // 工具类
    │   └── assertion                
    │       └── assert_control.py      // 断言
    │       └── assert_type.py         // 断言类型
    │   └── cache_process              // 缓存处理模块
    │       └── cacheControl.py
    │       └── redisControl.py  
    │   └── logUtils                   // 日志处理模块
    │       └── logControl.py
    │       └── logDecoratrol.py       // 日志装饰器
    │       └── runTimeDecoratrol.py   // 统计用例执行时长装饰器
    │   └── mysqlUtils                 // 数据库模块
    │       └── get_sql_data.py       
    │       └── mysqlControl.py   
    │   └── noticUtils                 // 通知模块
    │       └── dingtalkControl.py     // 钉钉通知 
    │       └── feishuControl.py       // 飞书通知
    │       └── sendmailControl.py     // 邮箱通知
    │       └── weChatSendControl.py   // 企业微信通知
    │   └── otherUtils                 // 其他工具类
    │       └── allureDate             // allure封装
    │           └── allure_report_data.py // allure报告数据清洗
    │           └── allure_tools.py   // allure 方法封装
    │           └── error_case_excel.py   // 收集allure异常用例，生成excel测试报告
    │       └── localIpControl.py      // 获取本地IP
    │       └── threadControl.py       // 定时器类
    │   └── readFilesUtils             // 文件操作
    │       └── caseAutomaticControl.py // 自动生成测试代码 
    │       └── clean_case.py           // 清理所有已生成的测试用例
    │       └── new_excel_control.py    // pandas重构excel控制器(未实装到用例)
    │       └── clean_files.py          // 清理文件
    │       └── excelControl.py         // 读写excel
    │       └── get_all_files_path.py   // 获取所有文件路径
    │       └── get_yaml_data_analysis.py // yaml用例数据清洗
    │       └── regularControl.py        // 正则
    │       └── yamlControl.py          // yaml文件读写
    │   └── recordingUtils             // 代理录制
    │       └── mitmproxyContorl.py
    │   └── requestsUtils 
    │       └── dependentCase.py        // 数据依赖处理
    │       └── requestControl.py      // 请求封装
    │   └── timeUtils
    ├── Readme.md                       // help
    ├── pytest.ini                  
    ├── run.py                           // 运行入口  