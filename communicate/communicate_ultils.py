import uuid
def get_uuid():
    # _uuid = uuid.uuid1()
    _uuid = uuid.UUID(int=uuid.getnode())
    uuid_str = str(_uuid)
    return uuid_str[-12:]
