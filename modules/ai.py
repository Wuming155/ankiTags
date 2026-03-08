import requests
import re
import html

class AIClient:
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base
    
    def clean_html(self, text):
        """清理HTML标签和转义字符"""
        # 清理HTML标签
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # 处理转义字符
        text = html.unescape(text)
        # 压缩空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def generate_tags(self, text, model, prompt):
        """使用AI生成标签"""
        if not self.api_key:
            return ["错误: 请输入API Key"]
        
        try:
            response = requests.post(
                self.api_base,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"为以下Anki卡片内容生成标签：\n{text}"}
                    ],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                tags = response.json()["choices"][0]["message"]["content"].strip()
                # 清洗标签
                cleaned_tags = []
                for tag in tags.split(","):
                    tag = tag.strip()
                    # 过滤空标签
                    if not tag:
                        continue
                    # 过滤无效标签
                    if tag == "生成失败" or tag.startswith("错误"):
                        continue
                    # 移除Anki不支持的特殊字符
                    tag = re.sub(r'[\s,/\\]', '_', tag)
                    cleaned_tags.append(tag)
                return cleaned_tags if cleaned_tags else ["未生成有效标签"]
            else:
                return [f"错误: 状态码 {response.status_code}"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def get_models(self):
        """获取可用的模型列表"""
        if not self.api_key:
            return []
        
        try:
            import urllib.parse
            # 解析URL
            parsed_url = urllib.parse.urlparse(self.api_base)
            # 构建基础路径（移除路径部分）
            base_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, "/v1", '', '', ''))
            # 确保路径以/结尾
            if not base_url.endswith("/"):
                base_url += "/"
            # 构建模型列表URL
            model_url = f"{base_url}models"
            response = requests.get(
                model_url,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return [model["id"] for model in data["data"]]
            else:
                return []
        except Exception as e:
            return []