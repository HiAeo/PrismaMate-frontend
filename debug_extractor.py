# debug_extractor.py
import sys
sys.path.insert(0, r'D:\PrismaMate专用文件夹\prismamate-backend')

from app.services.brand_extractor import BrandExtractor
import re

print("=" * 60)
print("Debug Extractor")
print("=" * 60)

text = '华为是中国领先的科技公司，腾讯和阿里巴巴也在布局AI。'
print(f"Text: {text}")
print(f"Text repr: {repr(text)}")

extractor = BrandExtractor()

# 找到阿里巴巴的模式
for name, pattern in extractor._compiled_patterns:
    if '阿里' in name:
        print(f"\nPattern for {name}: {pattern.pattern}")
        matches = pattern.findall(text)
        print(f"Matches: {matches}")
        
        # 用 finditer 看详细信息
        for m in pattern.finditer(text):
            print(f"  finditer: '{m.group()}' at {m.span()}")

# 直接测试
print("\n[Direct test]")
ali_pattern = re.compile(r'(?<![a-zA-Z0-9\u4e00-\u9fff])(阿里巴巴)(?![a-zA-Z0-9])')
print(f"Pattern: {ali_pattern.pattern}")
print(f"Matches in text: {ali_pattern.findall(text)}")

# 检查文本中的字符
print("\n[Char analysis around 阿里巴巴]")
for i, c in enumerate(text):
    if i >= 12 and i <= 20:
        print(f"  {i}: '{c}' (U+{ord(c):04X})")
