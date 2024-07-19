from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, DecodeError
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        payload = {
            'id' : user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm = 'HS256')
 
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            'jwt' : token
        }
        return response
    

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except ExpiredSignatureError:
            raise AuthenticationFailed('Token expired. Please log in again.')
        except DecodeError:
            raise AuthenticationFailed('Invalid token. Please log in again.')

        user_id = payload.get('id')

        if not user_id:
            raise AuthenticationFailed('Invalid token. User ID not found.')

        user = User.objects.filter(id=user_id).first()

        if not user:
            raise AuthenticationFailed('User not found.')

        serializer = UserSerializer(user)
        return Response(serializer.data)

       