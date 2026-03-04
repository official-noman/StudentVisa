from django import template

register = template.Library()


@register.filter(name='has_perm')
def has_perm(user, permission):
    return user.has_perm(permission)
