import json
from playwright.sync_api import Page


def get_page_state(page: Page) -> str:
    # Strip mat-icon text from each button so agent sees only semantic label
    buttons = []
    for btn in page.get_by_role("button").all():
        try:
            icon_texts = set()
            for icon in btn.locator("mat-icon").all():
                try:
                    ic = (icon.text_content(timeout=200) or "").strip()
                    if ic:
                        icon_texts.add(ic)
                except Exception:
                    pass
            raw = btn.inner_text(timeout=300)
            cleaned = raw
            for ic in icon_texts:
                cleaned = cleaned.replace(ic, "")
            cleaned = " ".join(cleaned.split()).strip()
            if cleaned:
                buttons.append(cleaned)
        except Exception:
            pass
    buttons = buttons[:15]

    headings = [h.strip() for h in page.get_by_role("heading").all_text_contents() if h.strip()][:8]
    body     = page.inner_text("body")[:500]

    # input 欄位值（分享連結會出現在此）
    n_inputs = page.locator("input[type='text']").count()
    inputs   = [
        v for v in [
            page.locator("input[type='text']").nth(i).get_attribute("value") or ""
            for i in range(min(3, n_inputs))
        ] if v
    ]

    # mat-select 目前選中的值（Angular Material 下拉）
    selects = []
    for el in page.locator("mat-select").all():
        try:
            val = el.locator(".mat-mdc-select-min-line").text_content(timeout=1000) or ""
            fc  = el.get_attribute("formcontrolname") or ""
            if val.strip():
                selects.append({"formcontrolname": fc, "value": val.strip()})
        except Exception:
            pass

    # mat-option 開啟中的下拉選項（overlay 層，generalAccess 展開後才出現）
    options = []
    for el in page.locator("mat-option").all():
        try:
            t = " ".join(el.inner_text(timeout=300).split()).strip()
            if t:
                options.append(t)
        except Exception:
            pass

    return json.dumps({
        "url":      page.url,
        "buttons":  buttons,
        "headings": headings,
        "inputs":   inputs,
        "selects":  selects,
        "options":  options,
        "text":     body,
    }, ensure_ascii=False)


def click(page: Page, text: str) -> str:
    try:
        # Try accessible role match first (ignores aria-hidden icon text)
        btn = page.get_by_role("button").filter(has_text=text).first
        if btn.count() > 0 and btn.is_visible(timeout=3000):
            btn.click()
            page.wait_for_timeout(1000)
            return f"已點擊：{text}"
        # Fallback: any visible element containing the text
        page.get_by_text(text).first.click(timeout=5000)
        page.wait_for_timeout(1000)
        return f"已點擊：{text}"
    except Exception as e:
        return f"點擊失敗：{e}"


def force_click(page: Page, text: str) -> str:
    """強制點擊，繞過 overlay/backdrop 遮擋。"""
    try:
        btn = page.get_by_role("button").filter(has_text=text).first
        el  = btn if btn.count() > 0 else page.get_by_text(text).first
        el.click(force=True, timeout=5000)
        page.wait_for_timeout(1000)
        return f"已強制點擊：{text}"
    except Exception as e:
        return f"強制點擊失敗：{e}"


def upload_file(page: Page, file_path: str) -> str:
    """攔截 file chooser 後點擊上傳按鈕，OS 視窗不會出現。
    若 agent 事先已點擊「上傳檔案」導致 OS 視窗開啟，先用 SendKeys 關閉再繼續。
    """
    try:
        _dismiss_os_dialog()
        page.wait_for_timeout(300)

        with page.expect_file_chooser(timeout=10000) as fc_info:
            page.get_by_role("button").filter(has_text="上傳檔案").click()
        fc_info.value.set_files(file_path)
        page.wait_for_timeout(2000)

        insert_btn = page.get_by_role("button", name="插入")
        if insert_btn.is_visible(timeout=3000):
            insert_btn.click()
            page.wait_for_timeout(1000)

        return f"已上傳：{file_path}"
    except Exception as e:
        return f"上傳失敗：{e}"


def _dismiss_os_dialog() -> None:
    """關閉開啟中的 Windows 通用對話框（file picker）。
    以 #32770 window class 精準定位，不影響瀏覽器視窗。
    """
    import ctypes
    hwnd = ctypes.windll.user32.FindWindowW("#32770", None)
    if hwnd:
        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE


def click_by_css(page: Page, selector: str) -> str:
    """用 CSS selector 點擊。不帶 force，確保 Angular CDK 事件正常觸發。"""
    try:
        el = page.locator(selector).first
        el.click(timeout=5000)
        page.wait_for_timeout(1000)
        return f"已點擊：{selector}"
    except Exception as e:
        return f"CSS 點擊失敗：{e}"


def get_clipboard(page: Page) -> str:
    # 方法一：JS clipboard API
    try:
        url = page.evaluate("navigator.clipboard.readText()")
        if url and url.startswith("http"):
            return url
    except Exception:
        pass
    # 方法二：頁面上的 input[type='text'] 含 notebooklm URL
    try:
        for i in range(page.locator("input[type='text']").count()):
            val = page.locator("input[type='text']").nth(i).get_attribute("value") or ""
            if "notebooklm" in val:
                return val
    except Exception:
        pass
    return "無法取得剪貼簿，請確認已點擊複製連結"


def press_key(page: Page, key: str) -> str:
    try:
        page.keyboard.press(key)
        page.wait_for_timeout(500)
        return f"已按下：{key}"
    except Exception as e:
        return f"按鍵失敗：{e}"


def execute(page: Page, action: str, args: dict, file_path: str) -> str:
    if action == "click":
        return click(page, args.get("text", ""))
    if action == "upload_file":
        return upload_file(page, file_path)
    if action == "click_by_css":
        return click_by_css(page, args.get("selector", ""))
    if action == "force_click":
        return force_click(page, args.get("text", ""))
    if action == "press_key":
        return press_key(page, args.get("key", "Escape"))
    if action == "get_clipboard":
        return get_clipboard(page)
    if action == "wait":
        secs = min(int(args.get("seconds", 5)), 30)
        page.wait_for_timeout(secs * 1000)
        return f"已等待 {secs} 秒"
    return f"未知動作：{action}"
