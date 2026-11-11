# Auto Clicker Pro — bộ dựng EXE Windows

Mục tiêu: tạo `AutoClickerPro.exe` chạy trên Windows 10/11 mà máy sử dụng **không cần cài Python**.

## Cách lấy file EXE mà không cài Python trên máy của bạn

Cách đơn giản nhất là dùng GitHub Actions (GitHub sẽ dựng EXE trên máy Windows của họ):

1. Đăng nhập hoặc tạo tài khoản tại https://github.com.
2. Tạo một repository mới, ví dụ `auto-clicker-pro`.
3. Giải nén gói này và tải toàn bộ nội dung bên trong lên repository (giữ nguyên thư mục `.github/workflows/`).
4. Mở tab **Actions** của repository.
5. Chọn workflow **Build Auto Clicker Pro for Windows** rồi bấm **Run workflow** nếu workflow chưa tự chạy.
6. Khi job hoàn tất, mở lần chạy đó và tải artifact **AutoClickerPro-Windows**.
7. Giải nén artifact; chạy `AutoClickerPro.exe`.

Bạn không cần cài Python để chạy EXE. GitHub Actions dùng Python trên máy dựng tự động để đóng gói ứng dụng.

## Nếu máy bạn đã có Python
Nhấp đúp `build_windows.bat`. File EXE sẽ nằm trong `dist\AutoClickerPro.exe`.

## Ghi chú
- Gói này là dự án dựng EXE, không phải file EXE đã biên dịch sẵn. Môi trường tạo gói hiện tại không phải Windows nên không thể biên dịch và kiểm thử trực tiếp file `.exe` Windows tại đây.
- Windows SmartScreen/antivirus có thể cảnh báo vì EXE tự đóng gói chưa được ký số. Chỉ chạy nếu bạn tin tưởng nguồn file.
- Khi chạy, có thể cần cấp quyền Accessibility/keyboard hook tùy cấu hình Windows.
- Tính năng marker xuyên click dùng pywin32 trên Windows.
- Phím tắt: F7 thêm điểm; F6 bắt đầu/dừng. Góc trên trái màn hình là vùng dừng khẩn cấp PyAutoGUI.
