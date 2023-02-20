class InteractionData:
    def __init__(self, data_init_info):
        for key, val in data_init_info.items():
            self.__dict__[key] = val