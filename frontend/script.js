
const API_URL = 'http://192.168.0.33:8080/api';


let addProductModal;
let addSaleModal;
let addSupplierModal;


document.addEventListener('DOMContentLoaded', function() {
    
    addProductModal = new bootstrap.Modal(document.getElementById('addProductModal'));
    addSaleModal = new bootstrap.Modal(document.getElementById('addSaleModal'));
    addSupplierModal = new bootstrap.Modal(document.getElementById('addSupplierModal'));

    
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);

    document.getElementById('start-date').value = thirtyDaysAgo.toISOString().split('T')[0];
    document.getElementById('end-date').value = today.toISOString().split('T')[0];

    
    loadProducts();
    loadSales();
    loadSuppliers();
    loadAnalytics();
});


async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        const products = await response.json();
        
        const tableBody = document.getElementById('products-table-body');
        tableBody.innerHTML = '';
        
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.code}</td>
                <td>${product.category || '-'}</td>
                <td>${product.quantity}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">Excluir</button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        
        const saleProductSelect = document.getElementById('saleProduct');
        saleProductSelect.innerHTML = '<option value="">Selecione um produto</option>';
        products.forEach(product => {
            saleProductSelect.innerHTML += `<option value="${product.id}">${product.name} (${product.quantity} em estoque)</option>`;
        });
    } catch (error) {
        console.error('Error loading products:', error);
        alert('Erro ao carregar produtos. Por favor, tente novamente.');
    }
}

function showAddProductModal() {
    
    loadSuppliersForSelect();
    addProductModal.show();
}

async function addProduct() {
    const form = document.getElementById('addProductForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        name: document.getElementById('productName').value,
        code: document.getElementById('productCode').value,
        category: document.getElementById('productCategory').value,
        quantity: parseInt(document.getElementById('productQuantity').value),
        supplier_id: document.getElementById('productSupplier').value || null
    };

    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            addProductModal.hide();
            form.reset();
            loadProducts();
        } else {
            throw new Error('Erro ao adicionar produto');
        }
    } catch (error) {
        console.error('Error adding product:', error);
        alert('Erro ao adicionar produto. Por favor, tente novamente.');
    }
}

async function deleteProduct(productId) {
    if (!confirm('Tem certeza que deseja excluir este produto?')) return;

    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadProducts();
        } else {
            throw new Error('Erro ao excluir produto');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        alert('Erro ao excluir produto. Por favor, tente novamente.');
    }
}


async function loadSales() {
    try {
        const response = await fetch(`${API_URL}/sales`);
        const sales = await response.json();
        
        const tableBody = document.getElementById('sales-table-body');
        tableBody.innerHTML = '';
        
        sales.forEach(sale => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sale.date}</td>
                <td>${sale.product_name}</td>
                <td>${sale.quantity}</td>
                <td>R$ ${sale.unit_price.toFixed(2)}</td>
                <td>R$ ${sale.total_price.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteSale(${sale.id})">Excluir</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading sales:', error);
        alert('Erro ao carregar vendas. Por favor, tente novamente.');
    }
}

function showAddSaleModal() {
    addSaleModal.show();
}

async function addSale() {
    const form = document.getElementById('addSaleForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        product_id: parseInt(document.getElementById('saleProduct').value),
        quantity: parseInt(document.getElementById('saleQuantity').value),
        unit_price: parseFloat(document.getElementById('saleUnitPrice').value)
    };

    try {
        const response = await fetch(`${API_URL}/sales`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            addSaleModal.hide();
            form.reset();
            loadSales();
            loadProducts();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao registrar venda');
        }
    } catch (error) {
        console.error('Error adding sale:', error);
        alert(error.message || 'Erro ao registrar venda. Por favor, tente novamente.');
    }
}

async function deleteSale(saleId) {
    if (!confirm('Tem certeza que deseja excluir esta venda?')) return;

    try {
        const response = await fetch(`${API_URL}/sales/${saleId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadSales();
            loadProducts();
        } else {
            throw new Error('Erro ao excluir venda');
        }
    } catch (error) {
        console.error('Error deleting sale:', error);
        alert('Erro ao excluir venda. Por favor, tente novamente.');
    }
}


async function loadSuppliers() {
    try {
        const response = await fetch(`${API_URL}/suppliers`);
        const suppliers = await response.json();
        
        const tableBody = document.getElementById('suppliers-table-body');
        tableBody.innerHTML = '';
        
        suppliers.forEach(supplier => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${supplier.name}</td>
                <td>${supplier.contact || '-'}</td>
                <td>${supplier.email || '-'}</td>
                <td>${supplier.phone || '-'}</td>
                <td>${supplier.delivery_time || '-'} dias</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteSupplier(${supplier.id})">Excluir</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading suppliers:', error);
        alert('Erro ao carregar fornecedores. Por favor, tente novamente.');
    }
}

async function loadSuppliersForSelect() {
    try {
        const response = await fetch(`${API_URL}/suppliers`);
        const suppliers = await response.json();
        
        const select = document.getElementById('productSupplier');
        select.innerHTML = '<option value="">Selecione um fornecedor</option>';
        suppliers.forEach(supplier => {
            select.innerHTML += `<option value="${supplier.id}">${supplier.name}</option>`;
        });
    } catch (error) {
        console.error('Error loading suppliers for select:', error);
    }
}

function showAddSupplierModal() {
    addSupplierModal.show();
}

async function addSupplier() {
    const form = document.getElementById('addSupplierForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        name: document.getElementById('supplierName').value,
        contact: document.getElementById('supplierContact').value,
        email: document.getElementById('supplierEmail').value,
        phone: document.getElementById('supplierPhone').value,
        delivery_time: parseInt(document.getElementById('supplierDeliveryTime').value) || null,
        address: document.getElementById('supplierAddress').value
    };

    try {
        const response = await fetch(`${API_URL}/suppliers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            addSupplierModal.hide();
            form.reset();
            loadSuppliers();
            loadSuppliersForSelect();
        } else {
            throw new Error('Erro ao adicionar fornecedor');
        }
    } catch (error) {
        console.error('Error adding supplier:', error);
        alert('Erro ao adicionar fornecedor. Por favor, tente novamente.');
    }
}

async function deleteSupplier(supplierId) {
    if (!confirm('Tem certeza que deseja excluir este fornecedor?')) return;

    try {
        const response = await fetch(`${API_URL}/suppliers/${supplierId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadSuppliers();
            loadSuppliersForSelect();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir fornecedor');
        }
    } catch (error) {
        console.error('Error deleting supplier:', error);
        alert(error.message || 'Erro ao excluir fornecedor. Por favor, tente novamente.');
    }
}


async function loadAnalytics() {
    await Promise.all([
        loadSalesAnalytics(),
        loadInventoryAnalytics()
    ]);
}

async function loadSalesAnalytics() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    try {
        const response = await fetch(`${API_URL}/analytics/sales?start_date=${startDate}&end_date=${endDate}`);
        const data = await response.json();
        
        document.getElementById('total-sales').textContent = `R$ ${data.total_sales.toFixed(2)}`;
        document.getElementById('total-units').textContent = data.total_units;
    } catch (error) {
        console.error('Error loading sales analytics:', error);
    }
}

async function loadInventoryAnalytics() {
    try {
        const response = await fetch(`${API_URL}/analytics/inventory`);
        const data = await response.json();
        
        
        const lowStockList = document.getElementById('low-stock-list');
        lowStockList.innerHTML = data.low_stock_products.map(product => `
            <div class="alert alert-warning">
                ${product.name} - ${product.quantity} unidades
            </div>
        `).join('') || '<p class="text-muted">Nenhum produto com estoque baixo</p>';
        
        
        const categoryDistribution = document.getElementById('category-distribution');
        categoryDistribution.innerHTML = Object.entries(data.category_distribution)
            .map(([category, count]) => `
                <div class="mb-2">
                    <strong>${category || 'Sem categoria'}:</strong> ${count} produtos
                </div>
            `).join('');
    } catch (error) {
        console.error('Error loading inventory analytics:', error);
    }
}


async function askQuestion() {
    const questionInput = document.getElementById('question');
    const responseDiv = document.getElementById('response');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Por favor, digite uma pergunta.');
        return;
    }
    
    responseDiv.innerHTML = '<p class="text-muted">Processando sua pergunta...</p>';
    
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            responseDiv.innerHTML = `<p>${data.answer}</p>`;
        } else {
            responseDiv.innerHTML = `<p class="text-danger">${data.error || 'Erro ao processar a pergunta.'}</p>`;
        }
    } catch (error) {
        console.error('Error asking question:', error);
        responseDiv.innerHTML = '<p class="text-danger">Erro ao processar sua pergunta. Por favor, tente novamente.</p>';
    }
}


document.getElementById('question').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});