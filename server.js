const express = require('express');
const axios = require('axios');
const fs = require('fs-extra');
const ffmpeg = require('fluent-ffmpeg');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Helper function to download a video
async function downloadVideo(url, outputPath) {
  const response = await axios({
    url,
    method: 'GET',
    responseType: 'stream',
  });

  return new Promise((resolve, reject) => {
    const stream = response.data.pipe(fs.createWriteStream(outputPath));
    stream.on('finish', resolve);
    stream.on('error', reject);
  });
}

// Ensure the output directory exists
const ensureOutputDirectoryExists = (filePath) => {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

// Route to handle video watermarking
app.get('/watermark', async (req, res) => {
  const videoUrl = req.query.w;
  if (!videoUrl) {
    return res.status(400).send('Video URL is required');
  }

  const inputPath = path.join(__dirname, 'input.mp4');
  const outputPath = path.join(__dirname, 'output.mp4');

  ensureOutputDirectoryExists(outputPath);

  try {
    // Download the video
    await downloadVideo(videoUrl, inputPath);

    // Add watermark using FFmpeg
    ffmpeg(inputPath)
      .outputOptions('-vf', 'drawtext=text=\\'ronok\\':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h-th-10')
      .on('end', () => {
        // Send the watermarked video
        res.sendFile(outputPath);
      })
      .on('error', (err) => {
        console.error(err);
        res.status(500).send('Error processing video');
      })
      .save(outputPath);
  } catch (error) {
    console.error(error);
    res.status(500).send('Error downloading video');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
