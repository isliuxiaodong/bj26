from django.contrib.auth.decorators import login_required


class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls,**initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)