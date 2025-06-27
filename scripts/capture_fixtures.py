#!/usr/bin/env python3
"""
Script to capture real HTML snapshots from Twitter profiles for testing
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def capture_profile_html(username: str, output_path: Path):
    """Capture HTML from a Twitter profile"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        
        try:
            print(f"Capturing HTML for @{username}...")
            await page.goto(f"https://x.com/{username}", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # Wait for tweets to load
            await page.wait_for_selector("article", timeout=15000)
            
            # Get the HTML content
            html_content = await page.content()
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Saved HTML to {output_path}")
            
        except Exception as e:
            print(f"❌ Error capturing @{username}: {e}")
        finally:
            await browser.close()


async def main():
    """Capture HTML for multiple profiles"""
    # Create fixtures directory
    fixtures_dir = Path("tests/fixtures/twitter")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    # Profiles to capture
    profiles = [
        "nasa",           # Well-known account, likely to have recent tweets
        "GobCDMX",        # One of our target accounts
        "MetroCDMX",      # Another target account
        "elonmusk",       # High-activity account for testing
    ]
    
    print("🚀 Starting HTML capture for test fixtures...")
    
    for username in profiles:
        output_path = fixtures_dir / f"{username}_profile.html"
        await capture_profile_html(username, output_path)
        await asyncio.sleep(2)  # Be nice to Twitter
    
    print("✅ HTML capture complete!")
    print(f"📁 Fixtures saved in: {fixtures_dir}")


if __name__ == "__main__":
    asyncio.run(main()) 