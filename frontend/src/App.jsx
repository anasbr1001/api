import { useState, useEffect } from 'react';
import { productApi } from './api/fetch';
import ProductList from "./components/ProductList";
import ProductForm from "./components/ProductForm";
import './App.css';
import './index.css';

export default function App() {
  console.log("App component rendering"); // Check console
  return (
    <div style={{ color: 'white', background: 'black' }}>
      <h1>TEST - If you see this, React is working</h1>
      <p>Basic content check</p>
    </div>
  );
}