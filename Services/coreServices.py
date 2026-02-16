data = {}

class coreServices():
    # *********************************************
    # POST 
    # *********************************************
    @staticmethod
    def create(self, **kwargs):
        instance = cls(**kwargs)
        return instance 
    
    # *********************************************
    # GET 
    # *********************************************
    @staticmethod
    def read(self, object_id):
        return data.get(object_id)
    
    # *********************************************
    # DEL
    # *********************************************
    @staticmethod
    def delete(self, object_id):
        if object_id in data:
            del data[object_id]
    
    
    