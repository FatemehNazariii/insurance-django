# استفاده از نسخه کامل پایتون (که ابزارهای لازم را از قبل دارد)
FROM python:3.13

# تنظیمات محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تعیین پوشه کاری
WORKDIR /app

# نصب کتابخانه‌های پایتون (مستقیماً سراغ اصل مطلب می‌رویم)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# کپی کدها
COPY . /app/

# اجرا
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]