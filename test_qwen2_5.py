import base64
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 记录开始时间
start_time = time.time()

#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 将xxxx/eagle.png替换为你本地图像的绝对路径
base64_image = encode_image("./assets/intro.jpeg")
# base64_image = encode_image("./assets/text.jpg")

# 选择要使用的模型
'''model="qwen2.5-vl-3b-instruct",
    # model="qwen2.5-vl-7b-instruct",
    # model="qwen2.5-vl-32b-instruct",
    # model="qwen2.5-vl-72b-instruct",
    # model="qwen-vl-plus",
    # model="qwen-plus",
    # model="qwen2-vl-7b-instruct'''
model_name = "qwen-vl-max"  # 可以修改为其他模型

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
    # model="qwen2.5-vl-3b-instruct",
    # model="qwen2.5-vl-7b-instruct",
    # model="qwen2.5-vl-32b-instruct",
    # model="qwen2.5-vl-72b-instruct",
    # model="qwen-vl-plus",
    # model="qwen-plus",
    model=model_name,
    # model="qwen2-vl-7b-instruct",

    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "请准确输出这张图片里的所有原始文字与数字内容及对层级信息进行解析"}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    # 需要注意，传入Base64，图像格式（即image/{format}）需要与支持的图片列表中的Content Type保持一致。"f"是字符串格式化的方法。
                    # PNG图像：  f"data:image/png;base64,{base64_image}"
                    # JPEG图像： f"data:image/jpeg;base64,{base64_image}"
                    # WEBP图像： f"data:image/webp;base64,{base64_image}"
                    # "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                # {"type": "text", "text": "请准确识别这张图片里的所有原始文字与数字内容及图片中层级关系进行解析"},qwen2.5-vl
                {"type": "text", "text": "描述张张图片中的所有信息"},
                
            ],
        }
    ],
)

# 计算耗时
end_time = time.time()
elapsed_time = end_time - start_time

# 生成包含模型名称和时间的文件名
filename = f"{model_name}_{elapsed_time:.2f}s.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(completion.choices[0].message.content)

print(f"理解完毕，耗时：{elapsed_time:.2f}秒")
print(f"结果已保存到：{filename}")
print("理解完毕")
