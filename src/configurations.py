class Config(object):
	DEBUG = False
	TESTING = False

class ProductionConfig(Config):
	HOST = "MartinChan.mysql.pythonanywhere-services.com"
	USER = "MartinChan"
	PASSWORD = "Aweki2235zxc"
	DATABASE = "MartinChan$cookbook"

class DevelopmentConfig(Config):
	DEBUG = True
	HOST = "localhost"
	USER = "root"
	PASSWORD = "Aweki2235zxc"
	DATABASE = "cookbook"

class TestConfig(Config):
	TESTING = True
	HOST = "localhost"
	USER = "root"
	PASSWORD = "Aweki2235zxc"
	DATABASE = "testcookbook"

