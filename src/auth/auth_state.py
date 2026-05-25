class AuthState:
    def __init__(self):
        self.is_authenticated = False
        self.email = None
        self.local_id = None
        self.id_token = None
        self.refresh_token = None

    def login(self, auth_result: dict):
        self.is_authenticated = True
        self.email = auth_result.get("email")
        self.local_id = auth_result.get("local_id")
        self.id_token = auth_result.get("id_token")
        self.refresh_token = auth_result.get("refresh_token")

    def logout(self):
        self.is_authenticated = False
        self.email = None
        self.local_id = None
        self.id_token = None
        self.refresh_token = None