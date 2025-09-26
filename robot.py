import requests
import json


class Robot:
    def __init__(self):
        self.url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8d36956a-8984-4c1c-8fc4-2acbf8b00e35"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def send_text(self, content):

        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_mobile_list": [],
                "mentioned_user_list": [],
            },
        }

        return self._send_request(data)

    def _send_request(self, data):
        """发送请求到企业微信机器人"""
        try:
            response = requests.post(
                self.url, headers=self.headers, data=json.dumps(data), timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get("errcode") == 0:
                print("✅ 消息发送成功")
                return True
            else:
                print(f"❌ 消息发送失败: {result}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 发送消息时出现错误: {e}")
            return False
