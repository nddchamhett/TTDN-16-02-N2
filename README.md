<h2 align="center"> <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin"> 🎓 KHOA CÔNG NGHỆ THÔNG TIN - ĐẠI HỌC ĐẠI NAM </a> </h2>

<h1 align="center"> PLATFORM ERP (ODOO) </h1>

<div align="center"> <p align="center"> <img src="docs/logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/> <img src="docs/logo/fitdnu_logo.png" alt="FIT DNU Logo" width="180"/> <img src="docs/logo/dnu_logo.png" alt="DaiNam University Logo" width="200"/> </p>

</div>

📖 1. Tổng quan dự án
Platform ERP là hệ thống quản trị doanh nghiệp được xây dựng dựa trên mã nguồn mở Odoo. Dự án này được triển khai phục vụ cho học phần Thực tập doanh nghiệp tại Khoa Công nghệ thông tin - Đại học Đại Nam.

🔧 2. Công nghệ sử dụng (Tech Stack)
<div align="center">

Môi trường vận hành
Ngôn ngữ & Framework
Hệ quản trị Cơ sở dữ liệu
</div>

⚙️ 3. Hướng dẫn Cài đặt & Triển khai
3.1. Thiết lập môi trường phát triển
3.1.1. Clone mã nguồn
Tải mã nguồn dự án từ Github về máy cá nhân:

Bash
git clone https://github.com/FIT-DNU/Business-Internship.git
3.1.2. Cài đặt các thư viện hệ thống (System Dependencies)
Chạy lệnh sau để cài đặt các gói phụ trợ cần thiết trên Ubuntu/Linux:

Bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
3.1.3. Thiết lập môi trường ảo Python (Virtual Environment)
Để đảm bảo sự cô lập và ổn định cho dự án, hãy thực hiện các bước sau:

Khởi tạo venv:

Bash
python3.10 -m venv ./venv
Kích hoạt môi trường ảo:

Bash
source venv/bin/activate
Cài đặt các thư viện Python:

Bash
pip3 install -r requirements.txt
3.2. Khởi tạo Cơ sở dữ liệu (Database)
Dự án sử dụng Docker để chạy PostgreSQL. Khởi chạy container database bằng lệnh:

Bash
sudo docker-compose up -d
3.3. Cấu hình Odoo
Tạo tệp cấu hình odoo.conf tại thư mục gốc của dự án.

Mẹo: Bạn có thể sao chép mẫu từ tệp odoo.conf.template.

Nội dung tệp odoo.conf:

Ini, TOML
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
3.4. Khởi chạy hệ thống
Sử dụng lệnh sau để chạy Odoo và cập nhật các module:

Bash
python3 odoo-bin.py -c odoo.conf -u all
🚀 Truy cập: Mở trình duyệt và truy cập địa chỉ: http://localhost:8069/

📝 4. Bản quyền (License)
© 2024 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.
