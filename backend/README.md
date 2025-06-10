# Backend API

This is the backend API for the Product Manager application. It provides authentication and product management endpoints.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory with the following variables:
```
DB_HOST=localhost
DB_NAME=data
DB_USER=postgres
DB_PASSWORD=your-password
DB_PORT=5432
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

3. Initialize the database:
```bash
python api1.py
```

4. Run the server:
```bash
python api1.py
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with existing user

### Products
- `GET /products` - Get all products (requires authentication)
- `GET /products/<id>` - Get a specific product
- `POST /products` - Create a new product (requires authentication)
- `PUT /products/<id>` - Update a product
- `DELETE /products/<id>` - Delete a product
- `GET /products/search` - Search products

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Protected endpoints require a valid token in the `Authorization` header:

```
Authorization: Bearer <token>
``` 