data = {}

class coreServices():
    
    # --- P O S T  S E C T I O N ----------------
    @staticmethod
    def create(self, **kwargs):
        instance = cls(**kwargs)
        return instance 
    

    # --- G E T  S E C T I O N ----------------
    @staticmethod
    def read(self, object_id):
        return data.get(object_id)
    
    
    # --- D E L E T E  S E C T I O N -----------
    @staticmethod
    def delete(self, object_id):
        if object_id in data:
            del data[object_id]
    
    
    