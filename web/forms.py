from django import forms

class AssemblyForm(forms.Form):
    #fields from ENA assembly documentation
    study = forms.CharField(label = "STUDY") #STUDY: Study accession - mandatory
    sample = forms.CharField(label = "SAMPLE") #SAMPLE: Sample accession - mandatory
    assemblyname = forms.CharField(label = "ASSEMBLYNAME") #ASSEMBLYNAME: Unique assembly name, user-provided - mandatory
    assembly_type = forms.ChoiceField(label = "ASSEMBLY_TYPE") #ASSEMBLY_TYPE: ‘clone or isolate’ - mandatory
    coverage = forms.CharField(label = "COVERAGE") #COVERAGE: The estimated depth of sequencing coverage - mandatory
    program = forms.CharField(label = "PROGRAM") #PROGRAM: The assembly program - mandatory
    platform = forms.CharField(label = "PLATFORM") #PLATFORM: The sequencing platform, or comma-separated list of platforms - mandatory
    mingaplength = forms.CharField(label = "MINGAPLENGTH", required=False) #MINGAPLENGTH: Minimum length of consecutive Ns to be considered a gap - optional
    molecoletype = forms.ChoiceField(label = "MOLECULETYPE", required=False) #MOLECULETYPE: ‘genomic DNA’, ‘genomic RNA’ or ‘viral cRNA’ - optional
    description = forms.CharField(widget=forms.Textarea, required=False) #DESCRIPTION: Free text description of the genome assembly - optional
    run_ref = forms.CharField(label = "RUN_REF", required=False) #RUN_REF: Comma separated list of run accession(s) - optional

