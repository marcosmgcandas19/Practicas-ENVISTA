import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShoppingCart } from 'lucide-react'

interface Author {
  id: number
  name: string
}

interface ProductData {
  id: number
  name: string
  price: number
  description: string
  synopsis: string
  authors: Author[]
  image_url: string
  website_published: boolean
}

interface ApiResponse {
  success: boolean
  product?: ProductData
  error?: string
}

function Product() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [product, setProduct] = useState<ProductData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    setLoading(true)
    setError(null)

    fetch(`/api/toji/products/${id}`)
      .then((response) => {
        console.log('Response status:', response.status)
        console.log('Response headers:', response.headers.get('content-type'))
        if (!response.ok) {
          return response.text().then((text) => {
            console.error('Response body:', text)
            throw new Error(`Error HTTP ${response.status}: ${text || response.statusText}`)
          })
        }
        return response.json()
      })
      .then((data: ApiResponse) => {
        console.log('API Response:', data)
        if (data.success && data.product) {
          setProduct(data.product)
        } else {
          setError(data.error || 'Producto no encontrado')
        }
      })
      .catch((error: Error) => {
        console.error('Fetch error:', error)
        setError(error.message || 'Error al cargar el producto')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
          <p className="mt-4 text-gray-600">Cargando producto...</p>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-6">{error || 'Producto no encontrado'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="w-5 h-5" />
            Volver a la tienda
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con botón volver */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-700 hover:text-black transition-colors font-medium"
          >
            <ArrowLeft className="w-5 h-5" />
            Volver
          </button>
        </div>
      </div>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {/* Sección de Imagen */}
          <div className="flex items-center justify-center">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full aspect-square flex items-center justify-center border-2 border-black">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-contain"
              />
            </div>
          </div>

          {/* Sección de Información */}
          <div className="flex flex-col justify-start">
            {/* Header del Producto */}
            <div className="mb-8">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                {product.name}
              </h1>

              {/* Autores como Chips */}
              {product.authors.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {product.authors.map((author) => (
                    <span
                      key={author.id}
                      className="inline-block px-4 py-2 bg-gray-200 text-gray-800 rounded-full text-sm font-medium border border-gray-300"
                    >
                      {author.name}
                    </span>
                  ))}
                </div>
              )}

              {/* Precio */}
              <div className="text-3xl font-bold text-black mb-4">
                {product.price.toFixed(2)} €
              </div>
            </div>

            {/* Sección de Sinopsis */}
            {product.synopsis && (
              <div className="bg-white rounded-2xl shadow-lg p-6 mb-8 border-2 border-gray-200">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Sinopsis</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {product.synopsis}
                </p>
              </div>
            )}

            {/* Descripción adicional */}
            {product.description && (
              <div className="bg-gray-100 rounded-lg p-4 mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Descripción
                </h3>
                <p className="text-gray-700 leading-relaxed line-clamp-4">
                  {product.description}
                </p>
              </div>
            )}

            {/* Botones de Acción */}
            <div className="flex flex-col sm:flex-row gap-4 mt-auto">
              <button className="flex-1 bg-black text-white font-bold py-4 rounded-lg hover:bg-gray-800 transition-colors flex items-center justify-center gap-2">
                <ShoppingCart className="w-6 h-6" />
                Añadir al carrito
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-8 py-4 border-2 border-black text-black font-bold rounded-lg hover:bg-gray-100 transition-colors"
              >
                Continuar comprando
              </button>
            </div>

            {/* Información adicional */}
            <div className="mt-8 pt-8 border-t border-gray-300">
              <p className="text-sm text-gray-600">
                ✓ Envío disponible en España
              </p>
              <p className="text-sm text-gray-600">
                ✓ Garantía de satisfacción
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Product
