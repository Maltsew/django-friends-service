from django.db import models

# Create your models here.
class CustomUser(models.Model):
    """
    Модель пользователя для сервиса друзей
    """
    username = models.CharField(max_length=150, unique=True, help_text='Обязательное поле', verbose_name='username')

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
        CustomUser,
        on_delete=models.CASCADE,
        related_name='friendship_request_sender'
    )
    to_user = models.ForeignKey(
        CustomUser,
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

class Friends(models.Model):
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user'
    )
    to_user = models.ForeignKey(
        CustomUser,
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