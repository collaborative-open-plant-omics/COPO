These files specify which field groups are displayed on the DTOL sample wizard based on the dropdown selected
by the user as they are not all relvant to all users. The fields themselves were previously defined in
web/apps/web_copo/schemas/copo/uimodels/mappings/isa_mappings/sample.json but now the fiels are defined based
on the current schema in the directory web/apps/web_copo/schema_versions/<current_schema_version>/isa_mappings/sample.json
and then grouped into like field types in web/apps/web_copo/wizards/sample/dtol_field_mapping.json