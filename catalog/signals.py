from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Document, Product


def remove_file(field_file):
    if field_file and field_file.name:
        field_file.storage.delete(field_file.name)


def remove_old_file(model, instance, field):
    if not instance.pk:
        return
    old = model.objects.filter(pk=instance.pk).first()
    if old and getattr(old, field).name != getattr(instance, field).name:
        remove_file(getattr(old, field))


@receiver(pre_save, sender=Product)
def product_image_replaced(sender, instance, **kwargs):
    remove_old_file(Product, instance, "image")


@receiver(post_delete, sender=Product)
def product_image_deleted(sender, instance, **kwargs):
    remove_file(instance.image)


@receiver(pre_save, sender=Document)
def document_file_replaced(sender, instance, **kwargs):
    remove_old_file(Document, instance, "file")


@receiver(post_delete, sender=Document)
def document_file_deleted(sender, instance, **kwargs):
    remove_file(instance.file)
