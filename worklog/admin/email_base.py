# _*_ coding: utf-8 _*_
import abc
class email(metaclass=abc.ABCMeta):
    def __init__(self):
        self._user = "1747490424@qq.com"
        self._pwd = "oqcjloiqlsrieebf"
        self.title = None
        self.content = None
        self._to = None
    def setTitle(self, title):
        self.title = title
    def setContent(self, content):
        self.content = content
    def set_to(self, _to):
        self._to = _to
    @abc.abstractmethod
    def send_email(self):
        pass
