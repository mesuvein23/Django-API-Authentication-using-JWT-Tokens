from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['id','name','email','password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

        # user = User.objects.create(email = validated_data['email'])
        # user.set_password(validated_data['password'])
        # user.save()  
        # return user