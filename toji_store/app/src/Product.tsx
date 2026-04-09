import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShoppingCart, Home, Store, Truck } from 'lucide-react'
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
  const [isExpandedSynopsis, setIsExpandedSynopsis] = useState(false)

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


    <div className="bg-gray-50">
      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-2 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sección de Imagen - Izquierda */}
          <div className="lg:col-span-1 flex flex-col items-center gap-4">
            {/* Breadcrumb */}
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-2 px-5 py-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors text-gray-800 font-medium text-sm"
            >
              <Home className="w-5 h-5" />
              <span>Catálogo</span>
              <span className="text-gray-600">&gt;</span>
              <span className="font-semibold">{product.name}</span>
            </button>
            
            {/* Imagen */}
            <div className="bg-white rounded-3xl shadow-lg p-6 w-full flex items-center justify-center border-2 border-gray-200">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-auto object-contain"
              />
            </div>
          </div>

          {/* Sección de Información - Centro */}
          <div className="lg:col-span-1 flex flex-col">
            {/* Header del Producto */}
            <div className="mb-6">
              <h1 className="text-5xl font-bold text-gray-900 mb-6">
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
                      className="font-medium bg-gray-200 text-gray-800"
                    >
                      {author.name}
                    </Chip>
                  ))}
                </div>
              )}
            </div>

            {/* Sección de Sinopsis */}
            {product.synopsis && (
              <div className="mb-6">
                <Card className={`shadow-sm overflow-hidden relative ${
                  isExpandedSynopsis ? '' : ''
                }`}>
                  <div className={`p-6 ${
                    isExpandedSynopsis ? '' : 'max-h-48'
                  }`}>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap text-sm">
                      {product.synopsis}
                    </p>
                  </div>
                  {!isExpandedSynopsis && (
                    <div className="absolute inset-x-0 bottom-0 h-20 bg-linear-to-t from-white to-transparent pointer-events-none" />
                  )}
                </Card>
                <button
                  onClick={() => setIsExpandedSynopsis(!isExpandedSynopsis)}
                  className="mt-2 px-6 py-2 bg-black text-white font-semibold rounded-full hover:bg-gray-800 transition-colors text-sm"
                >
                  {isExpandedSynopsis ? 'Leer menos' : 'Leer más'}
                </button>
              </div>
            )}

            {/* Descripción adicional */}
            {product.description && (
              <div className="mb-6">
                <p className="text-gray-600 leading-relaxed text-sm line-clamp-6">
                  {product.description}
                </p>
              </div>
            )}


          </div>

          {/* Sidebar Derecha - Precio y CTA */}
          <div className="lg:col-span-1 flex flex-col h-fit border-2 border-black rounded-3xl p-8">
            {/* Precio */}
            <div className="text-center mb-6">
              <p className="text-4xl font-bold text-black">
                {product.price.toFixed(2)} €
              </p>
            </div>

            {/* Botón Añadir al Carrito */}
            <button className="w-full bg-black text-white font-bold py-3 rounded-full hover:bg-gray-800 transition-colors flex items-center justify-center gap-2 mb-6">
              <ShoppingCart className="w-5 h-5" />
            </button>

            {/* Info de Disponibilidad */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="shrink-0 w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Store className="w-6 h-6 text-gray-700" />
                </div>
                <p className="text-sm text-gray-700">
                  Consulta la disponibilidad en nuestras librerías. <span className="font-bold">Recógelo gratis</span>
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="shrink-0 w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Truck className="w-6 h-6 text-gray-700" />
                </div>
                <p className="text-sm text-gray-700">
                  <span className="font-bold">Recibelo mañana</span> jueves 9 de abril.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>


  )
}

export default Product
