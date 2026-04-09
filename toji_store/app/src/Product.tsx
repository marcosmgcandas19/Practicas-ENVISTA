import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShoppingCart } from 'lucide-react'
import { Chip, Card } from '@heroui/react'

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

    fetch(`/api/toji/products/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    })
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
      .then((data: any) => {
        console.log('API Response:', data)
        // Con type='json' en Odoo, la respuesta viene envuelta en jsonrpc
        const result = data.result || data
        if (result.success && result.product) {
          setProduct(result.product)
        } else {
          setError(result.error || 'Producto no encontrado')
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

              {/* Autores como Chips de HeroUI */}
              {product.authors.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {product.authors.map((author) => (
                    <Chip
                      key={author.id}
                      variant="soft"
                      size="lg"
                      className="font-medium"
                    >
                      {author.name}
                    </Chip>
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
              <Card className="mb-8 shadow-lg">
                <div className="p-6 gap-4">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Sinopsis</h2>
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {product.synopsis}
                  </p>
                </div>
              </Card>
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
