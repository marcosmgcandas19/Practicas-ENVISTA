/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    // Variables de estado
    let selectedSeats = [];
    let currentSessionId = null;

    // Referencias a elementos del DOM
    const modalSelect = document.getElementById('modal_select_seats');
    const modalSuccess = document.getElementById('modal_reserve_success');
    const seatsContainer = document.getElementById('seats_grid_container');
    const summarySpan = document.getElementById('js_selected_seats_summary');
    const btnConfirm = document.getElementById('js_btn_confirm_reserve');

    /**
     * 1. Apertura y Carga: Escuchar clics en las tarjetas de sesión
     */
    document.querySelectorAll('.js_open_seat_modal').forEach(card => {
        card.addEventListener('click', async (e) => {
            currentSessionId = card.dataset.sessionId;
            selectedSeats = []; // Reiniciar selección
            updateSummary();

            // Abrir modal usando Bootstrap (Odoo usa BS5)
            const modal = new bootstrap.Modal(modalSelect);
            modal.show();

            // Cargar butacas desde la API
            try {
                seatsContainer.innerHTML = '<div class="text-center w-100 py-5"><i class="fa fa-circle-o-notch fa-spin fa-2x"></i></div>';
                const data = await jsonrpc(`/cine/api/session/${currentSessionId}/seats`, {});
                renderSeats(data.seats);
            } catch (error) {
                seatsContainer.innerHTML = '<p class="text-danger">Error al cargar el mapa de sala.</p>';
            }
        });
    });

    /**
     * 2. Renderizado: Construir el mapa de asientos
     */
    function renderSeats(seats) {
        seatsContainer.innerHTML = ''; // Limpiar spinner
        
        seats.forEach(seat => {
            const seatDiv = document.createElement('div');
            seatDiv.classList.add('seat-item', 'p-2', 'text-center', 'rounded', 'border');
            seatDiv.style.width = '45px';
            seatDiv.style.cursor = seat.is_occupied ? 'not-allowed' : 'pointer';
            seatDiv.style.backgroundColor = seat.is_occupied ? '#6c757d' : '#fff';
            seatDiv.style.color = seat.is_occupied ? '#fff' : '#333';
            seatDiv.innerHTML = `<small>${seat.name}</small>`;
            seatDiv.dataset.seatId = seat.id;
            seatDiv.dataset.seatName = seat.name;

            if (!seat.is_occupied) {
                seatDiv.addEventListener('click', () => toggleSeat(seatDiv));
            }

            seatsContainer.appendChild(seatDiv);
        });
    }

    /**
     * 3. Selección (Eventos): Manejar el clic en butacas libres
     */
    function toggleSeat(element) {
        const seatId = parseInt(element.dataset.seatId);
        const seatName = element.dataset.seatName;

        if (selectedSeats.find(s => s.id === seatId)) {
            // Deseleccionar
            selectedSeats = selectedSeats.filter(s => s.id !== seatId);
            element.style.backgroundColor = '#fff';
            element.style.color = '#333';
        } else {
            // Seleccionar
            selectedSeats.push({ id: seatId, name: seatName });
            element.style.backgroundColor = '#2ECC71'; // Verde CinenVista
            element.style.color = '#fff';
        }
        updateSummary();
    }

    /**
     * Actualizar área de resumen en tiempo real
     */
    function updateSummary() {
        if (selectedSeats.length > 0) {
            summarySpan.innerText = selectedSeats.map(s => s.name).join(', ');
            btnConfirm.classList.remove('disabled');
            btnConfirm.disabled = false;
        } else {
            summarySpan.innerText = 'Ninguno';
            btnConfirm.classList.add('disabled');
            btnConfirm.disabled = true;
        }
    }

    /**
     * 4. Confirmación: Enviar datos al servidor
     */
    btnConfirm.addEventListener('click', async () => {
        if (selectedSeats.length === 0) return;

        btnConfirm.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Procesando...';
        btnConfirm.disabled = true;

        try {
            const response = await jsonrpc('/cine/api/session/reserve', {
                session_id: parseInt(currentSessionId),
                seat_ids: selectedSeats.map(s => s.id)
            });

            if (response.success) {
                /**
                 * 5. Éxito y redirección
                 */
                const bsModalSelect = bootstrap.Modal.getInstance(modalSelect);
                bsModalSelect.hide();

                const bsModalSuccess = new bootstrap.Modal(modalSuccess);
                bsModalSuccess.show();

                // Configurar el botón final para redirigir
                modalSuccess.querySelector('.btn-success').addEventListener('click', () => {
                    window.location.href = '/cine';
                });
            } else {
                alert('Error: ' + response.message);
                btnConfirm.innerHTML = 'Confirmar Reserva';
                btnConfirm.disabled = false;
            }
        } catch (error) {
            alert('Error crítico en la comunicación con el servidor.');
            btnConfirm.innerHTML = 'Confirmar Reserva';
            btnConfirm.disabled = false;
        }
    });
});