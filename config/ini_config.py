import configparser
from pathlib import Path


SQLITE = "SQLITE"
APP = "APP"

# .INI 파일 관리 클래스 정의
class Config:
    FILE_NAME = "config.ini"
    INI_PATH = Path(__file__).cwd() / FILE_NAME
    
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        
        # config.ini 파일이 없는 경우 디폴트 값으로 자동 생성
        if not self.INI_PATH.exists():
            # 섹션 생성 
            self.config[SQLITE] = dict()
            self.config[APP] = dict()
            
            # 섹션 아래 값 생성
            self.config[APP]["app"] = "main:app"
            self.config[APP]["host"] = "127.0.0.1"
            self.config[APP]["port"] = "8000"
            self.config[APP]["workers"] = "2"
            self.config[APP]["name"] = "pscraper-api-server"
            self.config[SQLITE]["db_conn_url"] = "sqlite:///./api-server.db"
            
            with open(self.INI_PATH, mode="w") as f:
                self.config.write(f)
                
                
    def read_value(self, section: str, key: str) -> str:
        self.config.read(self.FILE_NAME)
        return self.config[section][key]