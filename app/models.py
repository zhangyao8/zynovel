from django.db import models


# Create your models here.
class Novel(models.Model):
    status_choice = (
        (0, '弃坑'),
        (1, '追更'),
    )
    status = models.IntegerField(choices=status_choice, default=1, verbose_name="小说状态")
    name = models.CharField(max_length=30, verbose_name="小说名称")
    content = models.TextField(verbose_name="小说简介")
    imgurl = models.ImageField(upload_to='./static/images/novel/', verbose_name="小说图片地址")
    srcurl = models.URLField(verbose_name="小说源站首页地址")
    updatetime = models.DateTimeField(verbose_name="小说更新时间", null=True, blank=True)

    class Meta:
        verbose_name = '小说'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class NovelContent(models.Model):
    status_choice = (
        (0, '未下载'),
        (1, '已下载'),
    )
    status = models.IntegerField(choices=status_choice, default=1, verbose_name="小说下载状态")
    title = models.CharField(max_length=30, verbose_name="章节名称")
    content = models.TextField(verbose_name="小说内容", null=True, blank=True)
    preurl = models.CharField(max_length=10, verbose_name="上一章编号", null=True, blank=True)
    nexturl = models.CharField(max_length=10, verbose_name="下一章编号", null=True, blank=True)
    srcnum = models.CharField(max_length=10, verbose_name="小说源站地址")
    novelid = models.ForeignKey(Novel)

    class Meta:
        verbose_name = '小说内容'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ReadProgress(models.Model):
    novelid = models.OneToOneField(Novel)
    chapterid = models.ForeignKey(NovelContent)

    class Meta:
        verbose_name = '阅读进度'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}---{}'.format(self.novelid, self.chapterid)
