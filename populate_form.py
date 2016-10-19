from models.responses import (
    UserForm
)


def _copy_user_to_form(self, user_obj):
    user_form = UserForm()
    setattr(user_form, 'name', getattr(user_obj, 'name'))
    setattr(user_form, 'email', getattr(user_obj, 'email'))
    return user_form
