class dummy():
    def __init__(self, input_dict, global_manager):
        for key in input_dict:
            setattr(self, key, input_dict[key])
        print(self.init_type)