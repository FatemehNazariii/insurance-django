from .models import MenuCategory, InsuranceCompany, CarBrand 

def header_data(request):
    categories = MenuCategory.objects.prefetch_related('items').all()
   
    return {
        'nav_categories': categories,
        'companies': InsuranceCompany.objects.all(),
        'brands': CarBrand.objects.all(), 
    }