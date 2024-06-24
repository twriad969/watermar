from flask import Flask, request, send_file
import requests
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    video_url = request.args.get('w')
    if not video_url:
        return "Please provide a video URL with the 'w' query parameter.", 400
    
    video_filename = 'input_video.mp4'
    watermarked_filename = 'watermarked_video.mp4'
    watermark_text = 'ronok'
    
    try:
        # Download the video
        video_response = requests.get(video_url)
        video_response.raise_for_status()
        
        with open(video_filename, 'wb') as f:
            f.write(video_response.content)
        
        # Add watermark using FFmpeg
        ffmpeg_command = [
            'ffmpeg', '-i', video_filename,
            '-vf', f"drawtext=text='{watermark_text}':x=10:y=h-th-10:fontcolor=white:fontsize=24",
            '-codec:a', 'copy', watermarked_filename
        ]
        
        subprocess.run(ffmpeg_command, check=True)
        
        # Send the watermarked video
        return send_file(watermarked_filename, as_attachment=True)
    
    except requests.exceptions.RequestException as e:
        return f"Failed to download the video: {str(e)}", 400
    except subprocess.CalledProcessError as e:
        return f"Failed to process the video: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
