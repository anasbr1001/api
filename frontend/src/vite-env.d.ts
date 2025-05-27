/// <reference types="vite/client" />

interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
  
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_API_USER: string;
    readonly VITE_API_PASS: string;
    // Add other environment variables here as needed
  }