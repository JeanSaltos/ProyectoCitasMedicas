async function fetchPacientes() {
    const response = await fetch('http://127.0.0.1:5000/pacientes');
    const pacientes = await response.json();
    let tableBody = pacientes.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.nombre}</td>
            <td>${p.apellido}</td>
            <td>${p.fecha_nacimiento}</td>
            <td>${p.email}</td>
            <td>
                <button class='btn btn-warning btn-sm' onclick='editPaciente(${p.id})'>Editar</button>
                <button class='btn btn-danger btn-sm' onclick='deletePaciente(${p.id})'>Eliminar</button>
            </td>
        </tr>
    `).join("");
    document.getElementById('pacientes-table').innerHTML = tableBody;
}

async function crearPaciente() {
    const nombre = document.getElementById('pacienteNombre').value;
    const apellido = document.getElementById('pacienteApellido').value;
    const fechaNacimiento = document.getElementById('pacienteFechaNacimiento').value;
    const email = document.getElementById('pacienteEmail').value;

    const response = await fetch('http://127.0.0.1:5000/pacientes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, apellido, fecha_nacimiento: fechaNacimiento, email })
    });

    if (response.ok) {
        fetchPacientes();
        bootstrap.Modal.getInstance(document.getElementById('pacienteModal')).hide();
    } else {
        alert("Error al agregar paciente");
    }
}

async function deletePaciente(id) {
    if (!confirm("¿Seguro que deseas eliminar este paciente?")) return;
    const response = await fetch(`http://127.0.0.1:5000/pacientes/${id}`, { method: 'DELETE' });

    if (response.ok) {
        fetchPacientes();
    } else {
        alert("Error eliminando paciente");
    }
}

async function editPaciente(id) {
    const nombre = prompt("Nuevo nombre:");
    const apellido = prompt("Nuevo apellido:");
    const fechaNacimiento = prompt("Nueva fecha de nacimiento (YYYY-MM-DD):");
    const email = prompt("Nuevo email:");

    const response = await fetch(`http://127.0.0.1:5000/pacientes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, apellido, fecha_nacimiento: fechaNacimiento, email })
    });

    if (response.ok) {
        fetchPacientes();
    } else {
        alert("Error actualizando paciente");
    }
}