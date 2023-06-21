from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,  Row, Column

class AssemblyForm(forms.Form):

    def __init__(self, *args, sample_accession=None, study_accession=None, assembly=None, **kwargs):
        super(AssemblyForm, self).__init__(initial=assembly, *args, **kwargs)

        self.fields['study'].widget.attrs['readonly'] = True
        if study_accession and not assembly:
            self.fields['study'].initial = study_accession
        if sample_accession:
            tuplelist = []
            for x in sample_accession:
                tuplelist.append((x, x))
            self.fields['sample'].choices = tuplelist
            self.fields['sample_text'].widget.attrs['hidden'] = ''
            self.fields['sample_text'].label = ''
        else:
            self.fields['sample'].required = False
            self.fields['sample'].hidden = True
            pass
            # todo this bit does not really work, a drop down menu shows up no matter what (altough empty and optional)
            # so it works but it's an aesthetic problem
            # self.fields['sample'].hidden = True
            # self.fields['sample'].label = ''
            # self.fields['sample'].required = False

        if assembly:
            self.fields["study"].disabled = True
            self.fields["sample"].disabled = True
            self.fields["id"].initial =  str(assembly["_id"])



    # fields from ENA assembly documentation
    study = forms.CharField(label="STUDY",
                            widget=forms.TextInput(attrs={'placeholder': 'Study accession'}))
    sample = forms.ChoiceField(label="SAMPLE")
    sample_text = forms.CharField(label="SAMPLE", widget=forms.TextInput(attrs={'placeholder': 'Sample accession'}), required=False)
    assemblyname = forms.CharField(label="ASSEMBLYNAME", widget=forms.TextInput(attrs={'placeholder': 'Unique '
                                                                                                      'assembly name,'
                                                                                                      ' user-provided'}))
    assembly_type = forms.ChoiceField(label="ASSEMBLY_TYPE", choices=[('clone', 'clone'), ('isolate', 'isolate')])
    coverage = forms.FloatField(label="COVERAGE", widget=forms.TextInput(attrs={'placeholder': 'The estimated depth of '
                                                                                               'sequencing coverage'}))
    program = forms.CharField(label="PROGRAM", widget=forms.TextInput(attrs={'placeholder': 'The assembly program'}))
    platform = forms.CharField(label="PLATFORM", widget=forms.TextInput(attrs={'placeholder': 'The sequencing '
                                                                                              'platform, '
                                                                                              'or comma-separated '
                                                                                              'list of platforms'}))
    mingaplength = forms.IntegerField(label="MINGAPLENGTH", required=False,
                                      widget=forms.TextInput(
                                          attrs={'placeholder': 'Minimum length of consecutive Ns to '
                                                                'be considered a gap'}))
    moleculetype = forms.ChoiceField(label="MOLECULETYPE", required=False,
                                     choices=[('genomic DNA', 'genomic DNA'), ('genomic RNA', 'genomic RNA'),
                                              ("viral cRNA", "viral cRNA")])
    description = forms.CharField(label="DESCRIPTION", required=False,
                                  widget=forms.Textarea(attrs={'placeholder': 'Free text description of the genome '
                                                                              'assembly'}))
    run_ref = forms.CharField(label="RUN_REF", required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Comma separated list of run accession(s)'}))
    fasta = forms.FileField(label="FASTA", required=False, widget=forms.FileInput(
        #attrs={'accept': '.fasta.gz, .fas.gz, .fsa.gz, fna.gz, .fa.gz, .fasta.bz2, .fas.bz2, .fsa.bz2, .fna.bz2, .fa.bz2'}
         ))
    flatfile = forms.FileField(label="FLATFILE", required=False)
    agp = forms.FileField(label="AGP", required=False)
    chromosome_list = forms.FileField(label="CHROMOSOME_LIST", required=False)
    unlocalised_list = forms.FileField(label="UNLOCALISED_LIST", required=False)
    id = forms.CharField(label="ID", required=False, widget=forms.HiddenInput)


class AnnotationForm(forms.Form):

    def __init__(self, *args, sample_accession=None, study_accession=None, run_accession=None, experiment_accession=None, seq_annotation=None,  **kwargs):
        super(AnnotationForm, self).__init__(initial=seq_annotation, *args, **kwargs)
        if study_accession:
            self.fields['study'].initial = study_accession
            self.fields['study'].widget.attrs['readonly'] = True
        if run_accession:
            self.fields['run'].widget.attrs['readonly'] = True
            self.fields['run'].choices = [(x,x) for x in run_accession]
        if experiment_accession:
            self.fields['experiment'].widget.attrs['readonly'] = True
            self.fields['experiment'].choices =  [(x,x) for x in experiment_accession]
        if sample_accession:
            self.fields['sample'].widget.attrs['readonly'] = True
            self.fields['sample'].choices = [(x,x) for x in sample_accession]
        if kwargs.get('id', ""):
            self.fields['id'].initial = kwargs.get('id', "")
            self.fields['id'].widget.attrs['readonly'] = True

        if seq_annotation:
            #self.fields["study"].initial = seq_annotation.get("study", "")
            #self.fields["sample"].initial = seq_annotation.get("sample", "")
            #self.fields["run"].initial = seq_annotation.get("run", "")
            #self.fields["experiment"].initial = seq_annotation.get("experiment", "")
            #self.fields["title"].initial = seq_annotation.get("title", "")
            #self.fields["description"].initial = seq_annotation.get("description", "")
            self.fields["id"].initial =  str(seq_annotation["_id"])

    # fields from ENA annotation documentation
    study = forms.CharField(label="STUDY",
                            widget=forms.TextInput(attrs={'placeholder': 'Study accession'}))
    sample = forms.ChoiceField(label="SAMPLE")
    run = forms.MultipleChoiceField(label="RUN", required=False)
    experiment = forms.MultipleChoiceField(label="EXPERIMENT", required=False)

    title = forms.CharField(label="ANNOTATION TITLE", widget=forms.TextInput(attrs={'placeholder': 'Annotation title user-provided'}))
                                                                                                   
    description = forms.CharField(label="DESCRIPTION", required=False,
                                  widget=forms.Textarea(attrs={'placeholder': 'Free text description of the sequence annotation'
                                                                              'annotation'}))    
    id = forms.CharField(label="ID", required=False, widget=forms.HiddenInput)
    #files = forms.CharField(label="FILES", required=True, widget=forms.Textarea(attrs={'placeholder': 'Comma separated list of file names'}))
    
class AnnotationFilesForm(forms.Form):
    def __init__(self,  *args, ecs_files=None,  **kwargs):
        super(AnnotationFilesForm, self).__init__(*args, **kwargs)
        
        self.fields['type'].initial = None
        self.fields['file'].initial = None
        self.fields['file'].widget.attrs['readonly'] = True  
        files_choices = [("", 'None')]
        files_choices.extend([(x,x) for x in ecs_files])
        self.fields['file'].choices = files_choices
       

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('file', css_class='form-group col-md-8 mb-0'),
                Column('type', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )

    file = forms.ChoiceField(label="FILE", required=True )
    type = forms.ChoiceField(label="TYPE", required=True,
                                     choices=[('','None'),('gff', 'gff'), ('tab', 'tab'),
                                              ("fasta", "fasta"), ("bed", "bed")])

 
