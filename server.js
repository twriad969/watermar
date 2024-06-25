const express = require('express');
const fetch = require('node-fetch');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static('public'));
app.use(express.json());

app.post('/download', async (req, res) => {
    const { url } = req.body;

    const response = await fetch(url);
    if (!response.ok) {
        res.status(500).json({ error: 'Failed to download video' });
        return;
    }

    res.setHeader('Content-Length', response.headers.get('Content-Length'));
    res.setHeader('Content-Type', response.headers.get('Content-Type'));

    response.body.pipe(res);
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
