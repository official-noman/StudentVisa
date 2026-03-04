from django import template

register = template.Library()

@register.filter(name='calculate_image_number')
def calculate_image_number(counter):
    # Calculate the image number based on the counter
    return (counter - 1) % 4 + 1
