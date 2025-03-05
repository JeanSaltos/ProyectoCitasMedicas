async function fetchConsultorios() {
    const response = await fetch('http://127.0.0.1:5000/consultorios');
    const consultorios = await response.json();
    let tableBody = consultorios.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.numero}</td>
            <td>${c.ubicacion}</td>
            <td>${c.descripcion}</td>
            <td>
                <button class='btn btn-warning btn-sm' onclick='editConsultorio(${c.id})'>Editar</button>
                <button class='btn btn-danger btn-sm' onclick='deleteConsultorio(${c.id})'>Eliminar</button>
            </td>
        </tr>
    `).join("");
    document.getElementById('consultorios-table').innerHTML = tableBody;
}

async function crearConsultorio() {
    const data = {
        numero: document.getElementById('consultorioNumero').value,
        ubicacion: document.getElementById('consultorioUbicacion').value,
        descripcion: document.getElementById('consultorioDescripcion').value
    };

    const response = await fetch('http://127.0.0.1:5000/consultorios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        fetchConsultorios();
        bootstrap.Modal.getInstance(document.getElementById('consultorioModal')).hide();
    }
}

async function deleteConsultorio(id) {
    if (!confirm("¿Eliminar consultorio?")) return;
    await fetch(`http://127.0.0.1:5000/consultorios/${id}`, { method: 'DELETE' });
    fetchConsultorios();
}

async function editConsultorio(id) {
    const numero = prompt("Nuevo número:");
    const ubicacion = prompt("Nueva ubicación:");
    const descripcion = prompt("Nueva descripción:");

    await fetch(`http://127.0.0.1:5000/consultorios/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numero, ubicacion, descripcion })
    });
    fetchConsultorios();
}