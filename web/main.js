document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('data.json');
        const data = await response.json();

        // 1. 更新时间
        document.getElementById('last-updated').innerText = `更新于: ${data.last_updated}`;

        // 2. 渲染详细列表
        const tableBody = document.querySelector('#trends-table tbody');
        data.trends.forEach(item => {
            const row = document.createElement('tr');
            const catClass = getCategoryClass(item.category);
            row.innerHTML = `
                <td><strong>${item.keyword}</strong></td>
                <td>${item.traffic}</td>
                <td><span class="category-tag ${catClass}">${item.category}</span></td>
                <td>${item.score}</td>
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

