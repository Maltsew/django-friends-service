from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save


class User(AbstractUser):
    """
    Модель пользователя для сервиса друзей
    """
    username = models.CharField(
        'username',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return f"username: {self.username}"


class FriendshipRequest(models.Model):
    """
    Модель отображения состояния заявок дружбы
    """
    REQUEST_STATUS = (
        (1, 'None'),
        (2, 'Pending'),
        (3, 'Accept'),
        (4, 'Reject'),
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_request_sender'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_request_receiver'
    )
    request_status = models.PositiveSmallIntegerField(
      choices=REQUEST_STATUS,
      default=1,
   )

    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"username {self.from_user} created friendship request to {self.to_user}"

    def save(self, *args, **kwargs):
        """
        Расширение метода save() - нельзя отправить заявку себе самому
        """
        if self.from_user == self.to_user:
            raise ValidationError("Нельзя отправить заявку в друзья самому себе")
        super().save(*args, **kwargs)


@receiver(post_save, sender=FriendshipRequest)
def create_mutual_friends(instance, created, **kwargs):
    first_request = FriendshipRequest.objects.filter(
        from_user=instance.from_user,
        to_user=instance.to_user)
    second_request = FriendshipRequest.objects.filter(
        from_user=instance.to_user,
        to_user=instance.from_user)
    if created:
        if first_request and second_request:
            # создаем дружбу между польз.
            Friends.objects.create(from_user=instance.from_user, to_user=instance.to_user)
            # и удаляем обе заявки
            first_request.delete()
            second_request.delete()

class Friends(models.Model):
    """
    Модель, представляющая дружбу

    """
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend'
    )

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        # нельзя быть другом самому себе


    def __str__(self):
        return f"username {self.from_user} друг для {self.to_user}"

    def save(self, *args, **kwargs):
        """

        """
        if Friends.objects.filter(from_user=self.from_user, to_user=self.to_user).exists():
            raise Exception('Уже друзья')
        super().save(*args, **kwargs)