import os
import glob
import re
import asyncio
import aiofiles
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="", base_url="https://api.deepseek.com")

translate_prompt = """把下面的技术文档内容翻译地道、流畅自然的中文，文档中提到的人名和技术或其他常见名词不进行翻译，必须符合中文表达习惯，必须使用和原文排版一致的markdown格式输出。"""


def is_chinese(text):
    sample = text[:100]
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', sample)
    # 是否存在中文字符
    ratio = len(chinese_chars)
    return ratio > 1

async def translate_text(text):
    prompt = translate_prompt + f"```{text}```"
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=True
    )

    translated = ""
    reasoning_content = ""
    async for chunk in response:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            translated += delta.content
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            reasoning_content += delta.reasoning_content
            #print(f"🔍 推理内容: {reasoning_content}")
    return translated


async def extract_translatable_blocks(md_text: str):
    lines = md_text.splitlines()
    translated_segments = []
    raw_with_placeholders = []

    block_map = {}
    block_id = 0

    in_code_block = False
    code_block_buffer = []

    for line in lines:
        # 判断代码块开头或结尾（```）
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_buffer = [line]
            else:
                code_block_buffer.append(line)
                code_key = f"[[[CODE_BLOCK_{block_id}]]]"
                block_map[code_key] = "\n".join(code_block_buffer)
                raw_with_placeholders.append(code_key)
                block_id += 1
                in_code_block = False
            continue

        if in_code_block:
            code_block_buffer.append(line)
            continue

        if re.match(r'^\s*$', line):
            raw_with_placeholders.append("[[[EMPTY_LINE]]]")
            continue

        if re.match(r'^\[.*?\]\(.*?\)', line):  # 链接整行不翻译
            raw_with_placeholders.append(line)
            continue

        # 标题、列表、普通段落统一为占位符处理
        raw_with_placeholders.append(f"[[[TRANS_BLOCK_{len(translated_segments)}]]]")
        translated_segments.append(line)

    # 组合为一个大文本
    joined_text = "\n".join(translated_segments)
    translated_text = await translate_text(joined_text)

    # 分行回填
    translated_lines = translated_text.splitlines()
    block_map.update({
        f"[[[TRANS_BLOCK_{i}]]]": translated_lines[i] if i < len(translated_lines) else ""
        for i in range(len(translated_segments))
    })
    block_map["[[[EMPTY_LINE]]]"] = ""

    # 最终还原
    restored_lines = [
        block_map.get(line, line)
        for line in raw_with_placeholders
    ]
    return "\n".join(restored_lines)



async def process_file(file_path, semaphore):
    async with semaphore:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()

        if is_chinese(content):
            return  # 跳过中文文件

        print(f"🔄 正在翻译: {file_path}")
        try:
            translated = await extract_translatable_blocks(content)
            # 处理翻译结果
            if translated.strip().startswith("```") and translated.strip().endswith("```"):
                markdown = re.sub(r'^```[a-z]*\n?', '', translated.strip())
                markdown = re.sub(r'\n?```$', '', markdown)
            else:
                markdown = translated
                        # 保存翻译内容（覆盖原文件）
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(markdown)

            print(f"✅ 翻译完成并保存: {file_path}")
        except Exception as e:
            print(f"❌ 处理失败: {file_path}，错误: {e}")
            return

        # 删除源文件（已经覆盖，此处可略）
        # os.remove(file_path)  # 如不想覆盖原文件可改为新文件名后保留旧文件

def find_md_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return glob.glob(os.path.join(current_dir, '**', '*.mdx'), recursive=True)

async def main():
    md_files = find_md_files()
    semaphore = asyncio.Semaphore(8)  # 限制最多8个并发任务
    tasks = [process_file(fp, semaphore) for fp in md_files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
