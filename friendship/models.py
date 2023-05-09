from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
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
        # нельзя создать заявку на дружбу самому себе
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

    def accept_friend_request(self):
        """
        Принять заявку в друзья от другого пользователя
        """


class Friends(models.Model):
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
        unique_together = ('from_user', 'to_user')


    def __str__(self):
        return f"username {self.from_user} друг для {self.to_user}"