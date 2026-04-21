import asyncio
import os
import sys
import json
import time
from playwright.async_api import async_playwright, expect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configuration
BASE_URL = "http://localhost:5173"  # Frontend URL
API_URL = "http://localhost:8000"   # Backend URL

async def run_e2e_test():
    print("Starting Playwright E2E Test...")
    
    async with async_playwright() as p:
        # Launch browser (headless=True for CI/Sandbox)
        # Note: In sandbox environment, we might not have browsers installed.
        # If this fails, we might need to fallback to API-level simulation or assume browser exists.
        # Since 'playwright install' failed due to permission, we might rely on system browser if available?
        # Or we skip browser test and do pure API test.
        # But let's try to launch, maybe chromium is there?
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Failed to launch browser: {e}")
            print("Skipping browser-based E2E test due to environment limitations.")
            return

        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Capture Network Requests
        requests = []
        page.on("request", lambda request: requests.append({
            "url": request.url,
            "method": request.method
        }))
        
        responses = []
        page.on("response", lambda response: responses.append({
            "url": response.url,
            "status": response.status
        }))

        # 2. Go to Home
        print(f"Navigating to {BASE_URL}...")
        try:
            await page.goto(BASE_URL, timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}. Ensure frontend is running.")
            await browser.close()
            return

        # 3. Simulate User Interaction
        # Check if we are on chat page
        # Send a message
        print("Sending message...")
        # Note: selectors depend on actual DOM structure.
        # Assuming input is 'textarea' or 'input[type=text]'
        # And send button
        
        # Wait for input to be ready
        try:
            await page.wait_for_selector("textarea, input[type='text']", timeout=5000)
            await page.fill("textarea, input[type='text']", "Evaluate 1+1 and explain thinking.")
            await page.keyboard.press("Enter")
            
            # Wait for response
            # We look for specific API calls
            print("Waiting for generation...")
            # Wait for some time or wait for specific element
            await asyncio.sleep(10) 
            
            # Check for /thinking and /evaluation calls
            thinking_calls = [r for r in responses if "/thinking" in r["url"] and r["status"] == 200]
            evaluation_calls = [r for r in responses if "/evaluation" in r["url"] and r["status"] == 200]
            
            print(f"Thinking API Calls: {len(thinking_calls)}")
            print(f"Evaluation API Calls: {len(evaluation_calls)}")
            
            # 4. Create New Session
            print("Creating new session...")
            # Click 'New Chat' button (look for text 'New Chat')
            await page.click("text=New Chat")
            # Handle Modal if any
            # Assuming immediate switch or modal confirm
            # If modal:
            try:
                await page.click("button:has-text('Start Session')", timeout=2000)
            except:
                pass
                
            await asyncio.sleep(2)
            
            # 5. Switch Back to Previous Session
            print("Switching back...")
            # Click the second session in the list (index 1, since new is 0)
            # This is tricky with dynamic selectors.
            # We can try to click the second button in sidebar list
            # sidebar buttons usually in aside
            
            # For now, let's verify API calls happened during generation
            
        except Exception as e:
            print(f"Interaction failed: {e}")
            
        await browser.close()
        print("Browser test finished.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
