# 通义千问模型API调用示例

这个脚本演示了如何使用阿里云通义千问的多模态模型进行图像理解和文本生成。

## 环境配置

1. 在项目根目录创建 `.env` 文件
2. 在 `.env` 文件中添加你的API密钥：
   ```
   DASHSCOPE_API_KEY=你的API密钥
   ```

## 支持的模型

项目支持以下通义千问模型：

- `qwen2.5-vl-3b-instruct` - 3B参数视觉语言模型
- `qwen2.5-vl-7b-instruct` - 7B参数视觉语言模型  
- `qwen2.5-vl-32b-instruct` - 32B参数视觉语言模型
- `qwen2.5-vl-72b-instruct` - 72B参数视觉语言模型
- `qwen-vl-plus` - 通义千问视觉语言增强版
- `qwen-plus` - 通义千问增强版
- `qwen-vl-max` - 通义千问视觉语言最大版
- `qwen2-vl-7b-instruct` - 通义千问2.0 7B视觉语言模型



## 功能说明

- 支持图像识别和文字提取
- 自动进行Base64编码
- 支持PNG、JPEG、WEBP格式图片

