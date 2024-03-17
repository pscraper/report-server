import configparser
from pathlib import Path


SQLITE = "SQLITE"
APP = "APP"

# .INI 파일 관리 클래스 정의
class IniConfig:
    FILE_NAME = "config.ini"
    INI_PATH = Path(__file__).cwd() / FILE_NAME
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        
                
    def read_value(self, section: str, key: str) -> str:
        self.config.read(self.FILE_NAME)
        return self.config[section][key]