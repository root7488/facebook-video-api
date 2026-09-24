from flask import Flask, request, jsonify, send_file, after_this_request
import yt_dlp
import tempfile
import os

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


def is_valid_facebook_url(video_url):
    allowed_hosts = (
        "facebook.com",
        "www.facebook.com",
        "m.facebook.com",
        "fb.watch"
    )

    return (
        video_url.startswith(("https://", "http://"))
        and any(host in video_url.lower() for host in allowed_hosts)
    )


@app.route("/download", methods=["POST"])
def download_video():

    data = request.get_json(silent=True) or {}
    video_url = data.get("url", "").strip()

    if not video_url:
        return jsonify({
            "success": False,
            "message": "Video URL is required."
        }), 400

    if not is_valid_facebook_url(video_url):
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


@app.route("/download-file", methods=["GET"])
def download_file():

    video_url = request.args.get("url", "").strip()

    if not video_url:
        return "Video URL is required.", 400

    if not is_valid_facebook_url(video_url):
        return "Invalid Facebook URL.", 400

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(
        temp_dir,
        "facebook_video.%(ext)s"
    )

    try:
        options = {
            "quiet": True,
            "no_warnings": True,
            "format": "best",
            "outtmpl": output_template
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        files = os.listdir(temp_dir)

        if not files:
            return "Video download failed.", 500

        file_path = os.path.join(
            temp_dir,
            files[0]
        )

        @after_this_request
        def cleanup(response):
            try:
                for filename in os.listdir(temp_dir):
                    os.remove(
                        os.path.join(
                            temp_dir,
                            filename
                        )
                    )
                os.rmdir(temp_dir)
            except Exception:
                pass

            return response

        return send_file(
            file_path,
            as_attachment=True,
            download_name="facebook-video.mp4"
        )

    except Exception:
        try:
            for filename in os.listdir(temp_dir):
                os.remove(
                    os.path.join(
                        temp_dir,
                        filename
                    )
                )
            os.rmdir(temp_dir)
        except Exception:
            pass

        return (
            "Video could not be downloaded. "
            "Make sure it is publicly accessible "
            "and you have permission to download it.",
            400
        )


if __name__ == "__main__":
    app.run()
