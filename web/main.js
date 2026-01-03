document.addEventListener('DOMContentLoaded', async () => {
    // 检查是否通过 file:// 协议打开
    if (window.location.protocol === 'file:') {
        alert('提示：由于浏览器的安全策略（CORS），直接双击打开本地 HTML 文件无法加载 JSON 数据。请使用本地服务器运行（例如：python3 -m http.server），或者部署到 GitHub Pages/Vercel 后查看。');
    }

    try {
        const response = await fetch('data.json');
        if (!response.ok) throw new Error('无法加载 data.json');
        const data = await response.json();
        
        if (!data.trends || data.trends.length === 0) {
            document.querySelector('.container').innerHTML += '<p style="text-align:center; padding: 20px;">暂无趋势数据，请先运行爬虫脚本。</p>';
            return;
        }

        // 1. 更新时间
        document.getElementById('last-updated').innerText = `更新于: ${data.last_updated}`;

        // 2. 渲染详细列表
        const tableBody = document.querySelector('#trends-table tbody');
        data.trends.forEach(item => {
            const row = document.createElement('tr');
            const catClass = getCategoryClass(item.category);
            const trafficDisplay = formatTraffic(item.traffic_numeric);
            row.innerHTML = `
                <td><strong>${item.keyword}</strong></td>
                <td>${trafficDisplay}</td>
                <td><span class="category-tag ${catClass}">${item.category}</span></td>
                <td>${item.score.toLocaleString()}</td>
            `;
            tableBody.appendChild(row);
        });

        // 3. 渲染权重图表 (Bar Chart)
        const top10 = data.trends.slice(0, 10);
        new Chart(document.getElementById('weightChart'), {
            type: 'bar',
            data: {
                labels: top10.map(t => t.keyword),
                datasets: [{
                    label: '权重分',
                    data: top10.map(t => t.score),
                    backgroundColor: 'rgba(76, 175, 80, 0.6)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });

        // 4. 领域分布图表 (Pie Chart)
        const categories = Object.keys(data.category_stats);
        new Chart(document.getElementById('categoryChart'), {
            type: 'pie',
            data: {
                labels: categories,
                datasets: [{
                    data: categories.map(c => data.category_stats[c]),
                    backgroundColor: [
                        '#1976d2', '#d84315', '#2e7d32', '#7b1fa2', '#fbc02d'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });

        // 5. 渲染分析建议
        const insightsContainer = document.getElementById('insights-container');
        if (data.insights && data.insights.length > 0) {
            insightsContainer.innerHTML = '';
            data.insights.forEach(item => {
                const div = document.createElement('div');
                div.className = 'insight-item';
                div.innerHTML = `
                    <h3>${item.title}</h3>
                    <div class="context">${item.context}</div>
                    <div class="suggestion">${item.suggestion}</div>
                `;
                insightsContainer.appendChild(div);
            });
        } else {
            insightsContainer.innerHTML = '<p style="color: #666;">暂无分析建议。</p>';
        }

    } catch (error) {
        console.error('加载数据失败:', error);
    }
});

function getCategoryClass(cat) {
    switch (cat) {
        case '科技/AI': return 'cat-tech';
        case '体育': return 'cat-sports';
        case '金融/商业': return 'cat-finance';
        default: return 'cat-other';
    }
}

function formatTraffic(num) {
    if (num >= 10000) {
        return (num / 10000).toFixed(0) + '万+';
    }
    return num + '+';
}

