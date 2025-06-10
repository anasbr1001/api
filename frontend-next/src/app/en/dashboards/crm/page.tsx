'use client';

import { useState, useEffect } from 'react';
import { productApi } from '@/lib/api';
import { Product } from '@/lib/types';
import ProductList from '@/components/ProductList';
import ProductForm from '@/components/ProductForm';
import AuthForm from '@/components/AuthForm';
import { useAuth } from '@/lib/auth';
import '@/app/globals.css';

export default function CRMDashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [showRegister, setShowRegister] = useState(false);
  const itemsPerPage = 10;
  const { isAuthenticated, user, logout } = useAuth();

  const fetchProducts = async (page: number = 1) => {
    setLoading(true);
    try {
      const data = await productApi.getAll(page, itemsPerPage);
      setProducts(data.products);
      setTotalPages(data.total_pages);
      setTotalItems(data.total_items);
      setCurrentPage(data.page);
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError('Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchProducts(currentPage);
    }
  }, [currentPage, isAuthenticated]);

  const handleCreate = async (product: Omit<Product, 'id'>) => {
    try {
      const newProduct = await productApi.create(product);
      setProducts([...products, newProduct]);
      fetchProducts(currentPage);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Unknown error');
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await productApi.delete(id);
      setProducts(products.filter(p => p.id !== id));
      fetchProducts(currentPage);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Unknown error');
    }
  };

  const handleGetById = async (id: string | number) => {
    try {
      const product = await productApi.getById(id);
      setSelectedProduct(product);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError('Unknown error');
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  if (!isAuthenticated) {
    return (
      <div className="app-container">
        <h1>CRM Dashboard</h1>
        <AuthForm mode={showRegister ? 'register' : 'login'} />
        <div className="auth-switch">
          <button onClick={() => setShowRegister(!showRegister)}>
            {showRegister ? 'Already have an account? Login' : 'Need an account? Register'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="header">
        <h1>CRM Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.username}!</span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </div>
        <ProductForm onCreate={handleCreate} />
      {selectedProduct && (
        <div className="product-details">
          <h2>Product Details</h2>
          <p><strong>Title:</strong> {selectedProduct.title}</p>
          <p><strong>Price:</strong> ${selectedProduct.price ? Number(selectedProduct.price).toFixed(2) : 'N/A'}</p>
          {selectedProduct.description && (
            <p><strong>Description:</strong> {selectedProduct.description}</p>
          )}
          <button onClick={() => setSelectedProduct(null)}>Close</button>
        </div>
      )}
      {products.length === 0 ? (
        <div>No products found.</div>
      ) : (
        <>
          <ProductList 
            products={products} 
            onDelete={handleDelete} 
            onEdit={() => {}} 
            onGetById={handleGetById}
          />
          <div className="pagination">
            <button 
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <span>
              Page {currentPage} of {totalPages} ({totalItems} items)
            </span>
            <button 
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}