import sys
try:
    from playwright.sync_api import sync_playwright
    print('Playwright 导入成功', flush=True)
    with sync_playwright() as p:
        print('启动浏览器...', flush=True)
        browser = p.chromium.launch(headless=True)
        print('浏览器已启动', flush=True)
        page = browser.new_page()
        print('打开 DeepSeek...', flush=True)
        page.goto('https://chat.deepseek.com', timeout=30000)
        page.wait_for_timeout(5000)
        print('=== 页面标题 ===')
        print(page.title(), flush=True)
        print('=== textarea 数量 ===')
        print(page.locator('textarea').count(), flush=True)
        print('=== input 元素 ===')
        inputs = page.locator('input')
        print(f'共 {inputs.count()} 个', flush=True)
        for i in range(min(inputs.count(), 5)):
            t = inputs.nth(i).get_attribute('type')
            p = inputs.nth(i).get_attribute('placeholder')
            print(f'  input[{i}]: type={t}, placeholder={p}', flush=True)
        print('=== role=textbox 元素 ===')
        textboxes = page.locator('[role="textbox"]')
        print(f'共 {textboxes.count()} 个', flush=True)
        for i in range(min(textboxes.count(), 3)):
            tag = textboxes.nth(i).evaluate('el => el.tagName')
            cls = textboxes.nth(i).get_attribute('class')
            print(f'  textbox[{i}]: tag={tag}, class={cls}', flush=True)
        print('=== 页面可见文本前300字符 ===')
        text = page.locator('body').inner_text()
        print(text[:300], flush=True)
        browser.close()
        print('完成', flush=True)
except Exception as e:
    print(f'错误: {e}', flush=True)
    import traceback
    traceback.print_exc()
