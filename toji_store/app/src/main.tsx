import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './Header.tsx'
import Footer from './Footer.tsx'
import ProductCarousel from './ProductCarousel.tsx'
import Product from './Product.tsx'

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="grow bg-gray-50 py-12 px-2">
        {children}
      </main>
      <Footer />
    </div>
  )
}

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto">
      <ProductCarousel />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout children={<HomePage />} />} />
        <Route path="/product/:id" element={<Layout children={<Product />} />} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
