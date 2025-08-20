import base64
import os
import pdb
import time
from datetime import datetime
from dotenv import load_dotenv
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

load_dotenv()
# 初始化一个Client对象，从环境变量中获取API Key
client = Ark(
    api_key=os.getenv('ARK_API_KEY'),
)

# 定义方法将指定路径图片转为Base64编码


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 需要传给大模型的图片
image_path = "./assets/intro.jpeg"

# 将图片转为Base64编码
base64_image = encode_image(image_path)
model_name = "doubao-1-5-thinking-vision-pro-250428"
# 记录开始时间
start_time = time.time()
response = client.chat.completions.create(
    # 替换 <MODEL> 为模型的Model ID
    model=model_name,
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "你是一名图片理解助手，擅长识别文字图片的主要内容并进行模块化层级输出。需先判断图片模块内容（如包含图表、文字板块等），再提取各模块下的关键信息，按 “核心元素类别” 为一级，关键信息为二级的层级形式输出。无需对原始内容过度解读，只需要按层级输出原始内容即可。"}]
        },
        {
            "role": "user",
            "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            # 需要注意：传入Base64编码前需要增加前缀 data:image/{图片格式};base64,{Base64编码}：
                            # PNG图片："url":  f"data:image/png;base64,{base64_image}"
                            # JPEG图片："url":  f"data:image/jpeg;base64,{base64_image}"
                            # WEBP图片："url":  f"data:image/webp;base64,{base64_image}"
                            "url":  f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                {
                        "type": "text",
                        "text": "描述这张图片",
                    },
            ],
        }
    ],
)

# 计算耗时
end_time = time.time()
elapsed_time = end_time - start_time

# 生成包含模型名称和时间的文件名
filename = f"{model_name}_{elapsed_time:.2f}s_{datetime.now().strftime('%H%M%S')}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content)

print(f"理解完毕，耗时：{elapsed_time:.2f}秒")
print(f"结果已保存到：{filename}")
