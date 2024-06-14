# from django import forms
# from .models import ImageProfile
#
# class AvatarUploadForm(forms.ModelForm):
#     class Meta:
#         model = ImageProfile
#         fields = ('avatar',)

from django import forms
from .models import ImageProfile

class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = ImageProfile
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['avatar'].widget.attrs.update({'accept': 'image/*'})

    def avatar_upload_path(self, filename):
        # 获取当前用户的用户名
        username = self.instance.user.username
        return f"avatar/{username}/{filename}"

    def save(self, commit=True):
        # 如果需要保存实例，则在保存前设置 avatar 字段的上传路径
        if commit:
            self.instance.avatar = self.cleaned_data['avatar']
            self.instance.avatar.upload_to = self.avatar_upload_path
        return super().save(commit)

