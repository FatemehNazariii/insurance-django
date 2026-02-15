from .models import MenuCategory, InsuranceCompany, CarBrand 

def header_data(request):
    # دریافت تمام دسته‌بندی‌ها به همراه زیرمنوهایشان
    categories = MenuCategory.objects.prefetch_related('items').all()
   
    return {
        'nav_categories': categories,
        'companies': InsuranceCompany.objects.all(),
        'brands': CarBrand.objects.all(), 
    }