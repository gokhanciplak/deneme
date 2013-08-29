from django.template.defaulttags import register


@register.inclusion_tag('blog/children.html')
def subcomment_tag(parent, sub):
    parent = parent
    sub = sub
    return {'parent': parent, 'subs': sub, }
