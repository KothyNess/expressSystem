from django import forms

'''
快递员 /新增/修改 表单
'''

class StaffForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())  # 隐藏字段

    # 所属分公司选择框
    company = forms.ModelChoiceField(
        queryset=None,  # 该字段将在__init__方法中动态设置
        label='所属分公司',
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'margin-bottom:15px;'})
    )

    # 所属分站选择框
    station = forms.ModelChoiceField(
        queryset=None,  # 该字段将在__init__方法中动态设置
        label='所属分站',
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'margin-bottom:15px;'})
    )

    # 快递员姓名
    staff_name = forms.CharField(
        label='快递员姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '快递员姓名', 'required': True})
    )

    # 快递员账号
    staff_username = forms.CharField(
        label='快递员账号',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '快递员账号', 'required': True})
    )

    # 快递员密码
    staff_passwd = forms.CharField(
        label='快递员密码',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '快递员账号的密码', 'required': True})
    )

    def __init__(self, *args, companies=None, stations=None, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        if companies is not None:
            self.fields['company'].queryset = companies
        if stations is not None:
            self.fields['station'].queryset = stations