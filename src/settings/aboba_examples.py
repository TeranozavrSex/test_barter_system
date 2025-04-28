from django.http import HttpResponse, JsonResponse
from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from settings.aboba_swagger import aboba_swagger


@aboba_swagger(
    http_methods=["GET"],
    summary="Basic example with simple response",
    description="This is a basic example showing a simple string response",
    responses={
        "200": "Simple string response"
    },
    tags=["examples"],
)
def basic_example(request):
    return HttpResponse("Simple string response", status=200)


@aboba_swagger(
    http_methods=["GET"],
    summary="Example with JSON response",
    description="This example returns a simple JSON object",
    responses={
        "200": {"response": {"message": "Success", "data": 123}}
    },
    tags=["examples"],
)
def json_example(request):
    return JsonResponse({"message": "Success", "data": 123}, status=200)


@aboba_swagger(
    http_methods=["GET"],
    summary="Example with multiple response types",
    description="This example shows how to document multiple possible response formats for the same status code",
    responses={
        "200": {
            "String Response": "Simple string success",
            "JSON Response": {"status": "success", "code": 200}
        }
    },
    tags=["examples"],
)
def multiple_response_types(request):
    import random
    if random.choice([True, False]):
        return HttpResponse("Simple string success", status=200)
    else:
        return JsonResponse({"status": "success", "code": 200}, status=200)


@aboba_swagger(
    http_methods=["POST"],
    summary="Example with query parameters and body",
    description="This example shows how to document query parameters and request body",
    query_params={
        "filter": str,
        "limit": int,
        "include_deleted": bool,
    },
    body_params={
        "name": str,
        "age": int,
        "is_active": bool,
        "metadata": {
            "tags": [str],
            "created_at": "datetime",
            "priority": int,
        }
    },
    responses={
        "200": {"id": 123, "name": "Test User", "created": True},
        "400": {
            "Missing Field": {"error": "Field 'name' is required"},
            "Invalid Value": {"error": "Field 'age' must be positive"}
        }
    },
    tags=["examples"],
)
def complex_params_example(request):
    return JsonResponse({"id": 123, "name": "Test User", "created": True}, status=200)


@aboba_swagger(
    http_methods=["GET"],
    summary="Example with nested arrays in response",
    description="This example shows how to document responses with nested arrays",
    responses={
        "200": {"response": {
            "users": [
                {
                    "id": 1,
                    "name": "User 1",
                    "roles": ["admin", "editor"],
                    "permissions": [
                        {"resource": "articles", "actions": ["read", "write"]},
                        {"resource": "comments", "actions": ["read"]}
                    ]
                }
            ],
            "meta": {
                "total": 100,
                "page": 1,
                "limit": 10
            }
        }}
    },
    tags=["examples"],
)
def nested_arrays_example(request):
    data = {
        "users": [
            {
                "id": 1,
                "name": "User 1",
                "roles": ["admin", "editor"],
                "permissions": [
                    {"resource": "articles", "actions": ["read", "write"]},
                    {"resource": "comments", "actions": ["read"]}
                ]
            }
        ],
        "meta": {
            "total": 100,
            "page": 1,
            "limit": 10
        }
    }
    return JsonResponse(data, status=200)


@aboba_swagger(
    http_methods=["POST"],
    summary="Example with custom serializer fields",
    description="This example shows how to use custom serializer fields in responses",
    body_params={
        "date": serializers.DateField(),
        "time": serializers.TimeField(),
        "datetime": serializers.DateTimeField(),
        "email": serializers.EmailField(),
        "url": serializers.URLField(),
        "decimal": serializers.DecimalField(max_digits=10, decimal_places=2),
    },
    responses={
        "200": {
            "String Response": "Data saved successfully",
            "Object Response": {
                "id": 123,
                "created_at": "2023-07-25T12:34:56Z",
                "updated_at": "2023-07-25T12:34:56Z",
                "amount": "123.45",
            }
        }
    },
    tags=["examples"],
)
def custom_serializer_fields(request):
    from datetime import datetime
    from decimal import Decimal
    
    return JsonResponse({
        "id": 123,
        "created_at": datetime.now().isoformat(),
        "updated_at": "2023-07-25T12:34:56Z",
        "amount": str(Decimal("123.45")),
    }, status=200)


@aboba_swagger(
    http_methods=["GET"],
    summary="Example with auth required",
    description="This example shows how to require authentication",
    responses={
        "200": "You are authenticated",
        "401": "Authentication required"
    },
    need_auth=True,
    tags=["examples"],
)
def auth_required_example(request):
    return HttpResponse("You are authenticated", status=200)


@aboba_swagger(
    http_methods=["POST"],
    summary="Better example with custom serializer",
    description="This example demonstrates how to properly use serializers with the decorator",
    body_params={
        "name": str,
        "email": str,
        "age": int,
        "is_active": bool,
    },
    responses={
        "201": {
            "Created User": {
                "id": 42,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2023-08-15T14:30:45Z",
                "profile": {
                    "age": 30,
                    "is_active": True
                }
            }
        },
        "400": {
            "Invalid Email": {
                "error": "Invalid email format",
                "field": "email",
                "code": "invalid_format"
            },
            "Missing Fields": {
                "error": "Required fields missing",
                "fields": ["name", "email"],
                "code": "required_fields"
            }
        }
    },
    tags=["examples"],
)
def better_serializer_example(request):
    """
    This example demonstrates a better approach to defining complex responses
    without directly using serializer fields in the responses dictionary.
    """
    from datetime import datetime
    
    # Normally we would process the request.data here
    # For this example, we just return a predefined response
    return JsonResponse({
        "id": 42,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": datetime.now().isoformat(),
        "profile": {
            "age": 30,
            "is_active": True
        }
    }, status=201)


# Example serializers
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    is_active = serializers.BooleanField(default=True)


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, write_only=True)


# Paginator example
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Override to make the response structure consistent"""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


# Mock data generation
def generate_mock_users(count=20):
    """Generate a list of mock users"""
    users = []
    for i in range(1, count + 1):
        users.append({
            "id": i,
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "is_active": i % 3 != 0,  # Every third user is inactive
        })
    return users


def generate_mock_products(count=30):
    """Generate a list of mock products"""
    products = []
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    for i in range(1, count + 1):
        category = categories[i % len(categories)]
        products.append({
            "id": i,
            "name": f"Product {i}",
            "price": f"{(i * 9.99):.2f}",
            "description": f"Description of product {i} in {category} category",
            "category": category,
            "is_available": i % 4 != 0,  # Every fourth product is unavailable
        })
    return products


# Create mock data
MOCK_USERS = generate_mock_users()
MOCK_PRODUCTS = generate_mock_products()


# Review serializer for nested data
class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(max_length=100)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    is_available = serializers.BooleanField(default=True)


class UserViewSet(viewsets.ViewSet):
    """
    A viewset for managing users with aboba_swagger decorators.
    """
    pagination_class = StandardResultsSetPagination
    
    @aboba_swagger(
        summary="List all users",
        description="Returns a paginated list of all users in the system",
        query_params={
            "page": int,
            "page_size": int,
            "search": str,
            "active_only": bool,
        },
        responses={
            "200": {
                "Success": {
                    "count": 20,
                    "next": "http://example.com/api/users/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "username": "user1",
                            "email": "user1@example.com",
                            "is_active": True,
                        },
                        # More users would be listed here
                    ]
                }
            }
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    def list(self, request):
        """
        Get a paginated list of all users.
        """
        # Filter mock data based on query parameters
        users = MOCK_USERS.copy()
        active_only = request.query_params.get('active_only')
        search = request.query_params.get('search')
        
        if active_only and active_only.lower() == 'true':
            users = [user for user in users if user['is_active']]
            
        if search:
            users = [user for user in users if search.lower() in user['username'].lower() 
                     or search.lower() in user['email'].lower()]
        
        # Use serializer to validate and format the data
        serializer = UserSerializer(data=users, many=True)
        serializer.is_valid()  # We know our mock data is valid
        
        # Use the paginator
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(serializer.data, request)
        
        return paginator.get_paginated_response(paginated_users)

    @aboba_swagger(
        summary="Retrieve a specific user",
        description="Returns details for a specific user by ID",
        responses={
            "200": {
                "User Found": {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    "is_active": True,
                }
            },
            "404": {"Not Found": {"detail": "User not found"}}
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    def retrieve(self, request, pk=None):
        """
        Get details for a specific user.
        """
        try:
            pk = int(pk)
            user = next((user for user in MOCK_USERS if user["id"] == pk), None)
            if user:
                # Use serializer to validate and format the data
                serializer = UserSerializer(data=user)
                serializer.is_valid()  # We know our mock data is valid
                return Response(serializer.data)
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Create a new user",
        description="Creates a new user in the system",
        body_params={
            "username": str,
            "email": str,
            "password": str,
        },
        responses={
            "201": {
                "User Created": {
                    "id": 21,
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "is_active": True,
                }
            },
            "400": {
                "Validation Error": {
                    "username": ["This field is required."],
                    "email": ["Enter a valid email address."],
                }
            }
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    def create(self, request):
        """
        Create a new user.
        """
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Simulate creating a new user
            new_user_data = {
                "id": len(MOCK_USERS) + 1,
                "username": serializer.validated_data["username"],
                "email": serializer.validated_data["email"],
                "is_active": True,
            }
            # Use UserSerializer for the response to ensure consistency
            response_serializer = UserSerializer(data=new_user_data)
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Update a user",
        description="Updates an existing user in the system",
        body_params={
            "username": str,
            "email": str,
            "is_active": bool,
        },
        responses={
            "200": {
                "User Updated": {
                    "id": 1,
                    "username": "user1_updated",
                    "email": "user1@example.com",
                    "is_active": True,
                }
            },
            "404": {"Not Found": {"detail": "User not found"}}
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    def update(self, request, pk=None):
        """
        Update a user.
        """
        try:
            pk = int(pk)
            user = next((user for user in MOCK_USERS if user["id"] == pk), None)
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
            # Use serializer to validate incoming data
            serializer = UserSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            # Update the user data
            updated_user = {
                "id": user["id"],
                "username": request.data.get("username", user["username"]),
                "email": request.data.get("email", user["email"]),
                "is_active": request.data.get("is_active", user["is_active"]),
            }
            
            # Use serializer for response
            response_serializer = UserSerializer(data=updated_user)
            response_serializer.is_valid()
            return Response(response_serializer.data)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Delete a user",
        description="Deletes a user from the system",
        responses={
            "204": "User deleted successfully",
            "404": {"Not Found": {"detail": "User not found"}}
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    def destroy(self, request, pk=None):
        """
        Delete a user.
        """
        try:
            pk = int(pk)
            user = next((user for user in MOCK_USERS if user["id"] == pk), None)
            if user:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        http_methods=["POST"],
        summary="Activate a user account",
        description="Activates a deactivated user account",
        responses={
            "200": {"User Activated": {"detail": "User activated successfully"}},
            "404": {"Not Found": {"detail": "User not found"}}
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Activate a user account.
        """
        try:
            pk = int(pk)
            user = next((user for user in MOCK_USERS if user["id"] == pk), None)
            if user:
                if not user["is_active"]:
                    return Response({"detail": "User activated successfully"})
                return Response({"detail": "User is already active"})
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        http_methods=["POST"],
        summary="Reset user password",
        description="Sends a password reset email to the user",
        body_params={"email": str},
        responses={
            "200": {"Success": {"detail": "Password reset email sent"}},
            "404": {"Not Found": {"detail": "User with this email not found"}}
        },
        is_drf=True,
        tags=["drf_example_users"],
    )
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        """
        Reset a user's password.
        """
        email = request.data.get("email")
        user = next((user for user in MOCK_USERS if user["email"] == email), None)
        if user:
            return Response({"detail": "Password reset email sent"})
        return Response(
            {"detail": "User with this email not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )


class ProductViewSet(viewsets.ViewSet):
    """
    A viewset for managing products with aboba_swagger decorators.
    """
    pagination_class = StandardResultsSetPagination
    
    @aboba_swagger(
        summary="List all products",
        description="Returns a paginated list of all products in the system",
        query_params={
            "page": int,
            "page_size": int,
            "category": str,
            "min_price": float,
            "max_price": float,
            "available_only": bool,
        },
        responses={
            "200": {
                "Product List": {
                    "count": 30,
                    "next": "http://example.com/api/products/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Product 1",
                            "price": "9.99",
                            "description": "Description of product 1 in Electronics category",
                            "category": "Electronics",
                            "is_available": True,
                        },
                        # More products would be listed here
                    ]
                }
            }
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    def list(self, request):
        """
        Get a paginated list of all products.
        """
        # Filter products based on query parameters
        products = MOCK_PRODUCTS.copy()
        
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        available_only = request.query_params.get('available_only')
        
        if category:
            products = [p for p in products if p['category'].lower() == category.lower()]
            
        if min_price:
            try:
                min_price = float(min_price)
                products = [p for p in products if float(p['price']) >= min_price]
            except ValueError:
                pass
                
        if max_price:
            try:
                max_price = float(max_price)
                products = [p for p in products if float(p['price']) <= max_price]
            except ValueError:
                pass
                
        if available_only and available_only.lower() == 'true':
            products = [p for p in products if p['is_available']]
        
        # Use serializer to validate and format the data
        serializer = ProductSerializer(data=products, many=True)
        serializer.is_valid()  # We know our mock data is valid
        
        # Use the paginator
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(serializer.data, request)
        
        return paginator.get_paginated_response(paginated_products)

    @aboba_swagger(
        summary="Retrieve a specific product",
        description="Returns details for a specific product by ID",
        responses={
            "200": {
                "Product Found": {
                    "id": 1,
                    "name": "Product 1",
                    "price": "9.99",
                    "description": "Description of product 1 in Electronics category",
                    "category": "Electronics",
                    "is_available": True,
                }
            },
            "404": {"Not Found": {"detail": "Product not found"}}
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    def retrieve(self, request, pk=None):
        """
        Get details for a specific product.
        """
        try:
            pk = int(pk)
            product = next((p for p in MOCK_PRODUCTS if p["id"] == pk), None)
            if product:
                # Use serializer to validate and format the data
                serializer = ProductSerializer(data=product)
                serializer.is_valid()
                return Response(serializer.data)
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        http_methods=["GET"],
        summary="Get featured products",
        description="Returns a list of featured products",
        responses={
            "200": {
                "Featured Products": [
                    {
                        "id": 1,
                        "name": "Product 1",
                        "price": "9.99",
                        "description": "Description of product 1 in Electronics category",
                        "category": "Electronics",
                        "is_available": True,
                    },
                    {
                        "id": 5,
                        "name": "Product 5",
                        "price": "49.95",
                        "description": "Description of product 5 in Electronics category",
                        "category": "Electronics",
                        "is_available": True,
                    }
                ]
            }
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    @action(detail=False, methods=["get"])
    def featured(self, request):
        """
        Get featured products.
        """
        # For this example, we'll just pick a few products as featured
        featured_products = [p for p in MOCK_PRODUCTS if p["id"] in [1, 5, 10, 15, 20]]
        
        # Use serializer to format the data
        serializer = ProductSerializer(data=featured_products, many=True)
        serializer.is_valid()  # We know our mock data is valid
        
        return Response(serializer.data)

    @aboba_swagger(
        http_methods=["GET"],
        summary="Get product reviews",
        description="Returns all reviews for a specific product",
        responses={
            "200": {
                "Product Reviews": [
                    {
                        "id": 1,
                        "user": "user1",
                        "rating": 5,
                        "comment": "Great product!",
                        "created_at": "2023-08-15T14:30:45Z",
                    },
                    {
                        "id": 2,
                        "user": "user2",
                        "rating": 4,
                        "comment": "Good product",
                        "created_at": "2023-08-16T09:15:20Z",
                    }
                ]
            },
            "404": {"Not Found": {"detail": "Product not found"}}
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """
        Get reviews for a specific product.
        """
        try:
            pk = int(pk)
            product = next((p for p in MOCK_PRODUCTS if p["id"] == pk), None)
            if not product:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
                
            # Generate mock reviews based on product ID
            from datetime import datetime, timedelta
            
            base_date = datetime.now()
            
            mock_reviews = [
                {
                    "id": 1,
                    "user": f"user{pk * 2 - 1}",
                    "rating": min(5, (pk % 5) + 3),
                    "comment": "Great product! Would buy again.",
                    "created_at": (base_date - timedelta(days=5)).isoformat()
                },
                {
                    "id": 2,
                    "user": f"user{pk * 2}",
                    "rating": max(1, 5 - (pk % 3)),
                    "comment": "Good value for money.",
                    "created_at": (base_date - timedelta(days=2)).isoformat()
                }
            ]
            
            # Add a third review for some products
            if pk % 3 == 0:
                mock_reviews.append({
                    "id": 3,
                    "user": f"user{pk + 5}",
                    "rating": 3,
                    "comment": "Average product, nothing special.",
                    "created_at": (base_date - timedelta(days=1)).isoformat()
                })
                
            # Use ReviewSerializer to validate and format the data
            serializer = ReviewSerializer(data=mock_reviews, many=True)
            serializer.is_valid()
            
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        http_methods=["POST"],
        summary="Add product review",
        description="Adds a new review for a specific product",
        body_params={
            "rating": int,
            "comment": str,
        },
        responses={
            "201": {
                "Review Added": {
                    "id": 3,
                    "user": "current_user",
                    "rating": 4,
                    "comment": "Very good product",
                    "created_at": "2023-08-15T14:30:45Z",
                }
            },
            "400": {"Validation Error": {"rating": ["Rating must be between 1 and 5."]}},
            "404": {"Not Found": {"detail": "Product not found"}}
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    @action(detail=True, methods=["post"])
    def add_review(self, request, pk=None):
        """
        Add a review to a specific product.
        """
        try:
            pk = int(pk)
            product = next((p for p in MOCK_PRODUCTS if p["id"] == pk), None)
            if not product:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Use ReviewSerializer to validate incoming data
            serializer = ReviewSerializer(data={
                "id": 3,  # This would normally be assigned by the database
                "user": "current_user",  # This would normally come from the authentication
                "rating": request.data.get("rating"),
                "comment": request.data.get("comment"),
                "created_at": datetime.now().isoformat()
            })
            
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except (ValueError, TypeError):
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Create a new product",
        description="Creates a new product in the system",
        body_params={
            "name": str,
            "price": "decimal",
            "description": str,
            "category": str,
            "is_available": bool,
        },
        responses={
            "201": {
                "Product Created": {
                    "id": 31,
                    "name": "New Product",
                    "price": "99.99",
                    "description": "A brand new product",
                    "category": "Electronics",
                    "is_available": True,
                }
            },
            "400": {
                "Validation Error": {
                    "name": ["This field is required."],
                    "price": ["A valid number is required."],
                }
            }
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    def create(self, request):
        """
        Create a new product.
        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Simulate creating a new product
            new_product_data = {
                "id": len(MOCK_PRODUCTS) + 1,
                **serializer.validated_data
            }
            
            # Create a response using the same serializer
            response_serializer = ProductSerializer(data=new_product_data)
            response_serializer.is_valid()
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Update a product",
        description="Updates an existing product in the system",
        body_params={
            "name": str,
            "price": "decimal",
            "description": str,
            "category": str,
            "is_available": bool,
        },
        responses={
            "200": {
                "Product Updated": {
                    "id": 1,
                    "name": "Updated Product 1",
                    "price": "19.99",
                    "description": "Updated description",
                    "category": "Electronics",
                    "is_available": True,
                }
            },
            "404": {"Not Found": {"detail": "Product not found"}}
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    def update(self, request, pk=None):
        """
        Update a product.
        """
        try:
            pk = int(pk)
            product = next((p for p in MOCK_PRODUCTS if p["id"] == pk), None)
            if not product:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
                
            # Validate incoming data with ProductSerializer
            serializer = ProductSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            # Update product with validated data
            updated_product = {
                "id": product["id"],
                "name": request.data.get("name", product["name"]),
                "price": request.data.get("price", product["price"]),
                "description": request.data.get("description", product["description"]),
                "category": request.data.get("category", product["category"]),
                "is_available": request.data.get("is_available", product["is_available"]),
            }
            
            # Use serializer for response formatting
            response_serializer = ProductSerializer(data=updated_product)
            response_serializer.is_valid()
            
            return Response(response_serializer.data)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)

    @aboba_swagger(
        summary="Delete a product",
        description="Deletes a product from the system",
        responses={
            "204": "Product deleted successfully",
            "404": {"Not Found": {"detail": "Product not found"}}
        },
        is_drf=True,
        tags=["drf_example_products"],
    )
    def destroy(self, request, pk=None):
        """
        Delete a product.
        """
        try:
            pk = int(pk)
            product = next((p for p in MOCK_PRODUCTS if p["id"] == pk), None)
            if product:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST) 