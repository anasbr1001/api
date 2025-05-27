import { useState, useEffect } from 'react';
import { productApi } from './api/fetch';
import ProductList from "./components/ProductList";
import ProductForm from "./components/ProductForm";
import './App.css';

export default function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const data = await productApi.getAll();
      setProducts(data.products);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreate = async (product) => {
    try {
      const newProduct = await productApi.create(product);
      setProducts([...products, newProduct]);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    try {
      await productApi.delete(id);
      setProducts(products.filter(p => p.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app-container">
      <h1>Product Manager</h1>
      <ProductForm onCreate={handleCreate} />
      <ProductList products={products} onDelete={handleDelete} />
    </div>
  );
}