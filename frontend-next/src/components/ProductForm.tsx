import { useState, useEffect } from 'react';
import { Product } from '../lib/api';

interface ProductFormProps {
  onCreate: (product: Omit<Product, 'id'> | Product) => void;
  initialProduct?: Product;
  onCancel?: () => void;
  isEdit?: boolean;
}

export default function ProductForm({ onCreate, initialProduct, onCancel, isEdit }: ProductFormProps) {
  const [product, setProduct] = useState({
    title: initialProduct?.title || '',
    price: initialProduct?.price?.toString() || '',
    description: initialProduct?.description || ''
  });

  useEffect(() => {
    if (initialProduct) {
      setProduct({
        title: initialProduct.title,
        price: initialProduct.price?.toString() || '',
        description: initialProduct.description || ''
      });
    }
  }, [initialProduct]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const productData: any = { 
      title: product.title,
      description: product.description || undefined
    };
    if (product.price !== '') productData.price = parseFloat(product.price);
    if (isEdit && initialProduct) productData.id = initialProduct.id;
    onCreate(productData);
    setProduct({ title: '', price: '', description: '' });
    if (isEdit && onCancel) onCancel();
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <input
        type="text"
        value={product.title}
        onChange={(e) => setProduct({ ...product, title: e.target.value })}
        placeholder="Product name"
        required
      />
      <input
        type="number"
        value={product.price}
        onChange={(e) => setProduct({ ...product, price: e.target.value })}
        placeholder="Price (optional)"
        step="0.01"
        min="0"
      />
      <textarea
        value={product.description}
        onChange={(e) => setProduct({ ...product, description: e.target.value })}
        placeholder="Description (optional)"
        rows={3}
      />
      <button type="submit">{isEdit ? 'Update Product' : 'Add Product'}</button>
      {isEdit && onCancel && (
        <button type="button" onClick={onCancel}>Cancel</button>
      )}
    </form>
  );
} 