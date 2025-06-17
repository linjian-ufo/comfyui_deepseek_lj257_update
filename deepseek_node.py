import os
import json
import requests
from pathlib import Path

class DeepSeekChatNode:
    """
    ComfyUI节点，用于调用DeepSeek Chat API处理文本输入并返回文本输出
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
            },
            "optional": {
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "test_mode": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "process_text"
    CATEGORY = "DeepSeek"
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
        self.load_config()
    
    def load_config(self):
        """加载配置文件，获取API密钥"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.api_key = config.get("api_key", "")
            except Exception as e:
                print(f"Error loading config: {e}")
                self.api_key = ""
        else:
            # 创建默认配置文件
            default_config = {"api_key": "your_deepseek_api_key_here"}
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            self.api_key = ""
            print(f"Created default config file at {self.config_path}. Please edit it to add your DeepSeek API key.")
    
    def process_text(self, text, temperature=0.7, max_tokens=1024, system_prompt="You are a helpful assistant.", test_mode=False):
        """处理输入文本并通过DeepSeek API获取响应"""
        # 测试模式，不实际调用API
        if test_mode:
            return (f"[测试模式] 输入文本: '{text[:30]}...' 已接收。在实际模式下，将使用以下参数调用DeepSeek API:\n"
                   f"- 温度: {temperature}\n"
                   f"- 最大tokens: {max_tokens}\n"
                   f"- 系统提示词: '{system_prompt}'\n"
                   f"测试模式不会消耗API额度，适合用于验证节点连接和参数设置。",)
        
        # 检查API密钥
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            return ("错误: 请在配置文件中设置有效的DeepSeek API密钥。\n"
                   "配置文件路径: " + self.config_path + "\n"
                   "或者启用测试模式来验证节点功能而不调用API。",)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # 添加超时设置
            )
            
            if response.status_code == 200:
                result = response.json()
                return (result["choices"][0]["message"]["content"],)
            elif response.status_code == 402:
                # 处理余额不足错误
                error_message = "错误: DeepSeek API账户余额不足。\n\n"
                error_message += "请检查以下可能的原因:\n"
                error_message += "1. 您的DeepSeek账户余额已用完\n"
                error_message += "2. 您的API密钥可能未绑定付款方式\n"
                error_message += "3. 您的账户可能有未结清的账单\n\n"
                error_message += "解决方法:\n"
                error_message += "1. 登录DeepSeek官网检查账户余额\n"
                error_message += "2. 充值您的DeepSeek账户\n"
                error_message += "3. 确认您的付款方式设置正确\n"
                error_message += "4. 暂时可以启用测试模式来验证节点功能\n\n"
                error_message += "原始错误: " + response.text
                print(error_message)
                return (error_message,)
            else:
                # 处理其他API错误
                error_code = response.status_code
                error_text = response.text
                
                error_message = f"错误: DeepSeek API请求失败 (状态码: {error_code})\n\n"
                
                # 根据常见错误代码提供更具体的提示
                if error_code == 401:
                    error_message += "API密钥无效或已过期。请检查您的API密钥是否正确。\n\n"
                elif error_code == 429:
                    error_message += "请求频率超限。请减少API调用频率或等待一段时间再试。\n\n"
                elif error_code >= 500:
                    error_message += "DeepSeek服务器错误。请稍后再试。\n\n"
                
                error_message += "原始错误: " + error_text
                print(error_message)
                return (error_message,)
                
        except requests.exceptions.Timeout:
            error_message = "错误: 连接DeepSeek API超时。请检查您的网络连接或稍后再试。"
            print(error_message)
            return (error_message,)
        except requests.exceptions.ConnectionError:
            error_message = "错误: 无法连接到DeepSeek API。请检查您的网络连接。"
            print(error_message)
            return (error_message,)
        except Exception as e:
            error_message = f"错误: 处理文本时出现未知问题: {str(e)}\n"
            error_message += "请尝试启用测试模式来验证节点功能。"
            print(error_message)
            return (error_message,)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "DeepSeekChatNode": DeepSeekChatNode
}

# 设置显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "DeepSeekChatNode": "DeepSeek Chat"
}
