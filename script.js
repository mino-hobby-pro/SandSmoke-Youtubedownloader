document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const videoId = params.get('id');

    if (videoId) {
        const apiUrl = `https://inv.nadeko.net/api/v1/videos/${videoId}`;
        
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                const urlList = extractUrls(html);
                displayUrls(urlList);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    } else {
        document.getElementById('url-list').innerText = '動画IDが指定されていません。';
    }
});

function extractUrls(html) {
    const regex = /https:\/\/rr[^\s]+/g;
    return html.match(regex) || [];
}

function displayUrls(urls) {
    const urlListDiv = document.getElementById('url-list');
    if (urls.length > 0) {
        urlListDiv.innerHTML = '<h2>抽出されたURL:</h2><ul>' + urls.map(url => `<li>${url}</li>`).join('') + '</ul>';
    } else {
        urlListDiv.innerText = 'URLが見つかりませんでした。';
    }
}
