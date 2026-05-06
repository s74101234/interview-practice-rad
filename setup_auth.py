"""
Run this script once to save Google session for NotebookLM automation.
A browser window will open — log in to your Google account, then close it.
The session is saved to auth.json and reused automatically.
"""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://accounts.google.com")
        print("請在瀏覽器中登入 Google 帳號，完成後關閉瀏覽器視窗...")

        try:
            await page.wait_for_url("https://myaccount.google.com/**", timeout=120000)
        except Exception:
            pass

        await context.storage_state(path="auth.json")
        await browser.close()
        print("auth.json 已儲存，後續自動化將直接使用此 session。")


if __name__ == "__main__":
    asyncio.run(main())
