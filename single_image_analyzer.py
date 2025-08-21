import base64
import json
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
                "content": [{"type": "text", "text": "你是一名图片理解专家，需精准识别图片里的内容模块，接着以树状层级结构的 JSON 格式输出。要严格按照 “主要模块→子模块→子类别→元素” 这样的树状层级来组织内容，保证每个元素都能追溯到其所属的上级模块。所有层级都得有明确的命名，像模块名称、子模块名称、类别名称等，不能使用匿名结构。数组只用来存储同一层级的并列元素，比如子模块列表、元素列表。必须保证 JSON 格式完全正确，能直接解析，数组里的元素用字符串表示。另外，要忠实地反映图片原始内容的层级关系，不添加额外的解读，只进行结构化整理。"}]
            },
            {
                "role": "user",
                "content": content
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
        filename = f"{base_name}_{model_name}_{elapsed_time:.2f}s_{datetime.now().strftime('%H%M%S')}.json"

        # 保存结果
        try:
            # 处理可能的 Markdown 代码块格式
            cleaned_result = result.strip()
            if cleaned_result.startswith('```json'):
                # 移除 ```json 和 ``` 标记
                cleaned_result = cleaned_result.replace(
                    '```json', '').replace('```', '').strip()
            elif cleaned_result.startswith('```'):
                # 移除 ``` 标记
                cleaned_result = cleaned_result.replace('```', '').strip()

            # 尝试解析JSON
            json_data = json.loads(cleaned_result)

            # 保存为格式化的JSON文件
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"  完成，耗时：{elapsed_time:.2f}秒，结果已保存到：{filename}")

        except json.JSONDecodeError as e:
            # 如果JSON解析失败，尝试进一步清理
            print(f"  JSON解析失败，尝试进一步清理: {e}")
            try:
                # 移除可能的额外字符
                cleaned_result = cleaned_result.replace(
                    '\n', ' ').replace('\r', '')
                # 尝试找到JSON的开始和结束位置
                start = cleaned_result.find('{')
                end = cleaned_result.rfind('}') + 1
                if start != -1 and end != 0:
                    json_part = cleaned_result[start:end]
                    json_data = json.loads(json_part)
                    with open(filename, "w", encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    print(f"  完成，耗时：{elapsed_time:.2f}秒，结果已保存到：{filename}")
                else:
                    raise ValueError("未找到有效的JSON内容")
            except Exception as e2:
                # 如果仍然失败，保存原始内容
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"  完成，耗时：{elapsed_time:.2f}秒，结果已保存到：{filename} (原始格式)")

        except Exception as e:
            print(f"  保存失败: {e}")
    except Exception as e:
        print(f"  处理失败: {e}")

# 计算总耗时
total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time

print(f"\n所有图片处理完毕，总耗时：{total_elapsed_time:.2f}秒")
print(f"共处理了 {len(image_paths)} 张图片")
