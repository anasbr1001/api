import { useState } from 'react';

export default function ProductForm({ onCreate }) {
  const [product, setProduct] = useState({
    title: '',
    price: 0
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate(product);
    setProduct({ title: '', price: 0 });
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <input
        type="text"
        value={product.title}
        onChange={(e) => setProduct({...product, title: e.target.value})}
        placeholder="Product name"
        required
      />
      <input
        type="number"
        value={product.price}
        onChange={(e) => setProduct({...product, price: parseFloat(e.target.value) || 0})}
        placeholder="Price"
        step="0.01"
        min="0"
        required
      />
      <button type="submit">Add Product</button>
    </form>
  );
}