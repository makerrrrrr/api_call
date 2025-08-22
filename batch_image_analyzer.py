import base64
import os
import pdb
import time
from datetime import datetime

import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_files(folder_path='./assets'):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]


# 获取所有图片
image_paths = get_image_files()

# 编码所有的图片
base64_images = []
for image_path in image_paths:
    base64_image = encode_image(image_path)
    if image_path.lower().endswith('.png'):
        image_url = f"data:image/png;base64,{base64_image}"
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        image_url = f"data:image/jpeg;base64,{base64_image}"
    elif image_path.lower().endswith('.webp'):
        image_url = f"data:image/webp;base64,{base64_image}"
    base64_images.append(image_url)

# 构建包含多张图片的消息
image_contents = []
for image_url in base64_images:
    image_contents.append({
        "type": "image_url",
        "image_url": {"url": image_url}
    })

# 模型类型
# model_name = "qwen-vl-max"
model_name = "qwen2.5-vl-3b-instruct"

# 添加文本提示
image_contents.append({"type": "text", "text": "请分别描述每张图片的内容，用图片1、图片2、图片3等标识"})

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
start_time = time.time()
completion = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "你是一名图片理解助手，擅长理解图片后将图片信息进行模块化输出。你需先判断图片所包含的模块内容（如包含图表、文字板块等），再提取各模块下的关键信息，按 “核心元素类别” 为一级，关键信息为二级的层级形式输出。无需对原始内容过度解读，只需要按层级输出原始内容即可"}]
        },
        {
            "role": "user",
            "content": image_contents,
        }
    ],
)
# 计算耗时
end_time = time.time()
elapsed_time = end_time - start_time

# 生成包含模型名称和时间的文件名
filename = f"{model_name}_{elapsed_time:.2f}s_{datetime.now().strftime('%H%M%S')}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(completion.choices[0].message.content)
print(f"理解完毕，耗时：{elapsed_time:.2f}秒")
print(f"结果已保存到：{filename}")
