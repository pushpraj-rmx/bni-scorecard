from django import forms

class UploadFilesForm(forms.Form):
    scores_file = forms.FileField(label="Employee Scores File")
    training_file = forms.FileField(label="Member Training File")
