from django import forms


class AssemblyForm(forms.Form):

    def __init__(self, *args, sample_accession=None, study_accession=None, **kwargs):
        super(AssemblyForm, self).__init__(*args, **kwargs)
        # todo check for multiple sample
        if study_accession:
            self.fields['study'].initial = study_accession
            self.fields['study'].widget.attrs['readonly'] = True
        if sample_accession:
            tuplelist = []
            for x in sample_accession:
                tuplelist.append((x, x))
            self.fields['sample'].choices = tuplelist
            self.fields['sample_text'].widget.attrs['hidden'] = ''
            self.fields['sample_text'].label = ''
        else:
            self.fields['sample'].widget.attrs['hidden'] = ''
            self.fields['sample'].label = ''

    # fields from ENA assembly documentation
    study = forms.CharField(label="STUDY", widget=forms.TextInput(attrs={'placeholder': 'Study accession'}))
    sample = forms.ChoiceField(label="SAMPLE")
    sample_text = forms.CharField(label="SAMPLE", widget=forms.TextInput(attrs={'placeholder': 'Sample accession'}))
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
    molecoletype = forms.ChoiceField(label="MOLECULETYPE", required=False,
                                     choices=[('', ''), ('genomic DNA', 'genomic DNA'), ('genomic RNA', 'genomic RNA'),
                                              ("viral cRNA", "viral cRNA")])
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={'placeholder': 'Free text description of the genome '
                                                                              'assembly'}))
    run_ref = forms.CharField(label="RUN_REF", required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Comma separated list of run accession(s)'}))
    fasta = forms.FileField(label="FASTA", required=False, widget=forms.FileInput(
        attrs={'accept': '.fasta.gz, .fas.gz, .fsa.gz, fna.gz, .fa.gz, .fasta.bz2, .fas.bz2, .fsa.bz2, .fna.bz2, '
                         '.fa.bz2'}))
    flatfile = forms.FileField(label="FLATFILE", required=False)
    agp = forms.FileField(label="AGP", required=False)
    chromosome_list = forms.FileField(label="CHROMOSOME_LIST", required=False)
    unlocalised_list = forms.FileField(label="UNLOCALISED_LIST", required=False)
