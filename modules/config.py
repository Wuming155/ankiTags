import configparser
import os

class ConfigManager:
    def __init__(self):
        # 配置文件路径 - 基于主程序入口文件定位
        import sys
        # 获取主程序所在目录
        if hasattr(sys, 'frozen'):
            # 打包成exe的情况
            base_dir = os.path.dirname(sys.executable)
        else:
            # 正常运行的情况
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.api_config_file = os.path.join(base_dir, "api_config.ini")
        self.prompt_config_file = os.path.join(base_dir, "prompt_config.ini")
        
        # 初始化配置
        self.api_config = configparser.ConfigParser()
        self.prompt_config = configparser.ConfigParser()
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 加载API配置
        if os.path.exists(self.api_config_file):
            self.api_config.read(self.api_config_file, encoding="utf-8")
        
        # 确保API部分存在
        if "API" not in self.api_config:
            self.api_config["API"] = {
                "api_key": "",
                "api_base": "https://api.siliconflow.cn/v1/chat/completions",
                "model": "deepseek-ai/DeepSeek-V3",
                "models": ""
            }
        
        # 加载Prompt配置
        if os.path.exists(self.prompt_config_file):
            self.prompt_config.read(self.prompt_config_file, encoding="utf-8")
        
        # 确保Prompt部分存在
        if "Prompt" not in self.prompt_config:
            self.prompt_config["Prompt"] = {
                "default": "你是一个Anki卡片标签生成器，为给定的卡片内容生成5-8个相关的标签，标签之间用逗号分隔，不要有其他解释",
                "prompts": "标签生成器|你是一个Anki卡片标签生成器，为给定的卡片内容生成5-8个相关的标签，标签之间用逗号分隔，不要有其他解释;学习分类|根据卡片内容，生成3-5个学习分类标签，帮助组织学习内容;主题标签|为卡片内容生成主题相关的标签，每个标签不超过4个字"
            }
        
        # 保存配置
        self.save_api_config()
        self.save_prompt_config()
    
    def save_api_config(self):
        """保存API配置文件"""
        with open(self.api_config_file, "w", encoding="utf-8") as f:
            self.api_config.write(f)
    
    def save_prompt_config(self):
        """保存Prompt配置文件"""
        with open(self.prompt_config_file, "w", encoding="utf-8") as f:
            self.prompt_config.write(f)
    
    def get_api_key(self):
        return self.api_config["API"].get("api_key", "")
    
    def set_api_key(self, api_key):
        self.api_config["API"]["api_key"] = api_key
        self.save_api_config()
    
    def get_api_base(self):
        return self.api_config["API"].get("api_base", "https://api.siliconflow.cn/v1/chat/completions")
    
    def set_api_base(self, api_base):
        self.api_config["API"]["api_base"] = api_base
        self.save_api_config()
    
    def get_model(self):
        return self.api_config["API"].get("model", "deepseek-ai/DeepSeek-V3")
    
    def set_model(self, model):
        self.api_config["API"]["model"] = model
        self.save_api_config()
    
    def get_models(self):
        models_str = self.api_config["API"].get("models", "")
        return models_str.split(",") if models_str else []
    
    def set_models(self, models):
        self.api_config["API"]["models"] = ",".join(models)
        self.save_api_config()
    
    def get_default_prompt(self):
        return self.prompt_config["Prompt"].get("default", "你是一个Anki卡片标签生成器，为给定的卡片内容生成5-8个相关的标签，标签之间用逗号分隔，不要有其他解释")
    
    def set_default_prompt(self, prompt):
        self.prompt_config["Prompt"]["default"] = prompt
        self.save_prompt_config()
    
    def get_prompts(self):
        """获取所有保存的prompt，返回字典{名称: 内容}"""
        prompts_str = self.prompt_config["Prompt"].get("prompts", "")
        prompts = {}
        if prompts_str:
            for item in prompts_str.split(";"):
                if "|" in item:
                    name, content = item.split("|", 1)
                    prompts[name.strip()] = content.strip()
        return prompts
    
    def add_prompt(self, name, content):
        """添加一个新的prompt"""
        prompts = self.get_prompts()
        prompts[name] = content
        
        # 转换回字符串格式
        prompts_str = ";".join([f"{name}|{content}" for name, content in prompts.items()])
        self.prompt_config["Prompt"]["prompts"] = prompts_str
        self.save_prompt_config()
    
    def remove_prompt(self, name):
        """删除一个prompt"""
        prompts = self.get_prompts()
        if name in prompts:
            del prompts[name]
            
            # 转换回字符串格式
            prompts_str = ";".join([f"{name}|{content}" for name, content in prompts.items()])
            self.prompt_config["Prompt"]["prompts"] = prompts_str
            self.save_prompt_config()
    
    def update_prompt(self, name, content):
        """更新一个prompt"""
        self.add_prompt(name, content)