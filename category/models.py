from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify as django_slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)  # Фото категории
    description = models.TextField(blank=True)  # Описание с возможностью HTML-разметки
    parent = models.ForeignKey('self', on_delete=models.SET_NULL,
                               related_name='children', blank=True, null=True)
    slug = models.SlugField(max_length=100, primary_key=True)

    def __str__(self):
        return f'{self.parent} -> {self.name}' if self.parent else f'{self.name}'

    # def get_children(self):
    #     if self.parent:
    #         return self.children.all()
    #     return False

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


@receiver(pre_save, sender=Category)
def category_slug_save(sender, instance, *args, **kwargs):
    # print('***************************************')
    # print('SIGNAL IS WORKED!')
    # print('***************************************')
    if not instance.slug:
        alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z',
                    'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
                    'т': 't',
                    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e',
                    'ю': 'yu',
                    'я': 'ya'}

        instance.slug = django_slugify(''.join(alphabet.get(w, w) for w in instance.name.lower()))

        # instance.slug = slugify(instance.name)

