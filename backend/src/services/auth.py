from backend.src.models.user import Users


async def authenticate_user(self, db, username: str, password: str):
    user = await Users.get_by_username(db, username)
    if not user or not self.auth_handler.verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(self, db, token: str):
    try:
        payload = self.auth_handler.decode_token(token)
        username = payload.get("sub")
        return await Users.get_by_username(db, username)
    except Exception:
        return None