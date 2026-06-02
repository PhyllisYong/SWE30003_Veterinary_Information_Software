from app.core.security import generateToken, hashPassword, validateToken, verifyPassword


class Authentication:
    """External authentication service proxy used by the application facade."""

    def login(self, email: str, password: str, db) -> dict | None:
        from app.models.user import User

        user = db.query(User).filter(User.email == email).first()
        if user is None or not self.verifyPassword(password, user.password):
            return None
        return {
            "token": self.issueSession(user.userID, user.role),
            "user": user,
        }

    def issueSession(self, user_id: str, role: str) -> str:
        return self.generateToken(user_id, role)

    def logout(self, user_id: str | None = None) -> bool:
        return True

    def invalidateSession(self, user_id: str) -> bool:
        return True

    def hashPassword(self, password: str) -> str:
        return hashPassword(password)

    def verifyPassword(self, plain_password: str, hashed_password: str) -> bool:
        return verifyPassword(plain_password, hashed_password)

    def generateToken(self, user_id: str, role: str) -> str:
        return generateToken(user_id, role)

    def validateToken(self, token: str) -> dict | None:
        return validateToken(token)


AuthenticationFacade = Authentication
authentication = AuthenticationFacade()
