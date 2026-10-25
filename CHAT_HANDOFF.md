# Bàn giao cho chat tiếp theo

## Trạng thái hiện tại

**Tác vụ mới đang dở — Channel Nine:** Người dùng chọn làm video mới theo hướng ảnh nét hơn, kinh dị giải trí; không làm lại Hinterkaifeck. Đã chuẩn bị [The Last Voice on Channel Nine](videos/channel-nine/README.md), truyện hư cấu mới: bản nghe có sound design dài374,750 giây, Kokoro am_michael1.07, AAC48kHz stereo; đo bản AAC thực tế−16,00LUFS/−3,14dBTP, giải mã audio và coverage phụ đề đạt. Có raw voice/mix/bed, script, SRT, story bible,112 prompt ứng viên và96 cảnh được chọn có timing.

**Chặn ngoài môi trường:** image_gen trả HTTP429 usage_limit_reached ngay lần tạo ảnh mới đầu tiên. Công cụ báo reset dự kiến25/10/2026 13:12:11 giờ Việt Nam; phải thử lại sau thay đổi trạng thái thật, không lặp gọi hoặc lách hạn mức. **0/96 ảnh mới, chưa có thumbnail hoặc MP4.** [Báo cáo audio](videos/channel-nine/validation-summary.json) ghi rõ trạng thái partial. [Hướng dẫn tiếp tục](videos/channel-nine/project/README.md) và image-generation.md liệt kê phần còn lại. render_video.py mới chỉ chạy preflight thiếu ảnh; chưa chạy đường dựng/validate_video.py. Không nhận video đã hoàn thành. Không dùng lại ảnh Hinterkaifeck cho truyện này.

Người dùng đang hỏi lựa chọn công cụ tạo nhiều ảnh. Đã kiểm tra tài liệu chính thức: Claude không trực tiếp tạo ảnh minh họa kiểu image-generation; Midjourney Standard/Pro có Relax ảnh không giới hạn số lượng (phải chờ); Gemini Image API có nguồn2K/4K và phù hợp tự động hóa. Chưa có dịch vụ/API tạo ảnh thay thế được kết nối, chưa mua gói hay khai báo credential mới. Không mặc định quyền truy cập/billing cho các dịch vụ này.

Repo: https://github.com/tai23082004l02-svg/horro-story, nhánh bàn giao main. Ngày 25/10/2026, người dùng giao triển khai chủ đề Hinterkaifeck.

Đã sản xuất [Did Someone Stay? The Unsolved Hinterkaifeck Murders](videos/hinterkaifeck/README.md): 920,667 giây (khoảng 15:21), 225 hình khác nhau, trung bình 4,09 giây/cảnh, 298 mục phụ đề, 1280×720/24 fps/H.264/yuv420p/AAC 48 kHz mono. Kokoro am_michael speed 1.07. Bản cuối giải mã toàn bộ không lỗi; AAC đo thực tế −15,99 LUFS / −2,32 dBTP. [Báo cáo](videos/hinterkaifeck/validation-summary.json) có SHA-256 và phạm vi kiểm tra. Nguồn, kịch bản, thumbnail, nội dung đăng và [dự án dựng lại](videos/hinterkaifeck/project/README.md) đều có tệp thật. Không có tác vụ sản xuất còn dở hoặc lỗi kiểm tra bắt buộc còn mở trong bản này; việc đăng YouTube thuộc người dùng.

Người dùng đã **tạm bỏ mặc định minh họa 2D vẽ tay, viền đen, màu phẳng**. Phong cách cho vụ án kinh dị hiện tại là bán hiện thực, ánh sáng điện ảnh, xanh xám/nâu trầm và điểm sáng vàng; hình tĩnh và không máu me trực diện. Không tự khôi phục mặc định cũ khi chưa có yêu cầu mới. Giữ nhiều ô, 720p và các quy tắc nhịp dựng.

Giới hạn: ảnh AI là tái hiện, không phải chân dung hoặc bằng chứng thật; vụ án chưa giải; không nhận hung thủ đã chắc chắn ở lại bốn ngày. Nghiên cứu dựa trên tài liệu công bố và trích dẫn, chưa kiểm tra toàn bộ hồ sơ gốc; chưa có lượt nghe/xem thủ công toàn bộ phim. Cache mô hình và virtualenv nằm ngoài repo; trên máy mới cần kiểm tra lại theo hướng dẫn dự án.

Đọc AGENTS.md → VIDEO_GUIDELINES.md → PRODUCTION_WORKFLOW.md → DELIVERY_CHECKLIST.md, rồi tài liệu sản phẩm liên quan nếu có. Yêu cầu hiện tại của người dùng được ưu tiên.

## Các lựa chọn cần giữ

- Trao đổi tiếng Việt; sản phẩm mặc định tiếng Anh Mỹ, Kokoro am_michael, speed 1.07 làm điểm xuất phát; không atempo mặc định.
- Khi được giao làm video thì tự hoàn thành nghiên cứu/kịch bản/âm thanh/hình/dựng/QA/GitHub, không hỏi duyệt mỗi bước.
- Hình tĩnh, cắt thẳng, không zoom/pan/rung, không header/tên chương/bộ đếm hoặc dải đen cố định dưới phụ đề.
- Video dài khoảng 4 giây/cảnh: đơn giản 3–4 giây, giải thích 5–6 giây. Shorts đơn giản 2–3 giây, giải thích 4–5 giây. Không dùng nhịp cũ 4–6 giây làm mặc định mới.
- Nhiều minh họa khác nhau, đủ người, nhân vật nhất quán, không thay số hình mới bằng crop/zoom.
- Yêu cầu ảnh nét mới ưu tiên ảnh nguồn riêng đủ720p cho Channel Nine, thay cho ô nhỏ phóng lên. Giữ xuất720p, không tự tạo thử nâng nét hoặc đổi1080p. Các tài sản nhiều ô cũ của Hinterkaifeck giữ nguyên.
- Thể loại mới có thể đổi màu sắc, cảm xúc và cấu trúc kể chuyện. Không mặc định tên kênh The Long Wonder, nhân vật hoặc lịch đăng cũ thuộc repo này.
- Bàn giao GitHub có link tải thật, không chỉ link cục bộ. Không tự đăng YouTube.

## Mẫu tham khảo ở dự án gốc

Nguồn quy tắc được chuyển từ [VIDEO_GUIDELINES.md](https://github.com/tai23082004l02-svg/YTB-ng-i-que/blob/cb0ebe8305775d7981fcd7fad2d8f28d446b80d2/VIDEO_GUIDELINES.md) và [CHAT_HANDOFF.md](https://github.com/tai23082004l02-svg/YTB-ng-i-que/blob/cb0ebe8305775d7981fcd7fad2d8f28d446b80d2/CHAT_HANDOFF.md).

- [Born Between Stars](https://github.com/tai23082004l02-svg/YTB-ng-i-que/tree/cb0ebe8305775d7981fcd7fad2d8f28d446b80d2/videos/born-between-stars): mẫu đầu áp dụng nhịp mới khoảng 4 giây, 594 hình/39:38.
- [Without Us](https://github.com/tai23082004l02-svg/YTB-ng-i-que/tree/cb0ebe8305775d7981fcd7fad2d8f28d446b80d2/videos/without-us): mẫu video dài gần đây, 695 hình/46:26.
- [12 Shorts The Last Humans](https://github.com/tai23082004l02-svg/YTB-ng-i-que/tree/cb0ebe8305775d7981fcd7fad2d8f28d446b80d2/videos/the-last-humans/shorts): mẫu 9:16, lời đọc riêng từng tập, khoảng 57–64 giây.

Các tài sản này nằm ở repo gốc, chưa được chép sang đây. Không nhận là sản phẩm mới của repo này. Đừng tạo lại video cũ nếu người dùng chỉ giao chủ đề mới.

## Khi đổi chat hoặc máy

Không mặc định có /workspace/kokoro-env, cache, WAV hoặc công cụ tạo ảnh từ máy trước. Kiểm tra hiện trạng, cài lại khi cần, dùng GitHub làm nguồn bàn giao. Tài liệu không tự chuyển lịch sử chat hoặc quyền công cụ. Không yêu cầu lại token/quyền nếu công cụ hiện tại đã truy cập được; không lưu bí mật vào repo.

Sau mỗi tác vụ, cập nhật mục trạng thái bằng đường dẫn sản phẩm, số liệu đo thật, việc đã hoàn thành/đang dở, lỗi còn lại và cách tiếp tục. Giữ lựa chọn đã chốt, không thay bằng một mô tả chung chung.
