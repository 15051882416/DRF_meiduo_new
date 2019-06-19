from django.db import models


class Area(models.Model):

    name = models.CharField(max_length=20)
    # 自关联，允许为空，表示关联对象
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subs')
    #django框架根据外键parent自动创建：parent_id===》关联对象的主键

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name













