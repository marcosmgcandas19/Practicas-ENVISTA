/** @odoo-module **/

// ========== VARIABLES GLOBALES DE ESTADO ==========
let selectedSeats = [];
let currentSessionId = null;
let allSeatsData = [];

// Exportar funciones al scope global para que sean accesibles desde HTML
window.openSeatModal = openSeatModal;
window.closeSeatModal = closeSeatModal;
window.confirmSelection = confirmSelection;
window.redirectToHome = redirectToHome;

// ========== FUNCIÓN 1: ABRIR MODAL Y CARGAR BUTACAS ==========
/**
 * Abre el modal de selección de butacas y carga los datos de la sesión.
 * Se llama cuando el usuario hace clic en una tarjeta de sesión.
 */
async function openSeatModal(element) {
    const sessionId = element.getAttribute('data-session-id');
    
    if (!sessionId) {
        console.error('Atributo data-session-id no encontrado en elemento:', element);
        alert('Error: ID de sesión no válido');
        return;
    }

    console.log(`Abriendo modal para sesión: ${sessionId}`);
    
    currentSessionId = sessionId;
    selectedSeats = [];
    
    // Mostrar modal
    const modal = document.getElementById('seatSelectionModal');
    if (!modal) {
        console.error('Modal con ID "seatSelectionModal" no encontrado en el DOM');
        alert('Error: Los componentes de la interfaz no están cargados correctamente');
        return;
    }
    
    modal.classList.remove('hidden');
    console.log('Modal abierto');

    // Mostrar spinner mientras se cargan los datos
    const seatsGrid = document.getElementById('seatsGrid');
    if (!seatsGrid) {
        console.error('Contenedor con ID "seatsGrid" no encontrado en el DOM');
        alert('Error: Los componentes de la interfaz no están cargados correctamente');
        return;
    }
    
    seatsGrid.innerHTML = '<div class="loading-spinner">Cargando butacas...</div>';
    updateSelectedSeatsList();

    // Cargar datos de butacas desde la API
    try {
        console.log(`Llamando endpoint: /cine/api/session/${sessionId}/seats`);
        const response = await fetch(`/cine/api/session/${sessionId}/seats`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        console.log(`Respuesta HTTP: ${response.status} ${response.statusText}`);
        console.log(`Content-Type: ${response.headers.get('Content-Type')}`);

        // Leer la respuesta como texto primero para debugging
        const responseText = await response.text();
        console.log('Respuesta del servidor (texto):', responseText);

        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}: ${response.statusText}\nRespuesta: ${responseText}`);
        }

        // Parsear JSON
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error('Error al parsear JSON:', parseError);
            throw new Error(`Respuesta no es JSON válido: ${responseText}`);
        }

        // Validar que la respuesta tiene datos válidos
        if (!data || !data.seats) {
            console.error('Respuesta inválida del servidor:', data);
            throw new Error('La respuesta del servidor no contiene datos de butacas');
        }
        
        console.log('Butacas cargadas correctamente:', data.seats);
        allSeatsData = data.seats || [];
        renderSeatsGrid(allSeatsData);
    } catch (error) {
        console.error('Error detallado al cargar butacas:', error);
        seatsGrid.innerHTML = `<div class="loading-spinner" style="color: #dc3545;">Error al cargar el mapa de butacas: ${error.message}. Intenta nuevamente.</div>`;
    }
}

// ========== FUNCIÓN 2: CERRAR MODAL ==========
/**
 * Cierra el modal de selección de butacas.
 */
function closeSeatModal() {
    const modal = document.getElementById('seatSelectionModal');
    modal.classList.add('hidden');
    selectedSeats = [];
    updateSelectedSeatsList();
}

// ========== FUNCIÓN 3: RENDERIZAR GRID DE BUTACAS ==========
/**
 * Construye dinámicamente la cuadrícula de butacas organizadas por filas.
 * Cada botón tiene datos del asiento y gestiona el evento de clic.
 */
function renderSeatsGrid(seatsData) {
    const seatsGrid = document.getElementById('seatsGrid');
    
    // Validar datos
    if (!seatsData || seatsData.length === 0) {
        console.error('No hay datos de butacas para renderizar:', seatsData);
        seatsGrid.innerHTML = '<div class="loading-spinner" style="color: #dc3545;">No se encontraron butacas en esta sala.</div>';
        return;
    }
    
    console.log(`Renderizando ${seatsData.length} butacas`);
    seatsGrid.innerHTML = '';

    // Agrupar butacas por fila
    const seatsByRow = {};
    seatsData.forEach(seat => {
        if (!seatsByRow[seat.row]) {
            seatsByRow[seat.row] = [];
        }
        seatsByRow[seat.row].push(seat);
    });

    // Ordenar filas alfabéticamente
    const sortedRows = Object.keys(seatsByRow).sort();
    console.log(`Filas encontradas: ${sortedRows.join(', ')}`);

    // Crear contenedor de grid
    const gridContainer = document.createElement('div');
    gridContainer.className = 'seats-grid';

    // Renderizar cada fila
    sortedRows.forEach(rowLetter => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seats-row';

        // Etiqueta de fila
        const rowLabel = document.createElement('div');
        rowLabel.className = 'row-label';
        rowLabel.textContent = rowLetter;
        rowDiv.appendChild(rowLabel);

        // Butacas de la fila
        const seatsInRow = seatsByRow[rowLetter].sort((a, b) => a.number - b.number);
        seatsInRow.forEach(seat => {
            const seatButton = document.createElement('button');
            seatButton.className = 'seat';
            seatButton.textContent = seat.number;
            seatButton.dataset.seatId = seat.id;
            seatButton.dataset.seatName = seat.name;
            seatButton.type = 'button';

            if (seat.is_occupied) {
                seatButton.classList.add('occupied');
                seatButton.disabled = true;
            } else {
                seatButton.addEventListener('click', () => toggleSeatSelection(seat));
            }

            rowDiv.appendChild(seatButton);
        });

        gridContainer.appendChild(rowDiv);
    });

    seatsGrid.appendChild(gridContainer);
    console.log('Grid de butacas renderizado exitosamente');
}

// ========== FUNCIÓN 4: ALTERNAR SELECCIÓN DE BUTACA ==========
/**
 * Alterna la selección de una butaca (selecciona/deselecciona).
 * Actualiza la lista visible y el estado visual.
 */
function toggleSeatSelection(seat) {
    const seatIndex = selectedSeats.findIndex(s => s.id === seat.id);

    if (seatIndex > -1) {
        // Deseleccionar
        selectedSeats.splice(seatIndex, 1);
    } else {
        // Seleccionar
        selectedSeats.push(seat);
    }

    // Actualizar estilo de los botones
    updateSeatsVisualState();
    // Actualizar lista de resumen
    updateSelectedSeatsList();
}

// ========== FUNCIÓN 5: ACTUALIZAR ESTADO VISUAL DE BUTACAS ==========
/**
 * Aplica las clases CSS apropiadas a los botones según su estado.
 */
function updateSeatsVisualState() {
    document.querySelectorAll('.seat').forEach(button => {
        const seatId = parseInt(button.dataset.seatId);
        const isSelected = selectedSeats.some(s => s.id === seatId);

        if (isSelected) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
}

// ========== FUNCIÓN 6: ACTUALIZAR LISTA DE BUTACAS SELECCIONADAS ==========
/**
 * Actualiza la sección de resumen con las butacas seleccionadas.
 * Habilita/deshabilita el botón de confirmación.
 */
function updateSelectedSeatsList() {
    const listContainer = document.getElementById('selectedSeatsList');
    const confirmBtn = document.getElementById('confirmSeatsBtn');

    if (selectedSeats.length === 0) {
        listContainer.innerHTML = '<span class="empty-message">Ninguna butaca seleccionada</span>';
        confirmBtn.disabled = true;
    } else {
        // Crear badges para cada butaca seleccionada
        const seatBadges = selectedSeats
            .map(seat => 
                `<span class="seat-badge">${seat.name}</span>`
            )
            .join('');
        listContainer.innerHTML = seatBadges;
        confirmBtn.disabled = false;
    }
}

// ========== FUNCIÓN 7: CONFIRMAR SELECCIÓN ==========
/**
 * Envía los datos de la reserva al servidor.
 * Crea el pedido de venta y la reserva en el backend.
 */
async function confirmSelection() {
    if (selectedSeats.length === 0) {
        alert('Por favor selecciona al menos una butaca');
        return;
    }

    const confirmBtn = document.getElementById('confirmSeatsBtn');
    const originalText = confirmBtn.textContent;
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Procesando...';

    try {
        const seatIds = selectedSeats.map(s => s.id);
        const csrfToken = getCsrfToken();
        
        console.log('Enviando reserva:', {
            session_id: parseInt(currentSessionId),
            seat_ids: seatIds,
            csrf_token: csrfToken ? `${csrfToken.substring(0, 10)}...` : 'NONE'
        });
        
        const response = await fetch('/cine/api/session/reserve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                session_id: parseInt(currentSessionId),
                seat_ids: seatIds
            })
        });

        console.log(`Respuesta HTTP: ${response.status} ${response.statusText}`);
        
        const responseText = await response.text();
        console.log('Respuesta del servidor (texto):', responseText);

        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}: ${response.statusText}\nRespuesta: ${responseText.substring(0, 500)}`);
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error('Error al parsear JSON:', parseError);
            throw new Error(`Respuesta no es JSON válido: ${responseText}`);
        }

        console.log('Datos de respuesta:', data);

        if (data.success) {
            // Éxito: cerrar modal de selección y mostrar modal de confirmación
            closeSeatModal();
            showSuccessModal();
        } else {
            const errorMsg = data.message || 'No se pudo procesar la reserva';
            console.error('Error en respuesta:', errorMsg);
            alert('Error: ' + errorMsg);
            confirmBtn.disabled = false;
            confirmBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('Error detallado al confirmar reserva:', error);
        alert('Error crítico: ' + error.message);
        confirmBtn.disabled = false;
        confirmBtn.textContent = originalText;
    }
}

// ========== FUNCIÓN 8: MOSTRAR MODAL DE ÉXITO ==========
/**
 * Muestra el modal de confirmación de éxito.
 */
function showSuccessModal() {
    const successModal = document.getElementById('successModal');
    successModal.classList.remove('hidden');
}

// ========== FUNCIÓN 9: REDIRIGIR A LA PÁGINA PRINCIPAL ==========
/**
 * Redirige al usuario a la página principal del cine.
 * Se ejecuta cuando hace clic en el botón "Volver al cine".
 */
function redirectToHome() {
    window.location.href = '/cine';
}

// ========== FUNCIÓN AUXILIAR: OBTENER TOKEN CSRF ==========
/**
 * Obtiene el token CSRF necesario para las peticiones POST en Odoo.
 * En Odoo 17 para website, busca en odoo.csrf_token (variable global).
 */
function getCsrfToken() {
    // Intento 1: Odoo global object (Odoo 17 website)
    if (window.odoo && window.odoo.csrf_token) {
        console.log('CSRF token obtenido de odoo.csrf_token');
        return window.odoo.csrf_token;
    }
    
    // Intento 2: Buscar en input fields de Odoo
    const tokens = document.querySelectorAll('input[name="csrf_token"]');
    if (tokens.length > 0) {
        console.log('CSRF token obtenido de input field');
        return tokens[0].value;
    }
    
    // Intento 3: Buscar en meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        console.log('CSRF token obtenido de meta tag');
        return metaToken.content;
    }
    
    // Intento 4: Buscar en cookies
    const cookieName = 'XSRF-TOKEN';
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(cookieName + '='))
        ?.split('=')[1];
    
    if (cookieValue) {
        console.log('CSRF token obtenido de cookie');
        return cookieValue;
    }
    
    console.warn('No se encontró token CSRF');
    return '';
}

// ========== EVENTO: INICIALIZACIÓN ==========
/**
 * Al cargar la página, vincular los onclick de las tarjetas de sesión.
 * Nota: También se pueden usar onclick directamente en HTML.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Los onclick ya están en el HTML, no es necesario agregar listeners aquí
    // Pero dejamos el evento por si hay inicializaciones futuras necesarias
});