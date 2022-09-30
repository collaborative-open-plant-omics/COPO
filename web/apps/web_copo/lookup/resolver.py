# enables quick access to resource directories

import os
from django.conf import settings

web_copo = os.path.join(settings.BASE_DIR, 'web', 'apps', 'web_copo')

RESOLVER = dict()
RESOLVER['ena_cli'] = os.path.join(settings.BASE_DIR, 'tools', 'reposit', 'ena_cli')
RESOLVER['schemas_copo'] = os.path.join(web_copo, 'schemas', 'copo', 'dbmodels')
RESOLVER['copo_drop_downs'] = os.path.join(web_copo, 'lookup', 'drop_downs')
RESOLVER['isa_json_db_models'] = os.path.join(web_copo, 'schemas', 'copo', 'dbmodels', 'isa', 'json')
RESOLVER['uimodels_copo'] = os.path.join(web_copo, 'schemas', 'copo', 'uimodels')
RESOLVER['cg_core_schemas'] = os.path.join(web_copo, 'schemas', 'copo', 'uimodels', "mappings", "cgcore_mappings")
RESOLVER['schemas_generic'] = os.path.join(web_copo, 'schemas', 'generic')
RESOLVER['api_return_templates'] = os.path.join(settings.BASE_DIR, 'api', 'return_templates')
RESOLVER['wizards'] = os.path.join(web_copo, 'wizards')
RESOLVER['wizards_datafile'] = os.path.join(web_copo, 'wizards', 'datafile')
RESOLVER['wizards_sample'] = os.path.join(web_copo, 'wizards', 'sample')
RESOLVER['wizards_messages'] = os.path.join(web_copo, 'wizards', 'messages')
RESOLVER['lookup'] = os.path.join(web_copo, 'lookup')
RESOLVER['copo_exceptions'] = os.path.join(settings.BASE_DIR, 'copo_exceptions')
RESOLVER['schemas_utils'] = os.path.join(web_copo, 'schemas', 'utils')
RESOLVER['cg_core_utils'] = os.path.join(web_copo, 'schemas', 'utils', 'cg_core')
RESOLVER['schemas_xml_copo'] = os.path.join(web_copo, 'schemas', 'copo', 'dbmodels', 'xmls')
RESOLVER['isa_xml_db_models'] = os.path.join(web_copo, 'schemas', 'copo', 'dbmodels', 'isa', 'xmls')

# Get "sample.json" mappings based on the current schema version
# RESOLVER['isa_mappings'] = os.path.join(web_copo, 'schemas', 'copo', 'uimodels', 'mappings', 'isa_mappings')
RESOLVER['isa_mappings'] = os.path.join(web_copo, 'schema_versions', settings.CURRENT_SCHEMA_VERSION, 'isa_mappings')
