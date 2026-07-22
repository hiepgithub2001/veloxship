Notes DB hoang nam

1. Rename HUB 
2. Bỏ position vs department của user
3. Cân nhắc thêm role vào user
4. Cân nhắc hub_id trong user
5. Bỏ sender_name v.v.v , receiver_name v.v a. Chỉ cần id reference trong bill
6. Cân nhắc rename Trip
7. Bill -> current hub id -> latest hub id
8. Bill -> thêm latest_trip_id -> bỏ bảng tripbill
9. Design lại phần transaction => toàn bộ phần bill transaction bao gồm các phương thức thanh toán COD, chuyển khoản, nợ …
10. Thừa hub_service_areas
11. Bỏ price sheets, price rules
12. Vehicle : currenthubid -> latest_hub_id
13. Vehicle: thêm latest_trip_id
14. Tạo thêm một statemachine của bill 
15. bill_status_log: location = latest_trip_id OR latest_hub_id
16. 
