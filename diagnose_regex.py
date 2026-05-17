# diagnose_regex.py
# 深入调试正则边界问题
import re

text = '华为是中国领先的科技公司，腾讯和阿里巴巴也在布局AI。'

print("=" * 60)
print("正则边界调试")
print("=" * 60)

# 打印文本的每个字符及其 Unicode 编码
print("\n[步骤1] 文本字符分析")
print(f"文本长度: {len(text)}")
for i, char in enumerate(text[:20]):
    is_chinese = '\u4e00' <= char <= '\u9fff'
    print(f"  位置 {i}: '{char}' (U+{ord(char):04X}) {'中文' if is_chinese else '其他'}")

# 逐个测试不同的正则模式
print("\n[步骤2] 不同正则模式测试")

patterns = [
    ("简单匹配", r'华为'),
    ("英文边界", r'\b华为\b'),
    ("中文边界v1", r'(?<![a-zA-Z0-9\u4e00-\u9fff])(华为)(?![a-zA-Z0-9\u4e00-\u9fff])'),
    ("中文边界v2", r'(?<![a-zA-Z0-9\u4e00-\u9fff一-龥])(华为)(?![a-zA-Z0-9\u4e00-\u9fff一-龥])'),
    ("宽松边界", r'(?<!\w)(华为)(?!\w)'),
    ("无边界", r'华为'),
    ("前后空格检测", r' 华为 '),  # 文本开头有空格
]

for name, pattern_str in patterns:
    pattern = re.compile(pattern_str)
    matches = pattern.findall(text)
    print(f"  {name}: {pattern_str!r} -> {matches}")

# 测试边界检测本身
print("\n[步骤3] 边界检测详细分析")
for i in range(min(5, len(text))):
    char = text[i]
    next_char = text[i+1] if i+1 < len(text) else ''
    
    # 检查前面是否是边界字符
    before_boundary = not (char.isalnum() or '\u4e00' <= char <= '\u9fff')
    after_boundary = i+1 < len(text) and not (text[i+1].isalnum() or '\u4e00' <= text[i+1] <= '\u9fff') if i+1 < len(text) else True
    
    print(f"  位置 {i}: '{char}' 前面是边界={before_boundary}, 后面是边界={after_boundary}")

# 直接用 lookahead/lookbehind 测试
print("\n[步骤4] Lookahead/Lookbehind 单独测试")
pattern = re.compile(r'(?<!\w)华为(?!\w)')
print(f"  (?<!\w)华为(?!\w): {pattern.findall(text)}")

pattern = re.compile(r'\b华为\b')
print(f"  \\b华为\\b: {pattern.findall(text)}")

# 关键发现：空格在中文前后的行为
print("\n[步骤5] 关键测试 - 空格的影响")
text_with_space = ' 华为 '
text_no_space = '华为'
print(f"  带空格: '{text_with_space}', 无空格: '{text_no_space}'")

pattern = re.compile(r'(?<!\w)(华为)(?!\w)')
print(f"  带空格匹配: {pattern.findall(text_with_space)}")
print(f"  无空格匹配: {pattern.findall(text_no_space)}")

pattern2 = re.compile(r'(?<![a-zA-Z0-9\u4e00-\u9fff])(华为)(?![a-zA-Z0-9\u4e00-\u9fff])')
print(f"  中文边界-带空格: {pattern2.findall(text_with_space)}")
print(f"  中文边界-无空格: {pattern2.findall(text_no_space)}")

print("\n" + "=" * 60)
