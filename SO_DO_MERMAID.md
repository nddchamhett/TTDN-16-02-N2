# CÁC SƠ ĐỒ MERMAID CHO BÁO CÁO

## 1. Kiến trúc 3 tầng của ERP

```mermaid
graph TB
    subgraph "TẦNG TRÌNH DIỄN (Presentation Tier)"
        A1[Web Application]
        A2[Desktop Application]
        A3[Mobile Application]
    end
    
    subgraph "TẦNG LOGIC NGHIỆP VỤ (Business Logic Tier)"
        B1[Module Nhân sự]
        B2[Module Dự án]
        B3[Module Công việc]
        B4[Business Rules Engine]
        B5[Workflow Management]
        B6[Security & Authorization]
    end
    
    subgraph "TẦNG DỮ LIỆU (Data Tier)"
        C1[(PostgreSQL Database)]
        C2[Nhân viên Tables]
        C3[Dự án Tables]
        C4[Công việc Tables]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    
    B1 --> B4
    B2 --> B5
    B3 --> B6
    
    B4 --> C1
    B5 --> C1
    B6 --> C1
    
    C1 --> C2
    C1 --> C3
    C1 --> C4
    
    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style A3 fill:#e1f5ff
    style B1 fill:#fff4e6
    style B2 fill:#fff4e6
    style B3 fill:#fff4e6
    style C1 fill:#f3e5f5
```

## 2. Kiến trúc Odoo (MVC)

```mermaid
graph TB
    subgraph "VIEW Layer"
        V1[Form View]
        V2[Tree View]
        V3[Kanban View]
        V4[Calendar View]
    end
    
    subgraph "CONTROLLER Layer"
        CT1[HTTP Request Handler]
        CT2[Route Management]
        CT3[Authentication]
        CT4[Authorization]
    end
    
    subgraph "MODEL Layer"
        M1[Business Logic]
        M2[Fields Definition]
        M3[Constraints]
        M4[Methods]
        M5[Computed Fields]
    end
    
    subgraph "ORM Layer"
        O1[Object-Relational Mapping]
        O2[CRUD Operations]
        O3[Query Builder]
        O4[Transaction Management]
    end
    
    subgraph "DATABASE"
        DB[(PostgreSQL)]
    end
    
    V1 --> CT1
    V2 --> CT1
    V3 --> CT1
    V4 --> CT1
    
    CT1 --> CT2
    CT2 --> CT3
    CT3 --> CT4
    
    CT4 --> M1
    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> M5
    
    M5 --> O1
    O1 --> O2
    O2 --> O3
    O3 --> O4
    
    O4 --> DB
    
    style V1 fill:#e3f2fd
    style V2 fill:#e3f2fd
    style V3 fill:#e3f2fd
    style V4 fill:#e3f2fd
    style CT1 fill:#fff3e0
    style M1 fill:#f1f8e9
    style O1 fill:#fce4ec
    style DB fill:#e1bee7
```

## 3. Quy trình quản lý dự án (PMBOK)

```mermaid
graph TD
    A[KHỞI ĐỘNG<br/>Initiating] --> B[LẬP KẾ HOẠCH<br/>Planning]
    B --> C[THỰC HIỆN<br/>Executing]
    C --> D[GIÁM SÁT & KIỂM SOÁT<br/>Monitoring & Controlling]
    D --> C
    D --> E[KẾT THÚC<br/>Closing]
    
    A1[- Xác định mục tiêu<br/>- Chọn PM<br/>- Phê duyệt dự án] -.-> A
    B1[- Phạm vi<br/>- Thời gian<br/>- Chi phí<br/>- Nguồn lực<br/>- Rủi ro] -.-> B
    C1[- Phân công<br/>- Điều phối<br/>- Giao tiếp<br/>- Quản lý team] -.-> C
    D1[- Theo dõi tiến độ<br/>- Đo lường KPI<br/>- Điều chỉnh kế hoạch] -.-> D
    E1[- Bàn giao sản phẩm<br/>- Đánh giá<br/>- Rút kinh nghiệm] -.-> E
    
    style A fill:#4caf50,color:#fff
    style B fill:#2196f3,color:#fff
    style C fill:#ff9800,color:#fff
    style D fill:#f44336,color:#fff
    style E fill:#9c27b0,color:#fff
```

## 4. Mối quan hệ Dự án - Công việc - Nhân sự

```mermaid
erDiagram
    DU_AN ||--o{ CONG_VIEC : "bao gồm"
    DU_AN ||--o{ PHAN_CONG_DU_AN : "có"
    NHAN_VIEN ||--o{ PHAN_CONG_DU_AN : "tham gia"
    NHAN_VIEN ||--o{ PHAN_CONG_CONG_VIEC : "thực hiện"
    CONG_VIEC ||--o{ PHAN_CONG_CONG_VIEC : "được giao cho"
    
    DU_AN {
        int id PK
        string ten_du_an
        text mo_ta
        date ngay_bat_dau
        date ngay_ket_thuc
        float phan_tram_hoan_thanh
        string trang_thai
    }
    
    CONG_VIEC {
        int id PK
        int du_an_id FK
        string ten_cong_viec
        text mo_ta
        datetime han_chot
        float phan_tram_hoan_thanh
        string trang_thai
    }
    
    NHAN_VIEN {
        int id PK
        string ma_dinh_danh
        string ho_va_ten
        string email
        int tuoi
        string chuc_vu
    }
    
    PHAN_CONG_DU_AN {
        int du_an_id FK
        int nhan_vien_id FK
        string vai_tro
        float phan_tram_tham_gia
    }
    
    PHAN_CONG_CONG_VIEC {
        int cong_viec_id FK
        int nhan_vien_id FK
        string vai_tro
    }
```

## 5. Kiến trúc tổng thể hệ thống

```mermaid
graph TB
    subgraph "USER INTERFACE"
        UI1[Web Browser]
        UI2[Mobile Browser]
    end
    
    subgraph "ODOO FRAMEWORK"
        subgraph "Module Nhân sự"
            NS1[Quản lý nhân viên]
            NS2[Quản lý chứng chỉ]
            NS3[Lịch sử công tác]
        end
        
        subgraph "Module Dự án"
            DA1[Quản lý dự án]
            DA2[Quản lý tài nguyên]
            DA3[AI Service]
        end
        
        subgraph "Module Công việc"
            CV1[Quản lý công việc]
            CV2[Nhật ký công việc]
            CV3[Đánh giá nhân viên]
            CV4[Dashboard]
        end
    end
    
    subgraph "EXTERNAL SERVICES"
        AI[Google Gemini API]
    end
    
    subgraph "DATABASE"
        DB[(PostgreSQL)]
    end
    
    UI1 --> NS1
    UI2 --> NS1
    
    NS1 --> DA1
    NS2 --> DA1
    NS3 --> DA1
    
    DA1 --> CV1
    DA2 --> CV1
    
    DA3 --> AI
    AI --> DA3
    
    NS1 --> DB
    NS2 --> DB
    NS3 --> DB
    DA1 --> DB
    DA2 --> DB
    CV1 --> DB
    CV2 --> DB
    CV3 --> DB
    
    style UI1 fill:#e3f2fd
    style UI2 fill:#e3f2fd
    style NS1 fill:#c8e6c9
    style NS2 fill:#c8e6c9
    style NS3 fill:#c8e6c9
    style DA1 fill:#fff9c4
    style DA2 fill:#fff9c4
    style DA3 fill:#fff9c4
    style CV1 fill:#ffccbc
    style CV2 fill:#ffccbc
    style CV3 fill:#ffccbc
    style CV4 fill:#ffccbc
    style AI fill:#ce93d8
    style DB fill:#90caf9
```

## 6. Luồng xử lý AI gợi ý nhân sự

```mermaid
sequenceDiagram
    participant User
    participant UI as Giao diện Dự án
    participant Model as Model Dự án
    participant AI as AI Client
    participant Gemini as Gemini API
    participant DB as Database
    
    User->>UI: Click "AI gợi ý nhân sự"
    UI->>Model: action_ai_goi_y_nhan_su()
    
    Model->>DB: Lấy thông tin dự án
    DB-->>Model: Dữ liệu dự án
    
    Model->>DB: Lấy danh sách nhân viên
    DB-->>Model: Danh sách nhân viên + kỹ năng
    
    Model->>AI: chat_json(system_prompt, user_prompt)
    
    AI->>AI: Xây dựng prompt
    AI->>Gemini: POST /generateContent
    
    Gemini-->>AI: JSON Response
    
    AI->>AI: Parse JSON
    AI-->>Model: {nguoi_phu_trach, nhan_vien[], ghi_chu}
    
    Model->>DB: Cập nhật dự án
    DB-->>Model: Success
    
    Model-->>UI: Thông báo thành công
    UI-->>User: Hiển thị kết quả
```

## 7. Luồng xử lý AI tạo công việc

```mermaid
sequenceDiagram
    participant User
    participant UI as Giao diện Dự án
    participant Model as Model Dự án
    participant AI as AI Client
    participant Gemini as Gemini API
    participant DB as Database
    
    User->>UI: Click "AI tạo công việc"
    UI->>Model: action_ai_de_xuat_cong_viec()
    
    Model->>DB: Lấy thông tin dự án
    DB-->>Model: Dữ liệu dự án
    
    Model->>DB: Lấy team dự án
    DB-->>Model: Danh sách nhân viên
    
    Model->>AI: chat_json(system_prompt, user_prompt)
    
    AI->>AI: Xây dựng prompt
    AI->>Gemini: POST /generateContent
    
    Gemini-->>AI: JSON Response
    
    AI->>AI: Parse JSON
    AI-->>Model: {cong_viec: [{ten, mo_ta, deadline, nhan_vien}]}
    
    loop Cho mỗi công việc
        Model->>DB: Tạo record công việc
        DB-->>Model: Success
    end
    
    Model-->>UI: Thông báo thành công
    UI-->>User: Hiển thị danh sách công việc
```

## 8. Sơ đồ Use Case tổng quan

```mermaid
graph LR
    subgraph "Actors"
        Admin[Quản trị viên]
        PM[Quản lý dự án]
        NV[Nhân viên]
    end
    
    subgraph "Module Nhân sự"
        UC1[Quản lý nhân viên]
        UC2[Quản lý chứng chỉ]
        UC3[Xem lịch sử công tác]
    end
    
    subgraph "Module Dự án"
        UC4[Tạo dự án]
        UC5[Gán nhân sự]
        UC6[AI gợi ý nhân sự]
        UC7[AI tạo công việc]
        UC8[Theo dõi tiến độ]
    end
    
    subgraph "Module Công việc"
        UC9[Tạo công việc]
        UC10[Cập nhật tiến độ]
        UC11[Ghi nhật ký]
        UC12[Đánh giá nhân viên]
        UC13[Xem dashboard]
    end
    
    Admin --> UC1
    Admin --> UC2
    
    PM --> UC4
    PM --> UC5
    PM --> UC6
    PM --> UC7
    PM --> UC8
    PM --> UC9
    PM --> UC12
    PM --> UC13
    
    NV --> UC3
    NV --> UC10
    NV --> UC11
    NV --> UC13
    
    style Admin fill:#ff6b6b
    style PM fill:#4ecdc4
    style NV fill:#95e1d3
```

## 9. Sơ đồ trạng thái công việc

```mermaid
stateDiagram-v2
    [*] --> Moi: Tạo công việc
    
    Moi --> DangLam: Bắt đầu làm
    DangLam --> TamDung: Tạm dừng
    TamDung --> DangLam: Tiếp tục
    
    DangLam --> HoanThanh: Hoàn thành (100%)
    HoanThanh --> [*]
    
    Moi --> Huy: Hủy bỏ
    DangLam --> Huy: Hủy bỏ
    TamDung --> Huy: Hủy bỏ
    Huy --> [*]
    
    note right of Moi
        Công việc mới tạo
        Chưa có ai làm
    end note
    
    note right of DangLam
        Đang được thực hiện
        Tiến độ 1-99%
    end note
    
    note right of HoanThanh
        Đã hoàn thành
        Tiến độ 100%
    end note
```

## 10. Sơ đồ trạng thái dự án

```mermaid
stateDiagram-v2
    [*] --> ChuaBatDau: Tạo dự án
    
    ChuaBatDau --> DangThucHien: Ngày bắt đầu đến
    DangThucHien --> TamDung: Tạm dừng
    TamDung --> DangThucHien: Tiếp tục
    
    DangThucHien --> HoanThanh: Tất cả CV hoàn thành
    HoanThanh --> [*]
    
    ChuaBatDau --> Huy: Hủy dự án
    DangThucHien --> Huy: Hủy dự án
    TamDung --> Huy: Hủy dự án
    Huy --> [*]
    
    note right of ChuaBatDau
        Chưa đến ngày bắt đầu
        Đang chuẩn bị
    end note
    
    note right of DangThucHien
        Đang trong thời gian thực hiện
        Có công việc đang làm
    end note
    
    note right of HoanThanh
        Đã qua ngày kết thúc
        Hoặc 100% công việc xong
    end note
```

## 11. Biểu đồ Gantt mẫu cho dự án

```mermaid
gantt
    title Lịch trình dự án mẫu
    dateFormat  YYYY-MM-DD
    section Giai đoạn 1
    Phân tích yêu cầu           :a1, 2024-01-01, 7d
    Thiết kế hệ thống          :a2, after a1, 10d
    section Giai đoạn 2
    Phát triển Module Nhân sự  :b1, after a2, 14d
    Phát triển Module Dự án    :b2, after b1, 14d
    Phát triển Module Công việc:b3, after b2, 14d
    section Giai đoạn 3
    Tích hợp AI                :c1, after b3, 10d
    Kiểm thử                   :c2, after c1, 7d
    section Giai đoạn 4
    Triển khai                 :d1, after c2, 5d
    Đào tạo người dùng         :d2, after d1, 3d
```

## 12. Biểu đồ phân bổ công việc theo nhân viên

```mermaid
pie title Phân bổ công việc theo nhân viên
    "Nguyễn Văn A" : 25
    "Trần Thị B" : 20
    "Lê Văn C" : 18
    "Phạm Thị D" : 15
    "Hoàng Văn E" : 12
    "Khác" : 10
```

## 13. Biểu đồ tiến độ dự án

```mermaid
graph LR
    subgraph "Tiến độ dự án"
        A[Dự án A<br/>85%]
        B[Dự án B<br/>60%]
        C[Dự án C<br/>30%]
        D[Dự án D<br/>100%]
    end
    
    style A fill:#4caf50
    style B fill:#ff9800
    style C fill:#f44336
    style D fill:#2196f3
```

---

## Hướng dẫn sử dụng:

1. Truy cập https://mermaid.live/
2. Copy từng đoạn code mermaid ở trên
3. Paste vào editor bên trái
4. Xem kết quả bên phải
5. Click "Actions" → "Export as PNG/SVG" để tải về
6. Chèn ảnh vào báo cáo Word/PDF

**Lưu ý:** Một số sơ đồ phức tạp có thể cần điều chỉnh kích thước hoặc màu sắc để phù hợp với báo cáo của bạn.
