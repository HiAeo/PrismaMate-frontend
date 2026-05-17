# test_pattern.py
# 精确测试正则模式
import re

print("=" * 60)
print("Test regex patterns")
print("=" * 60)

# 最简单测试：文本就是"华为"
text1 = '华为'
text2 = 'Hello华为World'
text3 = '华为公司'  # 华为后面是中文字符

patterns = [
    ("no boundary", r'华为'),
    ("left boundary only", r'(?<![a-zA-Z0-9])华为'),
    ("right boundary only", r'华为(?![a-zA-Z0-9])'),
    ("both boundaries", r'(?<![a-zA-Z0-9])华为(?![a-zA-Z0-9])'),
]

for name, p in patterns:
    pat = re.compile(p)
    r1 = pat.findall(text1)
    r2 = pat.findall(text2)
    r3 = pat.findall(text3)
    print(f"  {name}:")
    print(f"    '{text1}' -> {r1}")
    print(f"    '{text2}' -> {r2}")
    print(f"    '{text3}' -> {r3}")

# 关键测试：中文边界
print("\n[Key] Chinese-specific boundary test")
# 期望：'华为' 应该匹配（文本开头，中文边界）
# 期望：'华为公司' 应该匹配（'华为'后是中文字符'公'，也是边界）
text4 = '华为'
text5 = '华为公司'
text6 = '的公司华为好'  # 华为前面是中文字符

chinese_boundaries = r'(?<![a-zA-Z0-9\u4e00-\u9fff])华为(?![a-zA-Z0-9\u4e00-\u9fff])'
pat = re.compile(chinese_boundaries)

print(f"  Pattern: {chinese_boundaries!r}")
print(f"    '{text4}' -> {pat.findall(text4)}")
print(f"    '{text5}' -> {pat.findall(text5)}")
print(f"    '{text6}' -> {pat.findall(text6)}")

print("\n" + "=" * 60)
