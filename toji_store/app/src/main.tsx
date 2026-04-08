import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Header from './Header.tsx'
import Footer from './Footer.tsx'
import ProductCarousel from './ProductCarousel.tsx'

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow bg-gray-50 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <ProductCarousel />
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
