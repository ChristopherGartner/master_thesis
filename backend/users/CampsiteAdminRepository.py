from typing import List
from ..db.Database import Database
from ..users.User import User
from ..users.UserRepository import UserRepository

class CampsiteAdminRepository:
    def __init__(self, db: Database, user_repository: UserRepository):
        self.__db = db
        self.__user_repository = user_repository

    def getAdminsByCampsiteId(self, campsite_id: int) -> List[User]:
        """
        Retrieve all users who are admins for a specific campsite.
        """
        result = self.__db.execute(
            "SELECT id FROM users WHERE fk_campsiteAdmin = %s",
            (campsite_id,)
        )
        admin_ids = [row[0] for row in result]
        admins = []
        for admin_id in admin_ids:
            user = self.__user_repository.getUserById(admin_id)
            if user:
                admins.append(user)
        return admins

    def getAdminsByUserId(self, user_id: int) -> List[dict]:
        """
        Retrieve all campsite IDs where the specified user is an admin.
        """
        result = self.__db.execute(
            "SELECT fk_campsiteAdmin FROM users WHERE id = %s AND fk_campsiteAdmin IS NOT NULL",
            (user_id,)
        )
        campsite_ids = [row[0] for row in result]
        return [{"campsite_id": campsite_id} for campsite_id in campsite_ids]

    def updateCampsiteAdmins(self, campsite_id: int, selected_admin_ids: List[str]) -> None:
        """
        Update the campsite admins by setting fk_campsiteAdmin for selected users and clearing it for others.
        """
        try:
            # Convert selected_admin_ids to integers and validate
            selected_admin_ids = [int(admin_id) for admin_id in selected_admin_ids if admin_id.isdigit()]

            # First, clear fk_campsiteAdmin for any users who are no longer admins for this campsite
            self.__db.execute(
                "UPDATE users SET fk_campsiteAdmin = NULL WHERE fk_campsiteAdmin = %s AND id NOT IN (%s)" % (
                    campsite_id, ','.join(['%s'] * len(selected_admin_ids))
                ) if selected_admin_ids else (
                    "UPDATE users SET fk_campsiteAdmin = NULL WHERE fk_campsiteAdmin = %s", (campsite_id,)
                ),
                selected_admin_ids if selected_admin_ids else (campsite_id,),
                commit=True
            )

            # Then, set fk_campsiteAdmin for selected users (if not already set)
            for admin_id in selected_admin_ids:
                # Ensure user doesn't have another campsite admin role
                self.__db.execute(
                    "UPDATE users SET fk_campsiteAdmin = %s WHERE id = %s AND (fk_campsiteAdmin IS NULL OR fk_campsiteAdmin = %s)",
                    (campsite_id, admin_id, campsite_id),
                    commit=True
                )

            # Refresh user cache
            self.__user_repository.initializeUsers()

        except Exception as e:
            raise Exception(f"Failed to update campsite admins: {str(e)}")