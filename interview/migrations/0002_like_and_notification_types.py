from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=36, null=True, verbose_name='点赞用户标识')),
                ('post_id', models.IntegerField(blank=True, null=True, verbose_name='被点赞帖子ID')),
                ('comment_id', models.IntegerField(blank=True, null=True, verbose_name='被点赞评论ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='点赞时间')),
            ],
            options={
                'db_table': 'interview_like',
            },
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user_id', 'post_id'), name='uniq_user_post_like'),
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user_id', 'comment_id'), name='uniq_user_comment_like'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('reply', '回复'), ('system', '系统通知'), ('like', '点赞'), ('post', '发帖'), ('announcement', '公告')], max_length=10, verbose_name='通知类型'),
        ),
    ]

