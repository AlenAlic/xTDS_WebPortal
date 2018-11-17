from wtforms import widgets

__all__ = ['Select2Widget', ]


class Select2Widget(widgets.Select):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')
        kwargs.setdefault("width", u"100%")

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(Select2Widget, self).__call__(field, **kwargs)
