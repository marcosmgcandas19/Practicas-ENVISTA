import { Link } from 'react-router-dom'

interface ProductCardProps {
  id?: number
  nombre: string
  precio: number
  imagen: string
}

function ProductCard({ id, nombre, precio, imagen }: ProductCardProps) {
  const cardContent = (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden 
    hover:shadow-2xl transition-shadow duration-300 w-full border-black border-2 flex flex-col items-center cursor-pointer h-full">
      
      {/* Imagen del producto */}
      <div className="overflow-hidden bg-gray-100 aspect-square m-10 w-4/5 flex items-center justify-center">
        <img
          src={imagen}
          alt={nombre}
          className="w-full h-full object-contain "
        />
      </div>

      {/* Contenido */}
      <div className="p-4 relative w-full flex flex-col items-center">
        {/* Nombre */}
        <h3 className="text-lg font-semibold text-gray-800 mb-8 text-center">
          {nombre}
        </h3>

        {/* Precio y Botón */}
        <div className="flex items-center justify-center gap-4 bg-[#e3e3e3] rounded-full 
        px-4 py-2 w-full">
          <span className="text-2xl font-bold text-gray-900">
            {precio.toFixed(2)} €
          </span>
          <button 
            onClick={(e) => e.preventDefault()}
            className="bg-black text-white rounded-full px-10 py-4 hover:bg-gray-800 transition-colors duration-200 flex items-center justify-center shrink-0">
            <svg
              className="w-7 h-7"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2 9m10 0l2-9m-10 9h12m0 0H9"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )

  if (id) {
    return (
      <Link to={`/product/${id}`} className="no-underline">
        {cardContent}
      </Link>
    )
  }

  return cardContent
}

export default ProductCard
