import fetch from 'node-fetch';

export default async function handler(req, res) {
    const { id } = req.query;

    if (!id) {
        return res.status(400).json({ error: '動画IDが必要です' });
    }

    try {
        const apiUrl = `https://inv.nadeko.net/api/v1/videos/${id}`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error('APIからの応答エラー');
        }

        const html = await response.text();
        res.setHeader('Content-Type', 'text/html');
        res.send(html);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}
