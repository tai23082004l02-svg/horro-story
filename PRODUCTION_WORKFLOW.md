# Quy trình từ chủ đề đến video

Đây là quy trình cần thực hiện, không phải báo cáo các bước đã chạy trong repo này.

## 1. Khôi phục bối cảnh và chuẩn bị

Đọc tài liệu gốc, kiểm tra git status và tài liệu video liên quan. Giữ thay đổi có sẵn. Kiểm tra Python, FFmpeg/ffprobe, dung lượng, quyền truy cập GitHub và công cụ tạo ảnh thực tế. Không giả định công cụ của chat cũ còn tồn tại hoặc cần token chỉ vì không thấy biến môi trường.

Môi trường đã từng chạy thành công: Python 3.12, PyTorch CPU, kokoro==0.9.4, soundfile, FFmpeg, spaCy en_core_web_sm 3.8.0. Dùng nguồn chính thức và xác minh TLS. Đây là cấu hình tham khảo, chưa được cài/kiểm thử trong riêng repo mới.

Nếu home chỉ đọc, đặt cache ở nơi ghi được, ví dụ UV_CACHE_DIR=/workspace/.cache/uv, HF_HOME=/workspace/.cache/huggingface, XDG_CACHE_HOME=/workspace/.cache. HF_HUB_DISABLE_XET=1 từng giúp tải ổn định; không xem đây là yêu cầu bắt buộc cho mọi máy. Không commit token, cache, virtualenv hoặc mô hình.

## 2. Nghiên cứu và kịch bản

Xác định lời hứa của video, đối tượng và thể loại từ yêu cầu. Viết outline và script tiếng Anh Mỹ. Với thông tin thực tế, lập bảng claim/nguồn/mức chắc chắn; với truyện, lập story bible, tuyến thời gian, manh mối và kết quả. Rà sự mâu thuẫn trước khi tạo lời đọc. Không dừng xin duyệt từng bước khi người dùng đã giao tự triển khai.

## 3. Tạo lời đọc và timing

Mẫu API đã dùng:

```python
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
segments = pipeline(text, voice='am_michael', speed=1.07)
```

Kiểm tra API/token timing đúng phiên bản cài đặt, lưu WAV và timing theo đoạn. Kokoro xuất sóng 24 kHz; bản cuối dùng AAC 48 kHz. Ghép khoảng nghỉ có chủ đích, không kéo dài để đủ phút. Đo thời lượng thật, sửa phát âm trước khi khóa lời đọc. Cân âm lượng theo số đo riêng, kiểm tra lại sau mã hóa AAC.

## 4. Kế hoạch hình và tạo ảnh

Từ thời lượng thật, lập shots gồm ý lời đọc, nhân vật, hành động, bối cảnh, loại cảnh, thời gian và ảnh tham chiếu. Video dài lấy số giây/4 làm ước lượng đầu, Shorts dùng nhịp riêng. Chốt story bible và bảng màu; tạo tấm nhiều ô, tuyển chọn hình, ghi lỗi và ô loại. Shorts cần bố trí dọc từ đầu; không crop bản ngang làm mất nhân vật hoặc đảo nghĩa sơ đồ.

Lưu số hàng/cột, kích thước thật, chỉ số ô và crop; không mặc định mọi bộ giống nhau. Dùng danh sách cảnh thực tế để tính số hình đã dùng, phân biệt với số ô tạo ra.

## 5. Dựng và phụ đề

Quy đổi mốc thời gian sang frame ở 24 fps, lấy hiệu hai ranh giới để tránh lệch tích lũy. Scale giữ tỷ lệ, crop tĩnh, cắt thẳng. Khớp phụ đề với token timing/lời đọc, xử lý dấu câu và chỗ đổi hình. Không bật zoom/pan hoặc thêm header theo template mặc định.

Lưu mã dựng hoặc lệnh tái tạo thực sự đã chạy, phiên bản phụ thuộc và đường dẫn tương đối. Nếu script gốc chưa được lưu, nói rõ giới hạn; không nhận chỉ có JSON là đã bảo đảm dựng lại hoàn toàn.

## 6. Kiểm tra và sửa lỗi

Kiểm tra stream bằng ffprobe và giải mã toàn bộ:

```bash
ffmpeg -v error -i video.mp4 -f null -
ffmpeg -hide_banner -i video.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null -
```

Lệnh loudnorm trên là lượt đo: đọc input_i/input_tp của tệp hiện tại, không nhầm output dự kiến với số đo bản đã sửa. Sau cân âm/mã hóa phải đo lại MP4 cuối.

Kiểm tra phụ đề không âm thời gian/chồng ngoài ý muốn/vượt thời lượng, không thiếu câu hoặc cắt chữ; kiểm tra đoạn mở đầu, giữa, cuối, cảnh nhóm, sơ đồ và chỗ chuyển chương. Xem contact sheet để rà hình lặp/lỗi; nghe mẫu ở mối nối và tên riêng. Ghi chính xác kiểm tra tự động/thủ công đã thực hiện và sửa lỗi liên quan trước bàn giao.

## 7. Cấu trúc một sản phẩm

```text
videos/<slug>/
  README.md
  video.mp4
  thumbnail.jpg
  script.txt
  subtitles.srt
  SOURCES.md                    # hoặc ghi rõ hư cấu, nguồn tham khảo nếu có
  production-notes.md
  validation-summary.json
  youtube-upload-kit/
    title.txt
    description.txt
    tags.txt
    pinned-comment.txt
  project/
    README.md                   # hướng dẫn dựng lại, phụ thuộc, giới hạn
    render.py                   # hoặc mã/lệnh dựng thực sự đã dùng
    story-bible.json
    assets/
    shots.json
    timeline.json
    captions.json
    grid-crops.json
    curation-notes.json
    normalization-settings.json
```

Đây là mẫu: chỉ ghi có tệp khi tệp thật tồn tại. Nếu làm Shorts, dùng videos/<slug>/shorts/<id>-<slug>/ và thêm ZIP + CSV thứ tự gợi ý khi bàn giao nhiều tập. Không dùng lịch/ID 12 Shorts cũ làm lịch mặc định cho chủ đề mới.

## 8. Đăng GitHub và bàn giao

Rà diff, kiểm tra link tương đối, không có bí mật hoặc file tạm. GitHub thông thường chặn tệp trên 100 MiB; cảnh báo trên 50 MB không tự đồng nghĩa push thất bại. Nếu quá giới hạn, chọn encode/phương thức phân phối phù hợp và xác minh kết quả, không tự dùng LFS khi chưa kiểm tra nhu cầu.

Commit/push vào nhánh bàn giao của repo, không force push. Xác nhận remote chứa commit và URL MP4/ZIP truy cập được. Cập nhật README và CHAT_HANDOFF bằng trạng thái thật, không chỉ ghi kế hoạch là hoàn thành. Trả lời tiếng Việt với link video và thư mục. Chủ kênh tự đăng YouTube, tự gắn Related video khi URL thật đã có; không bịa URL hoặc cam kết view/CTR.
