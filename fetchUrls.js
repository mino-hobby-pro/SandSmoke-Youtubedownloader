#100%CHATGPTです
document.getElementById('fetchButton').addEventListener('click', async () => {
    const videoId = document.getElementById('videoId').value;
    const apiUrl = `https://inv.nadeko.net/api/v1/videos/${videoId}`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const htmlText = await response.text();
        
        // https://rrで始まるURLを全て取得
        const urls = htmlText.match(/https:\/\/rr[^'"]+/g);
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = ''; // 前回の結果をクリア

        if (urls) {
            urls.forEach(url => {
                const urlElement = document.createElement('div');
                urlElement.textContent = url;
                resultDiv.appendChild(urlElement);
            });
        } else {
            resultDiv.textContent = 'URLが見つかりませんでした。';
        }
    } catch (error) {
        console.error('Error fetching the URL:', error);
    }
});
