from django.contrib.auth.base_user import BaseUserManager


class MyManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('The email field must be set!')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **kwargs)
        user.create_activation_code()
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        if kwargs.get('is_staff') is not True:
            raise ValueError('The superuser must have "is_staff=True"')
        if kwargs.get('is_active') is not True:
            raise ValueError('The superuser must have "is_active=True"')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('The superuser must have "is_superuser=True"')
        return self._create_user(email, password, **kwargs)
