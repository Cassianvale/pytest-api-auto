import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from common.setting import ensure_path_sep
from utils import config
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.other_tools.models import TestMetrics


class SendEmail:
    """ 发送邮箱 """

    def __init__(self, case_count: TestMetrics):
        self.case_count = case_count
        self.allure_data = AllureFileClean()
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    @classmethod
    def send_mail(cls, user_list: list, sub, content: str, attachment_path=None) -> None:
        """
        @param user_list: 收件人邮箱列表
        @param sub: 邮件主题
        @param content: 邮件内容
        @param attachment_path: 附件路径
        @return:
        """
        # 名称只能为ascii编码
        user = "ChangQiu" + "<" + config.email.send_user + ">"

        # 创建邮件对象
        message = MIMEMultipart()
        message['Subject'] = Header(sub).encode()
        message['From'] = Header(user).encode()
        message['To'] = Header(";".join(user_list)).encode()

        # 邮件正文
        message.attach(MIMEText(content, _subtype='plain', _charset='utf-8'))

        # 添加附件
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                mime = MIMEBase('application', 'octet-stream', filename=os.path.basename(attachment_path))
                mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                mime.add_header('Content-ID', '<0>')
                mime.add_header('X-Attachment-Id', '0')
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                message.attach(mime)

        server = smtplib.SMTP()
        server.connect(config.email.email_host)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str, attachment_path=None) -> None:
        """
        执行异常邮件通知
        @param error_message: 报错信息
        @param attachment_path: 附件路径
        @return:
        """
        email = config.email.send_list
        user_list = email.split(',')

        sub = config.project_name + "接口自动化执行异常通知"
        content = f"接口自动化测试用例执行完毕，程序中发现异常，请悉知！报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content, attachment_path)

    def send_main(self, attachment_path=None) -> None:
        """
        发送邮件
        @param attachment_path: 附件路径
        @return:
        """
        email = config.email.send_list
        user_list = email.split(',')

        sub = config.project_name + "接口自动化报告"
        content = f"""
        您的接口自动化测试用例执行完成，执行结果如下:
            用例运行总数: {self.case_count.total} 个
            通过用例数: {self.case_count.passed} 个
            失败用例数: {self.case_count.failed} 个
            异常用例数: {self.case_count.broken} 个
            跳过用例数: {self.case_count.skipped} 个
            成  功  率: {self.case_count.pass_rate} %
            allure报告测试时长: {self.case_count.allure_time} 秒
            pytest测试会话时长: {self.case_count.pytest_time} 秒
        {self.allure_data.get_failed_cases_detail()}

        **********************************
        jenkins地址：https://121.xx.xx.47:8989/login
        详细情况可登录jenkins平台查看，非相关负责人员可忽略此消息。谢谢。
        """
        self.send_mail(user_list, sub, content, attachment_path)


if __name__ == '__main__':
    excel_path = ensure_path_sep("\\Files\\test_data\\自动化异常测试用例.xlsx")
    case_count_dict = AllureFileClean().get_case_count()
    case_count = TestMetrics(**case_count_dict)
    SendEmail(case_count).send_main(attachment_path=excel_path)


