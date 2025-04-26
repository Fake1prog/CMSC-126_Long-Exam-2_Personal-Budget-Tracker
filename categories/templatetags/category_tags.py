from django import template

register = template.Library()

@register.filter
def as_category_options(categories, selected_id=None):
    """Render categories as HTML options with data attributes."""
    html = ''
    for category in categories:
        selected = 'selected' if selected_id and str(category.id) == str(selected_id) else ''
        attrs = category.get_html_attributes()
        html += f'<option value="{category.id}" {attrs} {selected}>{category.name}</option>'
    return html