from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ChannelSystemBridge(SharedMemoryModel):
    db_script = models.OneToOneField('scripts.ScriptDB', related_name='channel_system_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_system_key = models.CharField(max_length=255, blank=False, null=True, unique=True)
    db_category_typeclass = models.CharField(max_length=255, blank=False, null=False)
    db_channel_typeclass = models.CharField(max_length=255, blank=False, null=False)
    db_command_class = models.CharField(max_length=255, blank=False, null=False)


class ChannelCategoryBridge(SharedMemoryModel):
    db_script = models.OneToOneField('scripts.ScriptDB', related_name='channel_category_bridge', primary_key=True,
                                      on_delete=models.CASCADE)

    db_system = models.ForeignKey(ChannelSystemBridge, related_name='channel_categories', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_unique_key = models.CharField(max_length=255, blank=False, null=True, unique=True)

    class Meta:
        verbose_name = 'ChannelCategory'
        verbose_name_plural = 'ChannelCategories'
        unique_together = (('db_system', 'db_iname'),)


class ChannelBridge(SharedMemoryModel):
    db_channel = models.OneToOneField('comms.ChannelDB', related_name='channel_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_category = models.ForeignKey(ChannelCategoryBridge, null=True, related_name='channels', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_unique_key = models.CharField(max_length=255, blank=False, null=True, unique=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        unique_together = (('db_category', 'db_iname'),)


class AbstractChannelSubscription(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_namespace = models.CharField(max_length=255, null=False, blank=False)
    db_codename = models.CharField(max_length=255, null=True, blank=False)
    db_ccodename = models.CharField(max_length=255, null=True, blank=False)
    db_icodename = models.CharField(max_length=255, null=True, blank=False)
    db_title = models.CharField(max_length=255, null=True, blank=False)
    db_altname = models.CharField(max_length=255, null=True, blank=False)
    db_muted = models.BooleanField(default=False, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        abstract = True


class AccountChannelSubscription(AbstractChannelSubscription):
    db_account = models.ForeignKey('accounts.AccountDB', related_name='channel_subscriptions', on_delete=models.CASCADE)
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='account_subscriptions', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_account', 'db_namespace', 'db_name'),
                           ('db_channel', 'db_icodename'))


class ObjectChannelSubscription(AbstractChannelSubscription):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='channel_subscriptions', on_delete=models.CASCADE)
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='object_subscriptions', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_object', 'db_namespace', 'db_name'),
                           ('db_channel', 'db_icodename'))
