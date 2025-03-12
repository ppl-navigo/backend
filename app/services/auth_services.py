
class AuthService:
    @staticmethod
    def authenticate_user(username: str, password: str):
        ...
    @staticmethod
    def create_tokens(user_id: int):
        ...

    
    @staticmethod
    def refresh_tokens(refresh_token: str):
        ...
            
    
    @staticmethod
    def logout(refresh_token: str):
        ...