import { useEffect, useState } from 'react'
import ProductCard from './ProductCard.tsx'

interface Product {
  id: number
  name: string
  price: number
  image_url: string
}

function ProductCarousel() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true)
        const url = '/api/toji/products'

        console.log('1️⃣ Fetching from:', url)
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        })
        
        console.log('2️⃣ Response status:', response.status)
        console.log('2️⃣ Response headers:', {
          'content-type': response.headers.get('content-type'),
          'content-length': response.headers.get('content-length'),
        })

        const content = await response.text()
        console.log('3️⃣ Response text (primeros 1000 chars):', content.substring(0, 1000))

        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`)
        }

        let data
        try {
          data = JSON.parse(content)
          console.log('4️⃣ Data parseado:', JSON.stringify(data, null, 2))
        } catch (e) {
          console.error('❌ No es JSON válido')
          throw new Error('Response no es JSON válido')
        }
        
        console.log('5️⃣ data.success:', data.success)
        console.log('5️⃣ data.products type:', Array.isArray(data.products) ? 'Array' : typeof data.products)
        console.log('5️⃣ data.products length:', data.products?.length || 0)
        
        if (data.success && Array.isArray(data.products)) {
          console.log('✅ Productos cargados:', data.products.length)
          setProducts(data.products)
        } else {
          console.warn('❌ Respuesta incompleta:', data)
          throw new Error(`No se cargaron productos. Success: ${data.success}, Products: ${Array.isArray(data.products) ? 'OK' : 'No es array'}`)
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Error desconocido'
        setError(errorMsg)
        console.error('❌ Error final:', errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-lg font-semibold text-gray-600">Cargando productos...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-lg font-semibold text-red-600">Error: {error}</div>
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-lg font-semibold text-gray-600">No hay productos disponibles</div>
      </div>
    )
  }

  const itemsPerPage = 4
  const totalPages = Math.ceil(products.length / itemsPerPage)
  const visibleProducts = products.slice(currentIndex * itemsPerPage, (currentIndex + 1) * itemsPerPage)

  return (
    <div className="w-full">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Nuestros Libros</h2>
      
      <div className="relative">
        {/* Carrusel */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {visibleProducts.map((product) => (
            <ProductCard
              key={product.id}
              id={product.id}
              nombre={product.name}
              precio={product.price}
              imagen={product.image_url}
            />
          ))}
        </div>

        {/* Botones de navegación */}
        <div className="flex justify-center items-center gap-8 mb-8">
          <button
            onClick={() => setCurrentIndex((prev) => (prev - 1 + totalPages) % totalPages)}
            className="bg-black text-white rounded-full p-3 hover:bg-gray-800 transition-colors"
            aria-label="Anterior"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Paginación */}
          <div className="flex justify-center gap-2">
            {Array.from({ length: totalPages }).map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentIndex ? 'bg-black' : 'bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Página ${index + 1}`}
              />
            ))}
          </div>

          <button
            onClick={() => setCurrentIndex((prev) => (prev + 1) % totalPages)}
            className="bg-black text-white rounded-full p-3 hover:bg-gray-800 transition-colors"
            aria-label="Siguiente"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProductCarousel