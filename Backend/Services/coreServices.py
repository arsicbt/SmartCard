"""Service de base fournissant les opérations CRUD génériques."""
data = {}


class coreServices():
    """Classe de base pour les services CRUD."""

    # *********************************************
    # POST
    # *********************************************
    @staticmethod
    def create(**kwargs):
        """Crée une nouvelle instance avec les paramètres fournis."""
        instance = coreServices(**kwargs)
        return instance

    # *********************************************
    # GET
    # *********************************************
    @staticmethod
    def read(object_id):
        """Retourne l'objet correspondant à l'identifiant donné."""
        return data.get(object_id)

    # *********************************************
    # DEL
    # *********************************************
    @staticmethod
    def delete(object_id):
        """Supprime l'objet correspondant à l'identifiant donné."""
        if object_id in data:
            del data[object_id]
