from typing import  Optional
from ninja import Query, Schema
from ninja_extra import route, api_controller, ControllerBase
from ninja_extra.pagination import paginate

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from pop.core import permissions as perms
from pop.core.security import XSessionTokenAuth
from pop.core.models import User
from pop.core.schemas import (
    Paginated,
    UserFilters,
    UserSchema, 
    UserCreateSchema,
    UserProfileSchema,
    UserPasswordResetSchema,
    ModifiedResourceSchema,
)
    
@api_controller(
    '/users', 
    auth=[XSessionTokenAuth()], 
    tags=['Users'],  
)
class UsersController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[UserSchema],
            401: None, 403: None,
        }, 
        operation_id='getUsers',
    )
    @paginate
    def get_all_users_matching_the_query(self, query: Query[UserFilters]): # type: ignore
        queryset = get_user_model().objects.all()
        return query.filter(queryset)
    
    @route.get(
        path="/{userId}", 
        response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        }, 
        operation_id='getUserById',
    )
    def get_user_by_id(self, userId: str):
        return get_object_or_404(get_user_model(), id=userId)


    @route.post(
        path="", 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        }, 
        permissions=[perms.CanManageUsers],
        operation_id='createUser',
    )
    def create_user(self, payload: UserCreateSchema):
        return 201, payload.model_dump_django()

    @route.put(
        path='/{userId}', 
       response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='updateUser',
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        user = get_object_or_404(User, id=userId)
        return payload.model_dump_django(instance=user)
        
    @route.put(
        path='/{userId}/profile', 
       response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageUsers | perms.IsRequestingUser],
        operation_id='updateUserProfile',
    )
    def update_user_profile(self, userId: str, payload: UserProfileSchema):
        user = get_object_or_404(User, id=userId)
        User.objects.filter(pk=user.id).update(**payload.model_dump(by_alias=True))
        return 201, get_object_or_404(User, id=user.id)
    
    @route.put(
        path='/{userId}/password', 
       response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        operation_id='updateUserPassword',
    )
    def update_user_password(self, userId: str, payload: UserPasswordResetSchema):
        user = get_object_or_404(User, id=userId)
        requesting_user = self.context.request.user
        authorized = user.id == requesting_user.id or requesting_user.can_manage_users
        if not authorized or not user.check_password(payload.oldPassword):
            return 403, None
        user.set_password(payload.newPassword)
        user.save()
        return 201, user 
    

    @route.post(
        path='/{userId}/password/reset', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='resetUserPassword',
    )
    def reset_user_password(self, userId: str, password: str):
        user = get_object_or_404(User, id=userId)
        user.set_password(password)
        user.save()
        return 201, user 
