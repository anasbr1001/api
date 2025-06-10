import { useState } from 'react';

export default function ProductForm({ onCreate }) {
  const [product, setProduct] = useState({
    title: '',
    price: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const productData = { ...product };
    if (productData.price === '') delete productData.price;
    else productData.price = parseFloat(productData.price);
    onCreate(productData);
    setProduct({ title: '', price: '' });
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
        onChange={(e) => setProduct({...product, price: e.target.value})}
        placeholder="Price (optionnel)"
        step="0.01"
        min="0"
      />
      <button type="submit">Add Product</button>
    </form>
  );
}