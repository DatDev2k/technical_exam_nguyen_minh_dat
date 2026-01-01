# Luồng Xử Lý Logic (Logic Flow)

Tài liệu này mô tả chi tiết quy trình xử lý dữ liệu và các logic nghiệp vụ được cài đặt trong hệ thống phân tích dữ liệu quảng cáo (`aggregator.py`).

## 1. Mục Tiêu Tổng Quan
Hệ thống được thiết kế để xử lý tệp CSV dữ liệu quảng cáo click-stream dung lượng lớn (có thể lên tới hàng GB) một cách hiệu quả, giảm thiểu việc sử dụng bộ nhớ (RAM) và tối ưu hóa thời gian thực thi. Mục tiêu cuối cùng là tổng hợp số liệu theo Chiến dịch (Campaign) và xuất ra các báo cáo xếp hạng.

## 2. Luồng Dữ Liệu (Data Pipeline)

Quy trình xử lý đi theo các bước tuần tự sau:

1.  **Input (Đầu vào)**: Nhận đường dẫn file CSV chứa dữ liệu raw (`ad_data.csv`).
2.  **Streaming Aggregation (Tổng hợp luồng)**: Đọc và xử lý từng dòng dữ liệu.
3.  **Metric Computation (Tính toán chỉ số)**: Tính các chỉ số hiệu quả (CTR, CPA) sau khi đã tổng hợp xong.
4.  **Reporting (Báo cáo)**: Sắp xếp và xuất top 10 chiến dịch ra file CSV.

## 3. Chi Tiết Logic Nghiệp Vụ

### 3.1. Tổng Hợp Dữ Liệu (Aggregation)
*Phương thức: `AdAggregator.aggregate()`*

Để xử lý file lớn mà không bị tràn bộ nhớ (Out of Memory), hệ thống **không** load toàn bộ file vào RAM (như pandas thường làm). Thay vào đó, hệ thống sử dụng kỹ thuật **Streaming**:
- Sử dụng `csv.DictReader` để tạo một iterator đọc từng dòng.
- Duyệt qua từng dòng và cộng dồn các chỉ số vào một từ điển (`dictionary`) trong bộ nhớ, với khóa (key) là `campaign_id`.
- **Dữ liệu lưu trữ**: Chỉ lưu tổng số `impressions`, `clicks`, `spend`, `conversions` cho mỗi campaign. Các cột không cần thiết (như `date`) bị bỏ qua để tiết kiệm RAM.

### 3.2. Tính Toán Chỉ Số (Metrics)
*Phương thức: `AdAggregator.compute_metrics()`*

Sau khi duyệt hết file, hệ thống tính toán các chỉ số phái sinh cho từng campaign:

#### a. Click-Through Rate (CTR)
- **Công thức**: `CTR = Clicks / Impressions`
- **Xử lý ngoại lệ**: Nếu `Impressions = 0`, gán `CTR = 0.0`.

#### b. Cost Per Acquisition (CPA)
- **Công thức**: `CPA = Spend / Conversions`
- **Xử lý ngoại lệ**: Nếu `Conversions = 0`, gán `CPA = None`. Lý do là campaign chưa có chuyển đổi nào thì không tính được chi phí trên mỗi chuyển đổi, và sẽ bị loại khỏi bảng xếp hạng Top CPA (thường ưu tiên CPA thấp nhất).

### 3.3. Báo Cáo (Reporting)
*Phương thức: `AdAggregator.write_reports()`*

Hệ thống tạo ra 2 file báo cáo trong thư mục output:

1.  **`top10_ctr.csv`**:
    - Tiêu chí: Sắp xếp theo **CTR giảm dần** (cao nhất đứng đầu).
    - Logic: Lấy 10 campaign có hiệu suất click tốt nhất.

2.  **`top10_cpa.csv`**:
    - Tiêu chí: Sắp xếp theo **CPA tăng dần** (thấp nhất đứng đầu - rẻ nhất).
    - Logic: **Loại bỏ** các campaign có `CPA = None` (0 conversions) trước khi sắp xếp. Lấy 10 campaign tối ưu chi phí chuyển đổi nhất.

## 4. Tối Ưu Hiệu Năng (Performance Optimization)

- **Input Reading**: Sử dụng thư viện chuẩn `csv` của Python (viết bằng C) cho tốc độ đọc nhanh.
- **Memory Management**: Chỉ lưu aggregate state (trạng thái tổng hợp), kích thước bộ nhớ phụ thuộc vào số lượng *unique campaign_id*, không phụ thuộc vào số lượng dòng của file input. Điều này cho phép xử lý file hàng tỷ dòng miễn là số lượng campaign nằm trong giới hạn RAM.
- **Benchmarking**: Tích hợp `tracemalloc` và `time` để đo lường lượng RAM tiêu thụ đỉnh (Peak Memory) và thời gian thực thi (Execution Time) ngay sau khi chạy xong.

## 5. Cấu Trúc File Đầu Ra
Các file báo cáo CSV bao gồm các cột:
`campaign_id`, `impressions`, `clicks`, `spend`, `conversions`, `ctr`, `cpa` (được làm tròn 4 chữ số thập phân).
