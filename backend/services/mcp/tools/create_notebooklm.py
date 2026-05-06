import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

AUTH_FILE = Path(__file__).parent.parent.parent.parent / "auth.json"
NOTEBOOKLM_URL = "https://notebooklm.google.com"


async def run(file_path: str, title: str = "DocMind Notebook") -> str:
    if not AUTH_FILE.exists():
        raise RuntimeError("auth.json not found. Run setup_auth.py first.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(AUTH_FILE))
        page = await context.new_page()

        await page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Create new notebook
        await page.locator("button.create-new-button").click()
        await page.wait_for_timeout(3000)

        # Click upload file option
        await page.get_by_role("button", name="上傳檔案").click()
        await page.wait_for_timeout(1000)

        # Upload the file
        async with page.expect_file_chooser() as fc_info:
            await page.get_by_role("button", name="從電腦選擇檔案").click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)
        await page.wait_for_timeout(2000)

        # Confirm upload
        insert_btn = page.get_by_role("button", name="插入")
        if await insert_btn.is_visible():
            await insert_btn.click()

        # Wait for indexing (up to 3 minutes)
        await page.wait_for_timeout(5000)
        try:
            await page.wait_for_selector(
                "text=已新增 1 個來源, text=1 個來源",
                timeout=180000,
            )
        except Exception:
            pass

        await page.wait_for_timeout(3000)

        # Enable sharing
        share_btn = page.get_by_role("button", name="分享").first
        if not await share_btn.is_visible():
            share_btn = page.locator("[aria-label*='share'], [aria-label*='分享']").first
        await share_btn.click()
        await page.wait_for_timeout(1500)

        # Enable "anyone with link"
        anyone_option = page.get_by_text("知道連結的任何人")
        if await anyone_option.is_visible():
            await anyone_option.click()
            await page.wait_for_timeout(1000)

        # Copy link button
        copy_btn = page.get_by_role("button", name="複製連結")
        if await copy_btn.is_visible():
            await copy_btn.click()
            await page.wait_for_timeout(500)

        notebook_url = page.url
        await context.close()
        await browser.close()
        return notebook_url
