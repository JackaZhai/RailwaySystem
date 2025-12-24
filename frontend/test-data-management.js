// 简单测试数据管理页面
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('打开数据管理页面...');
  await page.goto('http://localhost:5175');

  // 等待页面加载
  await page.waitForTimeout(2000);

  // 检查是否有数据统计卡片
  console.log('检查数据统计卡片...');
  const statCards = await page.$$('.stat-card');
  console.log(`找到 ${statCards.length} 个统计卡片`);

  // 检查卡片内容
  for (let i = 0; i < statCards.length; i++) {
    const card = statCards[i];
    const text = await card.textContent();
    console.log(`卡片 ${i + 1}: ${text.trim().substring(0, 50)}...`);
  }

  // 检查控制台错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('浏览器控制台错误:', msg.text());
    }
  });

  // 等待更多时间看看是否有数据加载
  await page.waitForTimeout(5000);

  // 再次检查卡片内容
  console.log('\n5秒后再次检查数据...');
  const statCardsAfter = await page.$$('.stat-card');
  for (let i = 0; i < statCardsAfter.length; i++) {
    const card = statCardsAfter[i];
    const text = await card.textContent();
    console.log(`卡片 ${i + 1}: ${text.trim().substring(0, 50)}...`);
  }

  // 检查网络请求
  console.log('\n检查网络请求...');
  const requests = [];
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      requests.push({
        url: request.url(),
        method: request.method()
      });
    }
  });

  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log(`API响应: ${response.url()} - ${response.status()}`);
    }
  });

  // 刷新页面看看是否有API调用
  await page.reload();
  await page.waitForTimeout(3000);

  console.log(`\nAPI请求数量: ${requests.length}`);
  requests.forEach((req, i) => {
    console.log(`请求 ${i + 1}: ${req.method} ${req.url}`);
  });

  await browser.close();
})();