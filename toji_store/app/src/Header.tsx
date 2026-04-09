function Header() {
  return (


    <header className="bg-black text-white">


      <div className="grid grid-cols-3 gap-8 items-center px-2 py-4 max-w-7xl mx-auto">
        {/* Logo - Izquierda */}
        <div className="flex items-center">
          <img
            src="/logo.svg"
            alt="Toji Store Logo"
            className="w-12 h-12 mr-2"
          />
          
        </div>

        {/* Navegación - Centro */}
        <nav className="flex justify-center gap-10">
          <a href="#" className="hover:text-gray-300 transition font-medium text-sm">
            Catálogo
          </a>
          <a href="#" className="hover:text-gray-300 transition font-medium text-sm">
            Juguetes
          </a>
          <a href="#" className="hover:text-gray-300 transition font-medium text-sm">
            Papelería
          </a>
        </nav>

        {/* Iconos - Derecha */}
        <div className="flex justify-end items-center gap-6">
          {/* Búsqueda */}
          <button className="hover:text-gray-300 transition" title="Buscar">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </button>

          {/* Carrito */}
          <button className="hover:text-gray-300 transition relative" title="Carrito">
            <svg
              className="w-5 h-5"
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
            <span className="absolute -top-2 -right-2 bg-red-500 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
              0
            </span>
          </button>

          {/* Perfil */}
          <button className="hover:opacity-80 transition" title="Perfil">
            <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center">
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 12a4 4 0 100-8 4 4 0 000 8z" />
                <path d="M12 14c-6 0-8 3-8 3v6h16v-6s-2-3-8-3z" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
