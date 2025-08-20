import base64
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_files(folder_path='./assets'):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]


def get_image_url(image_path):
    """根据图片格式生成对应的data URL"""
    base64_image = encode_image(image_path)

    if image_path.lower().endswith('.png'):
        return f"data:image/png;base64,{base64_image}"
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        return f"data:image/jpeg;base64,{base64_image}"
    elif image_path.lower().endswith('.webp'):
        return f"data:image/webp;base64,{base64_image}"
    else:
        raise ValueError(f"不支持的图片格式: {image_path}")


def analyze_single_image(image_path, model_name, client):
    """分析单张图片"""
    # 获取图片URL
    image_url = get_image_url(image_path)

    # 构建消息内容
    content = [
        {
            "type": "image_url",
            "image_url": {"url": image_url}
        },
        {
            "type": "text",
            "text": "描述这张图片"
        }
    ]

    # 调用API
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一名图片理解助手，擅长识别文字图片的主要内容并进行模块化层级输出。需先判断图片模块内容（如包含图表、文字板块等），再提取各模块下的关键信息，按 “核心元素类别” 为一级，关键信息为二级的层级形式输出。无需对原始内容过度解读，只需要按层级输出原始内容即可。"}]
            },
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    return completion.choices[0].message.content


# 获取所有图片
image_paths = get_image_files()

# 模型类型
# model_name = "qwen-vl-max"
model_name = "qwen2.5-vl-3b-instruct"

# 创建客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 记录总开始时间
total_start_time = time.time()

# 为每张图片单独调用API
for i, image_path in enumerate(image_paths, 1):
    print(f"正在处理第 {i}/{len(image_paths)} 张图片: {os.path.basename(image_path)}")

    # 记录单张图片开始时间
    start_time = time.time()

    try:
        # 分析单张图片
        result = analyze_single_image(image_path, model_name, client)

        # 计算单张图片耗时
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 生成包含图片名称、模型名称和时间的文件名
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        filename = f"{base_name}_{model_name}_{elapsed_time:.2f}s_{datetime.now().strftime('%H%M%S')}.txt"

        # 保存结果
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        print(f"  完成，耗时：{elapsed_time:.2f}秒，结果已保存到：{filename}")

    except Exception as e:
        print(f"  处理失败: {e}")

# 计算总耗时
total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time

print(f"\n所有图片处理完毕，总耗时：{total_elapsed_time:.2f}秒")
print(f"共处理了 {len(image_paths)} 张图片")
