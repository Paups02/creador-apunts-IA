// Configuración
// Detectar automáticamente la URL del backend basada en el hostname actual
const getApiUrl = () => {
    const hostname = window.location.hostname;
    // Si estamos accediendo con una IP o hostname específico, usar el mismo para el backend
    return `http://${hostname}:8000`;
};

const API_URL = getApiUrl();
let currentDocuments = [];

console.log('🔗 API URL:', API_URL);

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', () => {
    checkServerStatus();
    loadDocuments();
    loadStats();

    // Event listeners
    document.getElementById('uploadForm').addEventListener('submit', handleUpload);

    // Actualizar cada 30 segundos
    setInterval(() => {
        checkServerStatus();
        loadStats();
    }, 30000);
});

// ========== UTILIDADES ==========

function showTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Mostrar el tab seleccionado
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');

    // Cargar datos específicos del tab
    if (tabName === 'upload') {
        loadDocuments();
    } else if (tabName === 'stats') {
        loadStats();
    }
}

function showResult(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `result-box ${type}`;
    element.style.display = 'block';

    // Auto-ocultar después de 5 segundos si es success
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// ========== API CALLS ==========

async function checkServerStatus() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.classList.remove('error');
            statusText.textContent = 'Conectado';
        }
    } catch (error) {
        statusDot.classList.add('error');
        statusText.textContent = 'Desconectado';
        console.error('Error checking server status:', error);
    }
}

// ========== DOCUMENTOS ==========

async function handleUpload(e) {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const tags = document.getElementById('tags').value;
    const description = document.getElementById('description').value;

    if (!fileInput.files[0]) {
        showResult('uploadResult', 'Por favor selecciona un archivo', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('tags', tags);
    formData.append('description', description);

    try {
        showResult('uploadResult', 'Subiendo documento...', 'info');

        const response = await fetch(`${API_URL}/api/documents/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showResult('uploadResult', `✅ ${data.message}\nID: ${data.document_id}`, 'success');
            document.getElementById('uploadForm').reset();
            loadDocuments();
        } else {
            showResult('uploadResult', `❌ Error: ${data.detail || 'Error desconocido'}`, 'error');
        }
    } catch (error) {
        showResult('uploadResult', `❌ Error al subir el documento: ${error.message}`, 'error');
        console.error('Upload error:', error);
    }
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/api/documents/list`);
        const data = await response.json();

        if (data.success) {
            currentDocuments = data.documents;
            displayDocuments(data.documents);
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        document.getElementById('documentList').innerHTML = '<p style="color: #ef4444;">Error al cargar documentos</p>';
    }
}

function displayDocuments(documents) {
    const container = document.getElementById('documentList');

    if (!documents || documents.length === 0) {
        container.innerHTML = '<p style="color: #6b7280;">No hay documentos todavía</p>';
        return;
    }

    container.innerHTML = documents.map(doc => `
        <div class="document-item">
            <div class="document-info">
                <h4>${doc.metadata?.name || 'Sin nombre'}</h4>
                <p>ID: ${doc.id} | Tipo: ${doc.metadata?.type || 'N/A'}</p>
                <p>Creado: ${new Date(doc.metadata?.created_at).toLocaleString('es-ES')}</p>
                ${doc.tags && doc.tags.length > 0 ? `
                    <div class="document-tags">
                        ${doc.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
            <button onclick="deleteDocument('${doc.id}')" class="btn btn-danger">Eliminar</button>
        </div>
    `).join('');
}

async function deleteDocument(docId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este documento?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/documents/${docId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadDocuments();
        } else {
            alert('Error al eliminar el documento');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('Error al eliminar el documento');
    }
}

// ========== TAREAS DE IA ==========

async function executeTask() {
    const taskType = document.getElementById('taskType').value;
    const content = document.getElementById('taskContent').value;
    const instructions = document.getElementById('taskInstructions').value;

    if (!content) {
        showResult('taskResult', 'Por favor ingresa el contenido a procesar', 'error');
        return;
    }

    try {
        showResult('taskResult', '⏳ Procesando con IA...', 'info');

        const response = await fetch(`${API_URL}/api/ai/task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_type: taskType,
                content: content,
                instructions: instructions,
                temperature: 0.7,
                max_tokens: 4096
            })
        });

        const data = await response.json();

        if (data.success) {
            const result = data.result.result || 'Sin resultado';
            showResult('taskResult', `✅ Resultado:\n\n${result}`, 'info');
        } else {
            showResult('taskResult', `❌ Error: ${data.detail || 'Error desconocido'}`, 'error');
        }
    } catch (error) {
        showResult('taskResult', `❌ Error al ejecutar la tarea: ${error.message}`, 'error');
        console.error('Task execution error:', error);
    }
}

// ========== CHAT ==========

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Mostrar mensaje del usuario
    addChatMessage(message, 'user');
    input.value = '';

    // Mostrar indicador de carga
    const loadingId = 'loading-' + Date.now();
    addChatMessage('<div class="loading"></div>', 'assistant', loadingId);

    try {
        const response = await fetch(`${API_URL}/api/ai/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        // Remover indicador de carga
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        if (data.success) {
            addChatMessage(data.response, 'assistant');
        } else {
            addChatMessage('❌ Error al procesar el mensaje', 'assistant');
        }
    } catch (error) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        addChatMessage('❌ Error de conexión', 'assistant');
        console.error('Chat error:', error);
    }
}

function addChatMessage(message, sender, id = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    if (id) messageDiv.id = id;
    messageDiv.innerHTML = message;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ========== BÚSQUEDA ==========

async function searchDocuments() {
    const query = document.getElementById('searchInput').value.trim();

    if (!query) {
        showResult('searchResults', 'Por favor ingresa un término de búsqueda', 'error');
        return;
    }

    try {
        showResult('searchResults', 'Buscando...', 'info');

        const response = await fetch(`${API_URL}/api/documents/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.success) {
            if (data.results.length === 0) {
                showResult('searchResults', 'No se encontraron resultados', 'info');
            } else {
                const resultsHTML = data.results.map(doc => `
                    <div class="document-item">
                        <div class="document-info">
                            <h4>${doc.metadata?.name || 'Sin nombre'}</h4>
                            <p>ID: ${doc.id}</p>
                            <p>Relevancia: ${doc.score ? (doc.score * 100).toFixed(1) + '%' : 'N/A'}</p>
                        </div>
                    </div>
                `).join('');

                document.getElementById('searchResults').innerHTML = `
                    <h4>Resultados (${data.results.length}):</h4>
                    ${resultsHTML}
                `;
                document.getElementById('searchResults').className = 'result-box info';
            }
        } else {
            showResult('searchResults', 'Error en la búsqueda', 'error');
        }
    } catch (error) {
        showResult('searchResults', `Error: ${error.message}`, 'error');
        console.error('Search error:', error);
    }
}

// ========== ESTADÍSTICAS ==========

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('totalDocs').textContent = data.stats.total_documents;
            document.getElementById('aiStatus').textContent = data.stats.ai_agent_status === 'active' ? '✅ Activo' : '❌ Inactivo';
            document.getElementById('availableTasks').textContent = data.stats.available_tasks;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}
