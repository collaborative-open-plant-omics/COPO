from dal.copo_da import ValidationQueue


def process_validation_queue():
    # get all manifests queued for validation
    m_list = ValidationQueue().get_queued_manifests()
    print(m_list)
