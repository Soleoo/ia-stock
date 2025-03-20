from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import pandas as pd
from sqlalchemy import func
from sklearn.linear_model import LinearRegression
import numpy as np

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv('GOOGLE_API_KEY'),
    temperature=1
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente especializado em gestão de estoque. "
               "Use os dados do estoque fornecidos para responder às perguntas de forma clara e concisa."
               "Seu retorno não deverá ter *, somente texto."
               "Caso o retorno tiver a necessidade de ser em tópicos, utilize uma quebra de linha para listar."),
    ("human", "Dados do estoque:\n{inventory_context}\n\nPergunta: {question}")
])

chain = prompt_template | llm | StrOutputParser()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales = db.relationship('Sale', backref='product', lazy=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    supplier = db.relationship('Supplier', backref='products')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def calculate_total(self):
        print(self.unit_price)
        print(self.unit_price * self.quantity)
        self.total_price = self.quantity * self.unit_price

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    delivery_time = db.Column(db.Integer)  
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'code': p.code,
        'category': p.category,
        'quantity': p.quantity,
        'supplier_id': p.supplier_id
    } for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data['name'],
        code=data['code'],
        category=data.get('category'),
        quantity=data.get('quantity', 0),
        supplier_id=data.get('supplier_id')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully', 'id': new_product.id})

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    product.name = data.get('name', product.name)
    product.code = data.get('code', product.code)
    product.category = data.get('category', product.category)
    product.quantity = data.get('quantity', product.quantity)
    product.supplier_id = data.get('supplier_id', product.supplier_id)
    
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})


@app.route('/api/sales', methods=['GET'])
def get_sales():
    date_filter = request.args.get('date')
    query = Sale.query
    if date_filter:
        start_date = datetime.strptime(date_filter, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        query = query.filter(Sale.date >= start_date, Sale.date < end_date)
    sales = query.all()
    return jsonify([{
        'id': s.id,
        'product_id': s.product_id,
        'product_name': s.product.name,
        'quantity': s.quantity,
        'unit_price': s.unit_price,
        'total_price': s.total_price,
        'date': s.date.strftime('%Y-%m-%d %H:%M:%S')
    } for s in sales])

@app.route('/api/sales', methods=['POST'])
def add_sale():
    data = request.json
    product = Product.query.get_or_404(data['product_id'])
    
    if product.quantity < data['quantity']:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    new_sale = Sale(
        product_id=data['product_id'],
        quantity=data['quantity'],
        unit_price=data['unit_price']
    )
    new_sale.calculate_total()
    
    
    
    product.quantity -= data['quantity']
    
    db.session.add(new_sale)
    db.session.commit()
    return jsonify({'message': 'Sale recorded successfully', 'id': new_sale.id})

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    product = sale.product
    
    
    product.quantity += sale.quantity
    
    db.session.delete(sale)
    db.session.commit()
    return jsonify({'message': 'Sale deleted successfully'})


@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'contact': s.contact,
        'delivery_time': s.delivery_time,
        'email': s.email,
        'phone': s.phone,
        'address': s.address
    } for s in suppliers])

@app.route('/api/suppliers', methods=['POST'])
def add_supplier():
    data = request.json
    new_supplier = Supplier(
        name=data['name'],
        contact=data.get('contact'),
        delivery_time=data.get('delivery_time'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.session.add(new_supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier added successfully', 'id': new_supplier.id})

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.json
    
    supplier.name = data.get('name', supplier.name)
    supplier.contact = data.get('contact', supplier.contact)
    supplier.delivery_time = data.get('delivery_time', supplier.delivery_time)
    supplier.email = data.get('email', supplier.email)
    supplier.phone = data.get('phone', supplier.phone)
    supplier.address = data.get('address', supplier.address)
    
    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully'})

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if supplier.products:
        return jsonify({'error': 'Cannot delete supplier with associated products'}), 400
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'})


@app.route('/api/analytics/sales', methods=['GET'])
def get_sales_analytics():
    
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    
    sales = Sale.query.filter(
        Sale.date.between(start_date, end_date)
    ).all()
    
    
    total_sales = sum(s.total_price for s in sales)
    total_units = sum(s.quantity for s in sales)
    average_price = total_sales / total_units if total_units > 0 else 0
    
    
    product_sales = {}
    for sale in sales:
        if sale.product.name not in product_sales:
            product_sales[sale.product.name] = {
                'quantity': 0,
                'total': 0
            }
        product_sales[sale.product.name]['quantity'] += sale.quantity
        product_sales[sale.product.name]['total'] += sale.total_price
    
    return jsonify({
        'total_sales': total_sales,
        'total_units': total_units,
        'average_price': average_price,
        'product_sales': product_sales,
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    })

@app.route('/api/analytics/inventory', methods=['GET'])
def get_inventory_analytics():
    
    low_stock = Product.query.filter(Product.quantity < 10).all()
    
    
    category_counts = db.session.query(
        Product.category,
        func.count(Product.id)
    ).group_by(Product.category).all()
    
    
    total_value = sum(p.quantity * 100 for p in Product.query.all())  
    
    return jsonify({
        'low_stock_products': [{
            'name': p.name,
            'quantity': p.quantity,
            'category': p.category
        } for p in low_stock],
        'category_distribution': dict(category_counts),
        'total_inventory_value': total_value
    })

@app.route('/api/analytics/advanced', methods=['GET'])
def get_advanced_analytics():
    
    sales = Sale.query.all()
    products = Product.query.all()

    if not sales or not products:
        return jsonify({'error': 'Insufficient data for advanced analytics'}), 400

    
    sales_data = pd.DataFrame([{
        'date': s.date,
        'product_name': s.product.name,
        'quantity': s.quantity,
        'total_price': s.total_price
    } for s in sales])

    
    sales_data['date'] = pd.to_datetime(sales_data['date'])
    daily_sales = sales_data.groupby(sales_data['date'].dt.date).sum().reset_index()
    daily_sales.rename(columns={'date': 'day', 'total_price': 'daily_revenue'}, inplace=True)

    
    daily_sales['day_num'] = (daily_sales['day'] - daily_sales['day'].min()).dt.days
    X = daily_sales[['day_num']]
    y = daily_sales['daily_revenue']
    model = LinearRegression()
    model.fit(X, y)
    future_days = np.array([[i] for i in range(daily_sales['day_num'].max() + 1, daily_sales['day_num'].max() + 8)])
    future_revenue = model.predict(future_days)

    
    top_products = sales_data.groupby('product_name').sum().sort_values(by='quantity', ascending=False).head(5)
    top_products = top_products[['quantity', 'total_price']].reset_index()

    
    low_stock_products = [{
        'name': p.name,
        'quantity': p.quantity,
        'predicted_days_to_stockout': p.quantity / (sales_data[sales_data['product_name'] == p.name]['quantity'].mean() or 1)
    } for p in products if p.quantity < 10]

    return jsonify({
        'sales_trends': daily_sales.to_dict(orient='records'),
        'future_revenue_prediction': future_revenue.tolist(),
        'top_selling_products': top_products.to_dict(orient='records'),
        'low_stock_predictions': low_stock_products
    })

@app.route('/api/query', methods=['POST'])
def query_inventory():
    data = request.json
    question = data.get('question')
    print(question)
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        
        products = Product.query.all()
        sales = Sale.query.all()
        suppliers = Supplier.query.all()
        
        if not products:
            return jsonify({'error': 'No inventory data available'}), 400
        
        
        inventory_context = "\n".join([f"{p.name}: {p.quantity} unidades" for p in products])
        
        
        sales_context = "\n".join([
            f"Venda ID {s.id}: {s.quantity} unidades de {s.product.name} a {s.unit_price} cada em {s.date.strftime('%Y-%m-%d')}"
            for s in sales
        ])
        
        
        suppliers_context = "\n".join([
            f"Fornecedor {s.name}: {s.contact}, entrega em {s.delivery_time} dias"
            for s in suppliers
        ])
        
        
        full_context = (
            f"Dados do estoque:\n{inventory_context}\n\n"
            f"Dados das vendas:\n{sales_context}\n\n"
            f"Dados dos fornecedores:\n{suppliers_context}"
        )
        
        
        response = chain.invoke({
            "inventory_context": full_context,
            "question": question
        })
        
        if not response:
            raise ValueError("Empty response from LangChain")
        
        return jsonify({
            'answer': response
        })
    
    except ValueError as ve:
        print(f"Validation error: {ve}")  
        return jsonify({'error': 'Invalid response from the AI model. Please refine your question.'}), 500
    except Exception as e:
        print(f"Error during query processing: {e}")  
        return jsonify({'error': 'An error occurred while processing the query. Please try again later.'}), 500


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='192.168.0.33', port=8080, debug=True)