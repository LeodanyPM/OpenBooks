from django import template

register = template.Library()

@register.filter
def stars(rating):
    score = round(float(rating or 0))
    filled = "★" * score
    empty = "☆" * (5 - score)
    return f'<span class="text-warning">{filled}{empty}</span>'
