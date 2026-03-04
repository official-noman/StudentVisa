from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='get_key')
def get_key(dictionary, key):
    return dictionary.get(key, None)
    
    
@register.filter
def custom_date_format(date):
    if date is None:
        return ""  # Return an empty string if date is None
        
    if len(date.strftime("%B")) > 4:
        return date.strftime("%d %B %Y")  # For longer month names
        
    else:
        return date.strftime("%d %b %Y")  # For shorter month names