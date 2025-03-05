async function fetchMedicos() {
    const response = await fetch('http://127.0.0.1:5000/medicos');
    const medicos = await response.json();
    let tableBody = medicos.map(m => `
        <tr>
            <td>${m.id}</td>
            <td>${m.nombre}</td>
            <td>${m.apellido}</td>
            <td>${m.especialidad}</td>
            <td>${m.email}</td>
            <td>
                <button class='btn btn-warning btn-sm' onclick='editMedico(${m.id})'>Editar</button>
                <button class='btn btn-danger btn-sm' onclick='deleteMedico(${m.id})'>Eliminar</button>
            </td>
        </tr>
    `).join("");
    document.getElementById('medicos-table').innerHTML = tableBody;
}

async function crearMedico() {
    const data = {
        nombre: document.getElementById('medicoNombre').value,
        apellido: document.getElementById('medicoApellido').value,
        especialidad: document.getElementById('medicoEspecialidad').value,
        email: document.getElementById('medicoEmail').value
    };

    const response = await fetch('http://127.0.0.1:5000/medicos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        fetchMedicos();
        bootstrap.Modal.getInstance(document.getElementById('medicoModal')).hide();
    }
}

async function deleteMedico(id) {
    if (!confirm("¿Eliminar médico?")) return;
    await fetch(`http://127.0.0.1:5000/medicos/${id}`, { method: 'DELETE' });
    fetchMedicos();
}

async function editMedico(id) {
    const nombre = prompt("Nuevo nombre:");
    const apellido = prompt("Nuevo apellido:");
    const especialidad = prompt("Nueva especialidad:");
    const email = prompt("Nuevo email:");

    await fetch(`http://127.0.0.1:5000/medicos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, apellido, especialidad, email })
    });
    fetchMedicos();
}