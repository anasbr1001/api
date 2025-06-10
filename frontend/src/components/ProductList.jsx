export default function ProductList({ products, onDelete }) {
    return (
      <ul className="product-list">
        {products.map(product => (
          <li key={product.id} className="product-item">
            <span>
              {product.title} - $
              {typeof product.price === 'number' ? product.price.toFixed(2) : 'N/A'}
            </span>
            <button 
              onClick={() => onDelete(product.id)}
              className="delete-btn"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    );
  }