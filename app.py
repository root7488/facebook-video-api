from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Facebook Video API is running"
    })


@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "status": "OK"
    })


@app.route("/download", methods=["POST"])
def download_video():

    data = request.get_json(silent=True) or {}
    video_url = data.get("url", "").strip()

    if not video_url:
        return jsonify({
            "success": False,
            "message": "Video URL is required."
        }), 400

    allowed_hosts = (
        "facebook.com",
        "www.facebook.com",
        "m.facebook.com",
        "fb.watch"
    )

    if not video_url.startswith(("https://", "http://")):
        return jsonify({
            "success": False,
            "message": "Invalid URL."
        }), 400

    if not any(host in video_url.lower() for host in allowed_hosts):
        return jsonify({
            "success": False,
            "message": "Please provide a valid Facebook URL."
        }), 400

    try:
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "format": "best"
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                video_url,
                download=False
            )

        download_url = info.get("url")
        thumbnail = info.get("thumbnail", "")

        if not download_url:
            return jsonify({
                "success": False,
                "message": "Download URL could not be obtained."
            }), 400

        return jsonify({
            "success": True,
            "download_url": download_url,
            "thumbnail": thumbnail
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "This video could not be processed. Make sure it is publicly accessible and you have permission to download it."
        }), 400


if __name__ == "__main__":
    app.run()
