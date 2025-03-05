async function fetchCitas() {
    const response = await fetch('http://127.0.0.1:5000/citas');
    const citas = await response.json();
    let tableBody = citas.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.paciente_id}</td>
            <td>${c.medico_id}</td>
            <td>${c.consultorio_id}</td>
            <td>${c.fecha}</td>
            <td>${c.hora}</td>
            <td>
                <button class='btn btn-warning btn-sm' onclick='editCita(${c.id})'>Editar</button>
                <button class='btn btn-danger btn-sm' onclick='deleteCita(${c.id})'>Eliminar</button>
            </td>
        </tr>
    `).join("");
    document.getElementById('citas-table').innerHTML = tableBody;
}

async function crearCita() {
    const data = {
        paciente_id: document.getElementById('citaPacienteId').value,
        medico_id: document.getElementById('citaMedicoId').value,
        consultorio_id: document.getElementById('citaConsultorioId').value,
        fecha: document.getElementById('citaFecha').value,
        hora: document.getElementById('citaHora').value
    };

    const response = await fetch('http://127.0.0.1:5000/citas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        fetchCitas();
        bootstrap.Modal.getInstance(document.getElementById('citaModal')).hide();
    }
}

async function deleteCita(id) {
    if (!confirm("¿Eliminar cita?")) return;
    await fetch(`http://127.0.0.1:5000/citas/${id}`, { method: 'DELETE' });
    fetchCitas();
}

async function editCita(id) {
    const paciente_id = prompt("Nuevo ID Paciente:");
    const medico_id = prompt("Nuevo ID Médico:");
    const consultorio_id = prompt("Nuevo ID Consultorio:");
    const fecha = prompt("Nueva fecha (YYYY-MM-DD):");
    const hora = prompt("Nueva hora (HH:MM):");

    await fetch(`http://127.0.0.1:5000/citas/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paciente_id, medico_id, consultorio_id, fecha, hora })
    });
    fetchCitas();
}