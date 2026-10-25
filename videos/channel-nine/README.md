# The Last Voice on Channel Nine

**Truyện kinh dị hư cấu mới — trạng thái: bản nghe đã xong; ảnh và video đang chờ công cụ tạo ảnh.**

Một nhân viên trực đêm nhận được lời cảnh báo bằng chính giọng mình. Anh cắt kết nối với trạm, nhưng đã mở một đường dây khác trước đó.

- [Nghe bản audio có âm thanh không khí](audio-preview.m4a) — **6:14.750**, Kokoro am_michael, tiếng Anh Mỹ, AAC48kHz stereo.
- [Kịch bản](script.txt) · [Phụ đề SRT](subtitles.srt)
- [96 cảnh đã đặt thời gian](project/shots.json) · [112 ý tưởng/prompt ảnh riêng](project/shot-prompts.json)
- [Luật truyện, nhân vật và các manh mối](project/story-bible.json)
- [Ghi rõ tính hư cấu và nguồn tài sản](SOURCES.md)
- [Số đo bản nghe](validation-summary.json) · [Cách tiếp tục dựng](project/README.md)

## Đã xác minh

Bản AAC thực tế: **-16.00 LUFS / -3.14 dBTP**; giải mã toàn bộ audio không lỗi. Phụ đề phủ toàn bộ lời kể theo thứ tự, dùng timing token Kokoro. Phần âm thanh không khí, radio và gõ cửa được tổng hợp bằng mã nguồn của dự án; không dùng nhạc/SFX tải của bên thứ ba. Đây là kiểm tra tự động, chưa có lượt nghe thủ công toàn bộ.

## Còn thiếu

**0/96 ảnh mới được tạo; chưa có video.mp4 hoặc thumbnail.** Lượt gọi ảnh đầu tiên bị HTTP429 usage_limit_reached. Công cụ báo dự kiến mở lại13:12:11 ngày25/10/2026 giờ Việt Nam; cần kiểm tra lại khả năng thực tế sau đó. [Preflight hình](project/visual-preflight.json) ghi rõ96 ảnh thiếu.

Yêu cầu hình mới: mỗi cảnh là một ảnh nguồn riêng đủ ít nhất1280×720; không phóng ô nhỏ4×4. Bản xuất dự kiến vẫn720p,24fps, hình tĩnh và cắt thẳng. Sau khi đủ ảnh cần kiểm tra nhân vật, crop và nội dung theo lời kể; tạo thumbnail, dựng và xác minh MP4 trước khi đánh dấu hoàn tất. [Nội dung đăng dự kiến](youtube-upload-kit/) chưa được dùng để đăng/lên lịch.
