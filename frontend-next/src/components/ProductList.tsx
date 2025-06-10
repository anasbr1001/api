import { Product } from '../lib/api';

interface ProductListProps {
  products: Product[];
  onDelete: (id: string | number) => void;
  onEdit: (product: Product) => void;
  onGetById?: (id: string | number) => void;
}

export default function ProductList({ products, onDelete, onEdit, onGetById }: ProductListProps) {
  return (
    <ul className="product-list">
      {products.map((product, idx) => (
        <li key={product.id ?? idx} className="product-item">
          <span>
            {product.title} - $
            {product.price ? Number(product.price).toFixed(2) : 'N/A'}
          </span>
          <button onClick={() => onEdit(product)}>Edit</button>
          <button 
            onClick={() => onDelete(product.id)}
            className="delete-btn"
          >
            Delete
          </button>
          {onGetById && (
            <button 
              onClick={() => onGetById(product.id)}
              className="view-btn"
            >
              View
            </button>
          )}
        </li>
      ))}
    </ul>
  );
} 