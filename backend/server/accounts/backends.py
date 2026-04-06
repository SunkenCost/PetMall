from django.core.mail.backends.smtp import EmailBackend
import smtplib
import ssl

class Python312EmailBackend(EmailBackend):
    """
    专门解决 Python 3.12 环境下 Django 4.1 发送邮件报错的问题。
    手动建立连接以屏蔽掉 'keyfile' 和 'certfile' 参数。
    """
    def open(self):
        if self.connection:
            return False
        
        try:
            # 1. 准备连接类
            connection_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
            
            # 2. 初始化连接，不传递 Django 内部持有的 keyfile 和 certfile (Python 3.12 禁用了它们)
            self.connection = connection_class(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            
            # 3. 如果是 STARTTLS (非SSL端口但开启了加密)
            if not self.use_ssl and self.use_tls:
                self.connection.ehlo()
                self.connection.starttls() # 同样不传递参数
                self.connection.ehlo()
            
            # 4. 登录
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
        except:
            if not self.fail_silently:
                raise
            return False
