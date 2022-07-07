from django.http import QueryDict
from django.shortcuts import render
from django import views
from dictionary.models import Word
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import (
    serializers,
    viewsets,
    permissions,
    response,
    request,
    authentication,
)
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = \
            ('english', 'transcription', 'translation', \
            'note', 'favourite', 'category')


class MenuPage(views.View):
    def get(self, request):
        return render(request, 'api/doc_home.html')


class ApiPage(views.View):
    def get(self, request):
        return render(request, 'api/get_api.html')


class WordViewSet(LoginRequiredMixin, viewsets.ViewSet):
    renderer_classes = [JSONRenderer]

    def own_list(self, request):
        return response.Response(
                WordSerializer(Word.objects.filter(
                        user=request.user), many=True).data
            )

    # def create_word(self, request):
    #     print(request.data)
    #     serializer = WordSerializer(request.data)

# Thats not working, or i am stupid
class WordAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        return response.Response(WordSerializer(
            Word.objects.filter(user=self.request.user)).data
            )
