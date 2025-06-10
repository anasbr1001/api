# Frontend Next.js Application

This is the frontend application for the Product Manager, built with Next.js and TypeScript.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file in the frontend-next directory with the following variables:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

3. Run the development server:
```bash
npm run dev
```

## Features

- User authentication (login/register)
- Product management (create, read, update, delete)
- Pagination
- Search functionality
- Responsive design

## Project Structure

- `src/app/` - Next.js app router pages
- `src/components/` - Reusable React components
- `src/lib/` - Utility functions and API clients
- `src/app/globals.css` - Global styles

## Authentication

The application uses JWT (JSON Web Tokens) for authentication. The token is stored in localStorage and automatically included in API requests.

## API Integration

The frontend communicates with the backend API through the following endpoints:

- Authentication:
  - `POST /auth/register` - Register a new user
  - `POST /auth/login` - Login with existing user

- Products:
  - `GET /products` - Get all products
  - `GET /products/<id>` - Get a specific product
  - `POST /products` - Create a new product
  - `PUT /products/<id>` - Update a product
  - `DELETE /products/<id>` - Delete a product
  - `GET /products/search` - Search products
