import { test, expect } from '@playwright/test';

test.describe('Multi-Session Concurrency & Stability Test', () => {
  // 模拟后端数据存储
  const sessions = new Map(); // sessionId -> { history: [], streaming: bool }
  
  test.beforeEach(async ({ page }) => {
    // 1. Mock REST APIs
    
    // Mock Sessions List (Initial Empty)
    await page.route('/api/v1/chat/sessions', async route => {
      const sessionList = Array.from(sessions.values()).map(s => ({
        id: s.id,
        title: s.title,
        mode: s.mode,
        updated_at: new Date().toISOString()
      }));
      await route.fulfill({ json: sessionList });
    });

    // Mock Start Session
    await page.route('/api/v1/chat/session/start', async route => {
      const body = JSON.parse(route.request().postData());
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
      sessions.set(sessionId, {
        id: sessionId,
        title: body.course_id || 'New Session',
        mode: body.mode || 'learning',
        history: [],
        streaming: false
      });
      await route.fulfill({ json: { session_id: sessionId } });
    });

    // Mock Get History
    await page.route(/\/api\/v1\/chat\/history\/session_.*/, async route => {
      const sessionId = route.request().url().split('/').pop();
      // Handle /context endpoint
      if (sessionId === 'context') { 
          // Extract actual session id from previous part if url is .../history/{id}/context
          // But regex above matches .../history/session_...
          // Let's rely on standard parsing
          return route.fulfill({ json: {} });
      }
      
      const session = sessions.get(sessionId);
      if (session) {
        await route.fulfill({ json: session.history });
      } else {
        await route.fulfill({ json: [] });
      }
    });

    // Mock Other Context APIs
    await page.route('**/context', async route => route.fulfill({ json: {} }));
    await page.route('**/thinking', async route => route.fulfill({ json: {} }));
    await page.route('**/evaluation', async route => route.fulfill({ json: {} }));

    // 2. Mock WebSocket
    await page.routeWebSocket('**/api/v1/chat/ws', ws => {
      ws.onMessage(async message => {
        const data = JSON.parse(message);
        const sessionId = data.session_id;
        const query = data.query;
        
        if (!sessionId) return;

        // Update Mock DB
        const session = sessions.get(sessionId);
        if (session) {
          session.history.push({ role: 'user', content: query });
          const assistantMsg = { 
              role: 'assistant', 
              content: '', 
              status_updates: [],
              react_steps: []
          };
          session.history.push(assistantMsg);
          session.streaming = true;

          // Simulate Streaming
          const responseText = `Response to "${query}" for ${sessionId}. `;
          const tokens = responseText.split('');
          const totalTokens = 50; // Extend length
          
          // Simulate Token Streaming
          let tokenCount = 0;
          const streamInterval = setInterval(() => {
              if (tokenCount >= totalTokens) {
                  clearInterval(streamInterval);
                  session.streaming = false;
                  // Check if socket is still open? 
                  // Playwright might throw if we try to send to closed socket.
                  try {
                    ws.send(JSON.stringify({
                        type: 'end',
                        session_id: sessionId
                    }));
                  } catch (e) {
                    // ignore
                  }
                  return;
              }

              const chunk = tokens[tokenCount % tokens.length] || '.';
              assistantMsg.content += chunk; // Update backend state
              
              try {
                ws.send(JSON.stringify({
                    type: 'token',
                    session_id: sessionId,
                    content: chunk
                }));
              } catch (e) {
                clearInterval(streamInterval);
              }
              
              tokenCount++;
          }, 50); // Fast stream for test
        }
      });
    });
  });

  test('should handle multi-session switching and concurrent streaming', async ({ page }) => {
    test.setTimeout(60000); // Allow longer time for multiple sessions

    // 1. Initialize
    await page.goto('/');
    await expect(page.locator('text=Welcome to AI Tutor')).toBeVisible();

    // 2. Create Session 1
    await page.getByRole('button', { name: 'New Chat' }).click();
    await page.getByRole('button', { name: 'Start Session' }).click();
    await expect(page.locator('h2')).toContainText('Learning Session');
    
    // Send Message 1
    const q1 = 'Explain Quantum Physics';
    await page.fill('textarea', q1);
    await page.getByRole('button', { name: 'Send message' }).click();
    
    // Verify Session 1 starts streaming
    await expect(page.locator('.bg-white', { hasText: 'Response to' })).toBeVisible();
    await page.screenshot({ path: 'test-results/screenshots/step1_session1_streaming.png' });

    // 3. Create Session 2 (while Session 1 is streaming)
    await page.getByRole('button', { name: 'New Chat' }).click();
    await page.getByRole('button', { name: 'Start Session' }).click();
    // Wait for switch
    await page.waitForTimeout(500); 
    
    // Send Message 2
    const q2 = 'Explain Relativity';
    await page.fill('textarea', q2);
    await page.getByRole('button', { name: 'Send message' }).click();

    // Verify Session 2 starts streaming
    await expect(page.locator('.bg-white', { hasText: 'Response to' }).last()).toBeVisible();
    await page.screenshot({ path: 'test-results/screenshots/step2_session2_streaming.png' });

    // 4. Fast Switching Loop
    const sessionItems = page.locator('aside button.w-full');
    const count = await sessionItems.count();
    expect(count).toBeGreaterThanOrEqual(2);

    for (let i = 0; i < 6; i++) {
        const targetIndex = i % 2; // Toggle between 0 and 1
        const targetSessionBtn = sessionItems.nth(targetIndex);
        
        // Measure Switch Time
        const startSwitch = Date.now();
        await targetSessionBtn.click();
        
        // Verify loading or content appears
        // The loader might appear briefly
        // We check if the header title updates or message list is visible
        await expect(page.locator('main')).toBeVisible();
        
        const switchTime = Date.now() - startSwitch;
        console.log(`Switch ${i+1} time: ${switchTime}ms`);
        expect(switchTime).toBeLessThan(1000); // 宽松一点，CI环境可能慢

        // Verify content matches session
        const expectedQuery = targetIndex === 0 ? q2 : q1; // Session list order: Newest first (Unshift) -> Index 0 is Session 2
        await expect(page.locator('.bg-blue-600', { hasText: expectedQuery })).toBeVisible();
        
        // Verify streaming content exists (partial match)
        await expect(page.locator('.bg-white', { hasText: 'Response to' })).toBeVisible();
        
        if (i === 0) await page.screenshot({ path: 'test-results/screenshots/step3_switch_1.png' });
        
        await page.waitForTimeout(200); // Wait a bit before next switch
    }

    // 5. Verify Final Consistency
    // Wait for streams to potentially finish (50 tokens * 50ms = 2.5s)
    await page.waitForTimeout(3000);

    // Check Session 2 (Index 0)
    await sessionItems.nth(0).click();
    await expect(page.locator('.bg-white', { hasText: 'Response to "Explain Relativity"' })).toBeVisible();
    await page.screenshot({ path: 'test-results/screenshots/step4_session2_final.png' });
    
    // Check Session 1 (Index 1)
    await sessionItems.nth(1).click();
    await expect(page.locator('.bg-white', { hasText: 'Response to "Explain Quantum Physics"' })).toBeVisible();
    await page.screenshot({ path: 'test-results/screenshots/step5_session1_final.png' });

    // 6. Verify No Errors
    // Playwright automatically fails on uncaught exceptions if configured, 
    // but we can also check for console errors if we added listeners (omitted for brevity).
  });
});
