import json

import requests
from common.utils import centrifugo_post, is_authorized, is_valid_organisation
from django.conf import settings
from email_template.serializers import (
    EmailSerializer,
    EmailUpdateSerializer,
    SendEmailSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

ZURI_API_KEY = settings.ZURI_API_KEY
CENTRIFUGO_LIVE_ENDPOINT = settings.CENTRIFUGO_LIVE_ENDPOINT
API_KEY = settings.API_KEY
CENTRIFUGO_DEBUG_ENDPOINT = settings.CENTRIFUGO_DEBUG_ENDPOINT


PLUGIN_ID = settings.PLUGIN_ID
ORGANISATION_ID = settings.ORGANISATION_ID
# Create your views here.


class EmailTemplateCreateView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]

    Returns:
        [type]: [description]
    """

    serializer_class = EmailSerializer
    queryset = None

    def post(self, request):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        # check if user is authenticated
        # if not is_authorized(request):
        #     return Response(data={"message":"Missing Cookie/token header or session expired"}, status=status.HTTP_401_UNAUTHORIZED)

        # if not is_valid_organisation(ORGANISATION_ID, request):
        #     return Response(data={"message":"Invalid/Missing organization id"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = "https://api.zuri.chat/data/write"
        subject = request.data.get("subject")
        email = request.data.get("email")
        template_name = request.data.get("template_name")
        message = request.data.get("message")
        data = {
            "plugin_id": PLUGIN_ID,
            "organization_id": ORGANISATION_ID,
            "collection_name": "email_template",
            "bulk_write": False,
            "payload": {
                "subject": subject,
                "template_name": template_name,
                "email": email,
                "message": message,
            },
        }
        response = requests.post(url, data=json.dumps(data))
        res = response.json()
        if response.status_code == 201:
            centrifugo_post(
                "Email",
                {
                    "event": "new_template",
                    "token": "elijah",
                    "object": res,
                },
            )
            return Response(data=response.json(), status=status.HTTP_201_CREATED)
        return Response(
            data={"message": "Try again later"},
            status=response.status_code,
        )


class EmailTemplateListView(APIView):
    """

    [summary]

    Returns:
        [type]: [description]
    """

    serializer_class = EmailSerializer
    queryset = None

    def get(self, request):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        # check if user is authenticated
        if not is_authorized(request):
            return Response(
                data={"message": "Missing Cookie/token header or session expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_valid_organisation(ORGANISATION_ID, request):
            return Response(
                data={"message": "Invalid/Missing organization id"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        centrifugo_post("Email", {"event": "join", "token": "elijah"})
        url = f"https://api.zuri.chat/data/read/{PLUGIN_ID}/email_template/{ORGANISATION_ID}"
        response = requests.request("GET", url)
        if response.status_code == 200:
            return Response(data=response.json(), status=status.HTTP_200_OK)
        return Response(
            data=response.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class EmailDetailView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """

    def get(self, _id):
        """[summary]

        Args:
            request ([type]): [description]
            id ([type]): [description]

        Returns:
            [type]: [description]
        """
        url = "https://api.zuri.chat/data/read"
        data = {
            "plugin_id": PLUGIN_ID,
            "organization_id": ORGANISATION_ID,
            "collection_name": "email_template",
            "filter": {},
            "object_id": _id,
        }

        response = requests.post(url, data=json.dumps(data))
        print(response.json())
        if response.status_code == 200:
            return Response(data=response.json(), status=status.HTTP_200_OK)
        return Response(
            data=response.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class EmailTemplateUpdateView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]

    Returns:
        [type]: [description]
    """

    serializer_class = EmailUpdateSerializer
    queryset = None

    def put(self, request, template_id):
        """
        [summary]

        Args:
            request ([type]): [description]
            template_id ([type]): [description]

        Returns:
            [type]: [description]
        """
        # check if user is authenticated
        if not is_authorized(request):
            return Response(
                data={"message": "Missing Cookie/token header or session expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_valid_organisation(ORGANISATION_ID, request):
            return Response(
                data={"message": "Invalid/Missing organization id"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        url = "https://api.zuri.chat/data/write"
        serializer = EmailUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # object_id = serializer.data.get("object_id")
        data = {
            "plugin_id": PLUGIN_ID,
            "organization_id": ORGANISATION_ID,
            "collection_name": "email_template",
            "bulk_write": False,
            "object_id": template_id,
            "payload": serializer.data,
        }
        response = requests.put(url, data=json.dumps(data))

        if response.status_code in [200, 201]:
            response = response.json()
            centrifugo_post(
                "Email",
                {
                    "event": "edit_email",
                    "token": "elijah",
                    "object": response,
                },
            )
            return Response(data=response, status=status.HTTP_200_OK)

        return Response(
            data={"message": "Try again later", "data": request.data},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class EmailTemplateDeleteView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """

    def delete(self, request, template_id):
        """[summary]

        Args:
            request ([type]): [description]
            template_id ([type]): [description]

        Returns:
            [type]: [description]
        """
        # check if user is authenticated
        if not is_authorized(request):
            return Response(
                data={"message": "Missing Cookie/token header or session expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_valid_organisation(ORGANISATION_ID, request):
            return Response(
                data={"message": "Invalid/Missing organization id"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        url = "https://api.zuri.chat/data/delete"
        data = {
            "plugin_id": PLUGIN_ID,
            "organization_id": ORGANISATION_ID,
            "collection_name": "email_template",
            "object_id": template_id,
        }
        response = requests.post(url, data=json.dumps(data))
        print(response.text)
        res = response.json()
        if ((response.status_code == 200) and (res["data"]["deleted_count"])) == 0:
            return Response(
                data={
                    "message": "There is no template with the object id you supplied"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if response.status_code == 200:
            res = response.json()
            centrifugo_post(
                "Email",
                {
                    "event": "delete_email",
                    "token": "elijah",
                    "id": res,
                },
            )
            return Response(
                data={"message": f"{template_id} was deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"message": "Try again later"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class EmailSendView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]

    Returns:
        [type]: [description]
    """

    serializer = SendEmailSerializer
    queryset = None

    def post(self, request):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        if not is_authorized(request):
            return Response(
                data={"message": "Missing Cookie/token header or session expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not is_valid_organisation(ORGANISATION_ID, request):
            return Response(
                data={"message": "Invalid/Missing organization id"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mail = request.data.get("mail_body")

        url = "https://api.zuri.chat/external/send-mail?custom_mail=1"
        data = {
            "email": request.data.get("email"),
            "subject": request.data.get("subject"),
            "content_type": "text/html",
            "mail_body": f"<div>{mail}</div>",
        }

        response = requests.post(url, data=json.dumps(data))
        print(response.json())
        if response.status_code == 200:
            return Response(
                data={"message": "Mail sent Successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            data={"message": "Try again later"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
