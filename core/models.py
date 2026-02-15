from django.db import models
from django.conf import settings 
from django.contrib.auth.models import AbstractUser, BaseUserManager 


class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError('شماره موبایل اجباری است')
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(mobile, password, **extra_fields)
    
class User(AbstractUser):
    username = None 
    mobile = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")
    wallet_balance = models.PositiveIntegerField(default=0, verbose_name="موجودی کیف پول")
    
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "همه کاربران (سایت و ادمین)"

    def __str__(self):
        return self.mobile
    
class InsuranceCard(models.Model):
    CATEGORY_CHOICES = [
        ('insurance', 'بیمه'),
        ('service', 'کالا و خدمات'),
        ('investment', 'سرمایه‌گذاری'),
    ]

    TYPE_CHOICES = [
        ('third_party', 'شخص ثالث'),
        ('body', 'بدنه'),
        ('none', 'سایر (بدون نرخ محاسباتی)'),
    ]

    title = models.CharField(max_length=100, verbose_name="عنوان بیمه")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="نشانی (Slug)")
    image = models.ImageField(upload_to='insurance_icons/', verbose_name="آیکون/تصویر")
    badge_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="متن نشان (مثلاً: تخفیف ویژه)")
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='insurance', verbose_name="دسته بندی")
    insurance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='none', verbose_name="نوع پوشش (برای محاسبات)")
    
    price_start = models.CharField(max_length=100, blank=True, null=True, verbose_name="شروع قیمت از")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    meta_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="عنوان سئو")
    meta_description = models.TextField(blank=True, null=True, verbose_name="توضیحات سئو")

    class Meta:
        verbose_name = "کارت بیمه"
        verbose_name_plural = "کارت‌های بیمه"
        ordering = ['order']

    def __str__(self):
        return self.title

class MenuCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته")
    icon_class = models.CharField(max_length=50, default="fa-circle", verbose_name="کلاس آیکون")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['order']
        verbose_name = "دسته بندی منو"
        verbose_name_plural = "دسته بندی‌های منو"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="عنوان")
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, verbose_name="نشانی صفحه (Slug)", blank=True, null=True)
    description = models.TextField(verbose_name="توضیحات صفحه", blank=True)
    
    insurance_card = models.ForeignKey(
        InsuranceCard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="اتصال به صفحه بیمه"
    )
    external_link = models.CharField(max_length=200, blank=True, null=True, verbose_name="لینک خارجی (فقط وقتی اسلاگ و بیمه خالی باشد)")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ['order']
        verbose_name = "آیتم زیرمنو"
        verbose_name_plural = "آیتم‌های زیرمنو"

    def __str__(self):
        return self.title

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام شرکت")
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, verbose_name="نشانی (Slug)", blank=True, null=True)
    logo = models.ImageField(upload_to='companies/', verbose_name="لوگو")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    wealth_level = models.IntegerField(default=1, verbose_name="سطح توانگری")
    complaint_response_rate = models.IntegerField(default=100, verbose_name="درصد پاسخگویی به شکایات")

    class Meta:
        verbose_name = "شرکت بیمه همکار"
        verbose_name_plural = "شرکت‌های بیمه همکار"
        ordering = ['order']

    def __str__(self):
        return self.name

class InsuranceRate(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, related_name='rates', verbose_name="شرکت بیمه")
    
    insurance_type = models.CharField(
        max_length=20, 
        choices=[('body', 'بدنه'), ('third_party', 'ثالث')], 
        verbose_name="نوع بیمه"
    )
    base_fee = models.BigIntegerField(verbose_name="حق بیمه پایه (ریال)")
    car_value_coefficient = models.FloatField(default=0.005, verbose_name="ضریب ارزش خودرو")
        
        
class DamageStep(models.Model):
    number = models.IntegerField(verbose_name="شماره مرحله")
    title = models.CharField(max_length=100, verbose_name="عنوان مرحله")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "مرحله دریافت خسارت"
        verbose_name_plural = "مراحل دریافت خسارت"

    def __str__(self):
        return f"{self.number}. {self.title}"

class Inquiry(models.Model):
    phone_number = models.CharField(max_length=15, verbose_name="شماره تماس") 
    insurance_type = models.CharField(max_length=100, default='مشاوره کلی', verbose_name="نوع مشاوره")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    
    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"

class DamageReport(models.Model):
    INSURANCE_TYPES = [('third_party', 'بیمه شخص ثالث'), ('car_body', 'بیمه بدنه')]
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPES, verbose_name="نوع بیمه")
    company_name = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, verbose_name="شرکت بیمه")
    address = models.TextField(verbose_name="آدرس بازدید")
    phone_number = models.CharField(max_length=15, verbose_name="شماره موبایل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "گزارش خسارت"
        verbose_name_plural = "گزارش‌های خسارت"

class InsuranceInfo(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان بیمه")
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, verbose_name="نشانی (Slug)", blank=True, null=True)
    description = models.TextField(verbose_name="توضیحات کوتاه")
    image = models.ImageField(upload_to='insurance_info/', verbose_name="تصویر")
    link = models.CharField(max_length=200, default="#", blank=True, verbose_name="لینک خارجی (در صورت خالی بودن از اسلاگ استفاده می‌شود)")

    class Meta:
        verbose_name = "اطلاعات بیمه"
        verbose_name_plural = "اطلاعات بیمه"

    def __str__(self):
        return self.title

class Feature(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان ویژگی")
    description = models.TextField(verbose_name="توضیحات کوتاه")
    icon_class = models.CharField(max_length=100, verbose_name="کد آیکون FontAwesome")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ['order']

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ['order']

class TrustStep(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان مرحله")
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to='trust/', verbose_name="تصویر")
    order = models.IntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "گام اعتماد"
        verbose_name_plural = "گام‌های اعتماد"
        ordering = ['order']
        


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('canceled', 'لغو شده'),
    )
    PAYMENT_TYPES = (
        ('cash', 'نقدی'),
        ('installment', 'اقساطی'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    insurance = models.ForeignKey(InsuranceCard, on_delete=models.CASCADE, verbose_name="بیمه", related_name="insurance_orders")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ ثبت شده")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='cash', verbose_name="نوع پرداخت")
    installments_count = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد اقساط")
    company_name = models.CharField(max_length=100, verbose_name="نام شرکت بیمه", null=True, blank=True)
    plate_number = models.CharField(max_length=20, verbose_name="شماره پلاک", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    is_paid = models.BooleanField(default=False, verbose_name="وضعیت پرداخت کلی")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    national_code = models.CharField(max_length=10, verbose_name="کد ملی", null=True, blank=True)
    insurance_company = models.ForeignKey(
        InsuranceCompany, 
        on_delete=models.PROTECT, 
        verbose_name="شرکت بیمه همکار",
        related_name="orders",
        null=True)
    
    class Meta:
        verbose_name = "سفرش"
        verbose_name_plural = "سفارشات"

    def __str__(self):
        return f"سفارش {self.id} - {self.insurance.title} ({self.get_payment_type_display()})"

class Installment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='installments', verbose_name="سفارش")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ قسط")
    due_date = models.DateField(verbose_name="تاریخ سررسید")
    is_paid = models.BooleanField(default=False, verbose_name="وضعیت پرداخت قسط")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت واقعی")

    class Meta:
        verbose_name = "قسط"
        verbose_name_plural = "اقساط"

    def __str__(self):
        return f"قسط سفارش {self.order.id} - مبلغ {self.amount}"
    
class InsuranceBenefit(models.Model):
    insurance_card = models.ForeignKey(
        InsuranceCard, 
        on_delete=models.CASCADE, 
        related_name='benefits', 
        verbose_name="مربوط به بیمه"
    )
    title = models.CharField(max_length=100, verbose_name="عنوان مزیت (مثلاً: امنیت مالی)")
    description = models.TextField(verbose_name="توضیح کوتاه")
    image = models.ImageField(upload_to='benefits/', verbose_name="آیکون گرافیکی (SVG یا PNG)")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "مزیت بیمه"
        verbose_name_plural = "مزایای بیمه"
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.insurance_card.title}"
    
from django.db import models

class CarBrand(models.Model):
    name = models.CharField(max_length=50, verbose_name="برند خودرو")
    
    def __str__(self):
        return self.name

class CarModel(models.Model):
    FUEL_CHOICES = [
        ('gasoline', 'بنزینی'),
        ('diesel', 'دیزلی'),
        ('hybrid', 'هیبرید'),
        ('electric', 'برقی'),
        ('cng', 'دوگانه سوز'),
    ]

    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models', verbose_name="برند")
    name = models.CharField(max_length=100, verbose_name="نام مدل")
    base_price = models.BigIntegerField(default=0, verbose_name="قیمت پایه (ریال/تومان)")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='gasoline', verbose_name="نوع سوخت")

    class Meta:
        verbose_name = "مدل خودرو"
        verbose_name_plural = "مدل‌های خودرو"

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


class MotorcycleBrand(models.Model):
    """برند موتورسیکلت — از پنل ادمین قابل افزودن و حذف است."""
    name = models.CharField(max_length=80, verbose_name="برند موتور")

    class Meta:
        verbose_name = "برند موتور"
        verbose_name_plural = "برندهای موتور"

    def __str__(self):
        return self.name


class MotorcycleModel(models.Model):
    """مدل موتورسیکلت — وابسته به برند، از پنل ادمین قابل افزودن و حذف است."""
    brand = models.ForeignKey(
        MotorcycleBrand,
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name="برند موتور"
    )
    name = models.CharField(max_length=100, verbose_name="نام مدل")
    base_price = models.BigIntegerField(default=0, verbose_name="قیمت پایه (ریال)")

    class Meta:
        verbose_name = "مدل موتور"
        verbose_name_plural = "مدل‌های موتور"

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


