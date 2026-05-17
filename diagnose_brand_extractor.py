# diagnose_brand_extractor.py
# 最小验证脚本
import sys
sys.path.insert(0, r'D:\PrismaMate专用文件夹\prismamate-backend')

from app.services.brand_extractor import BrandExtractor

print("=" * 60)
print("Brand Extractor Verification")
print("=" * 60)

extractor = BrandExtractor()
text = '华为是中国领先的科技公司，腾讯和阿里巴巴也在布局AI。'
result = extractor.extract(text)
print(f"Text: {text}")
print(f"Result: {len(result)} mentions")

if result:
    for m in result:
        print(f"  Brand: {m.brand_name}")
        print(f"  Position: {m.position_start}-{m.position_end}")
        print(f"  Context: {m.context}")
else:
    print("  [FAIL] No mentions extracted!")

print("\n" + "=" * 60)
