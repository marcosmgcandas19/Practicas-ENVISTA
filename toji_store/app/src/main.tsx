import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Header from './Header.tsx'
import Footer from './Footer.tsx'
import ProductCard from './ProductCard.tsx'

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow bg-gray-50 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          
          {/* Carrusel de libros */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

            <ProductCard
              nombre="Hamlet"
              precio={24.99}
              imagen="https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop"
            />
            <ProductCard
              nombre="Don Quijote"
              precio={29.99}
              imagen="https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop"
            />
            <ProductCard
              nombre="1984"
              precio={18.99}
              imagen="https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop"
            />
            <ProductCard
              nombre="Orgullo y Prejuicio"
              precio={22.50}
              imagen="https://images.unsplash.com/photo-1507842217343-583f20270319?w=300&h=400&fit=crop"
            />

          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
