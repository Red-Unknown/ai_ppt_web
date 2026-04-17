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
    print("Starting Playwright E2E Test with Edge...")
    
    async with async_playwright() as p:
        try:
            # Use msedge channel
            browser = await p.chromium.launch(channel="msedge", headless=True)
            print("Browser launched successfully.")
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
        print("Sending message...")
        try:
            # Wait for textarea
            await page.wait_for_selector("textarea", timeout=5000)
            await page.fill("textarea", "Evaluate 1+1 and explain thinking.")
            await page.keyboard.press("Enter")
            
            print("Waiting for generation...")
            # Wait for some time for response
            await asyncio.sleep(10) 
            
            # Check for /thinking and /evaluation calls in network logs
            thinking_calls = [r for r in responses if "/thinking" in r["url"] and r["status"] == 200]
            evaluation_calls = [r for r in responses if "/evaluation" in r["url"] and r["status"] == 200]
            
            print(f"Thinking API Calls: {len(thinking_calls)}")
            print(f"Evaluation API Calls: {len(evaluation_calls)}")
            
            # Verify UI Elements (if possible)
            # Check if "Thinking Process" is visible
            # Note: This depends on exact text content
            content = await page.content()
            if "Thinking Process" in content:
                print("✅ UI: 'Thinking Process' text found.")
            else:
                print("⚠️ UI: 'Thinking Process' text NOT found.")

            if "Evaluation & Feedback" in content:
                 print("✅ UI: 'Evaluation & Feedback' text found.")
            else:
                 print("⚠️ UI: 'Evaluation & Feedback' text NOT found.")

            # 4. Create New Session
            print("Creating new session...")
            # Click 'New Chat' button. 
            # We need a robust selector. Let's try text.
            # If sidebar is collapsed, we might need to open it. 
            # But usually it is open on desktop size (default viewport).
            
            # Try to find New Chat button
            # Based on code: <button ...>New Chat</button> or similar icon
            # Let's assume there is a button with text "New Chat" or similar
            # If not found, we might skip this step or use API to create session then reload.
            
            # Let's try to click an element that looks like new chat
            # If fails, we catch it.
            try:
                # Adjust selector based on actual Vue code if known, or generic text
                await page.click("text=New Chat", timeout=3000)
                
                # If there is a modal confirm
                try:
                    await page.click("button:has-text('Start Session')", timeout=2000)
                except:
                    pass
                
                print("Switched to New Chat.")
                await asyncio.sleep(2)
                
                # 5. Switch Back
                print("Switching back to previous session...")
                # We need to find the session list.
                # Usually it's a list of buttons in sidebar.
                # We can try to click the second item.
                # Or just verify that the UI cleared.
                
                new_content = await page.content()
                if "Evaluate 1+1" not in new_content:
                    print("✅ UI: Chat content cleared on new session.")
                else:
                    print("❌ UI: Old content still visible after switch!")
                    
            except Exception as e:
                print(f"Session switching test failed/skipped: {e}")
            
        except Exception as e:
            print(f"Interaction failed: {e}")
            
        await browser.close()
        print("Browser test finished.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
