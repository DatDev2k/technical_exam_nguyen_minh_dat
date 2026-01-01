## 📝 Các Prompt Tôi Đã Sử Dụng

### Prompt 1: Khởi tạo dự án
**Tư duy của tôi**: Bắt đầu với việc hiểu rõ yêu cầu và data schema trước khi code.

```
"Hãy phân tích file ad_data.csv và cho tôi biết schema của nó. 
Sau đó thiết kế một class để aggregate data theo campaign_id, 
tính CTR = clicks/impressions và CPA = spend/conversions."
```

**Tại sao hỏi như vậy?**
- Tôi muốn AI inspect data trước để đảm bảo hiểu đúng cấu trúc
- Yêu cầu thiết kế class cho thấy tôi muốn code có tổ chức, dễ test

---

### Prompt 2: Xử lý file lớn
**Tư duy của tôi**: File ~1GB không thể load hết vào RAM (như Pandas thường làm). Cần streaming.

```
"File CSV này rất lớn (~1GB). Hãy implement logic đọc file theo cách 
streaming (từng dòng một) để tiết kiệm RAM. Không dùng pandas."
```

**Tại sao hỏi như vậy?**
- Thể hiện tôi hiểu về memory management
- Chủ động chọn approach (streaming) thay vì để AI quyết định
- Loại bỏ pandas để giảm dependencies và control memory tốt hơn

---

### Prompt 3: Edge cases
**Tư duy của tôi**: Production code cần handle các trường hợp đặc biệt.

```
"Cần xử lý edge cases:
1. Nếu impressions = 0 thì CTR tính sao?
2. Nếu conversions = 0 thì CPA tính sao? (đề bài nói return null)
Hãy implement và viết test cases cho các trường hợp này."
```

**Tại sao hỏi như vậy?**
- Cho thấy tôi đọc kỹ đề bài (CPA = null khi conversions = 0)
- Yêu cầu test cases đi kèm để đảm bảo logic đúng

---


### Prompt 4: CLI và Benchmarking
**Tư duy của tôi**: Đề bài yêu cầu CLI tool và report performance metrics.

```
"Thêm argparse để chạy bằng command line:
python aggregator.py --input ad_data.csv --output results/

Và đo processing time + peak memory usage để báo cáo."
```

**Tại sao hỏi như vậy?**
- Tuân thủ đúng format CLI đề bài yêu cầu
- Tự động benchmark để có số liệu cho README

---

### Prompt 5: Kiểm tra output format
**Tư duy của tôi**: Đề bài có format CSV cụ thể, cần verify.

```
"Đề bài yêu cầu output format:
campaign_id, total_impressions, total_clicks, total_spend, total_conversions, CTR, CPA

Hãy check lại code xem tên cột đã đúng chưa."
```

**Tại sao hỏi như vậy?**
- Tôi so sánh output thực tế với expected format trong đề
- Phát hiện sai sót (thiếu prefix "total_") và yêu cầu sửa

---

### Prompt 6: Documentation
**Tư duy của tôi**: Code sạch cần documentation tốt.

```
"Tạo README.md với:
- Setup instructions
- Cách chạy chương trình  
- Libraries used
- Processing time và peak memory đã đo được"
```

---


## � Kết Quả Cuối Cùng

| Metric | Giá trị |
|--------|---------|
| Processing Time | 331 giây |
| Peak Memory | 0.30 MB |
| File Size | ~995 MB |
| Throughput | 3.00 MB/s |


