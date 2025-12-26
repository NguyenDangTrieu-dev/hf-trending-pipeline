# **README.md — HF Trending Papers Pipeline**

## Mục tiêu:

Pipeline crawl HuggingFace Trending Papers, dùng Groq LLM để parse dữ liệu có cấu trúc (JSON), và quan sát hiệu năng bằng OpenTelemetry + Uptrace (Trace).

## Yêu cầu

* Python ≥ 3.10
* uv (không dùng venv)

### Tài khoản:

* Groq (API key)
* Uptrace (DSN)

## **Cài đặt môi trường**

### 1️⃣ Cài uv

`pip install uv`

### 2️⃣ Clone project
`git clone <your-repo-url>
cd hf_trending_pipeline`

### 3️⃣ Cài dependencies
`uv add requests beautifulsoup4 pydantic
uv add opentelemetry-sdk opentelemetry-exporter-otlp`

## Biến môi trường (BẮT BUỘC)

### 1️⃣ Groq API key

`export GROQ_API_KEY="gsk_xxxxxxxxx"`

### 2️⃣ Uptrace DSN

Lấy trong Uptrace project settings:

`export UPTRACE_DSN="https://<project_token>@api.uptrace.dev/<project_id>"`

### **Chạy pipeline**

`uv run python main.py`

## Xem Trace trên Uptrace

### Mở Uptrace
    https://uptrace.dev



