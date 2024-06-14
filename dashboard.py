import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
from db import engine, Product, Category, Order, Customer, Seller
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import plotly.graph_objects as go
from main import run_schedule
from threading import Thread


## Consultas 
Session = sessionmaker(bind=engine)
session = Session()
topsell = (
    session.query(
      Product.name,
      func.sum(Order.quantity).label('total_quantity')
    )
    .join(Order, Product.id == Order.product_id)
    .group_by(Product.name)
    .order_by(func.sum(Order.quantity).desc())
    .limit(5)
    .all()
)

topcategory = (
    session.query(
      Category.name,
      func.sum(Order.quantity).label('total_quantity')
    )
    .join(Product, Order.product_id == Product.id)
    .join(Category, Category.id == Product.category_id)
    .group_by(Category.name,)
    .order_by(func.sum(Order.quantity).desc())
    .limit(5)
    .all()
)

topcustomer = (
  session.query(  
    Customer.customer_id,
    func.count(Order.id).label('total_orders')
  )
  .join(Order, Customer.id == Order.customer_id)
  .group_by(Customer.id)
  .order_by(func.count(Order.id).desc())
  .limit(5)
  .all()
)

topspends = (
  session.query(
    Customer.customer_id,
    func.sum(Order.payment).label('total_spends')
  )
  .join(Order, Customer.id == Order.customer_id)
  .group_by(Customer.id)
  .order_by(func.sum(Order.payment).desc())
  .limit(5)
  .all()
)

avg_rating = (
    session.query(
      Product.name,
      func.avg(Order.rating).label('average_rating')
    )
    .join(Order, Product.id == Order.product_id)
    .group_by(Product.name)
    .order_by(func.sum(Order.quantity).desc())
    .limit(5)
    .all()
)

dist_payments_methods = (
  session.query(
    Order.payment_type,
    func.count(Order.id).label('total_orders')
  )
  .group_by(Order.payment_type)
  .limit(5)
  .all()
)

city_purchases = (
  session.query(
    Customer.city,
    func.count(Order.id).label('total_orders')
  )
  .join(Order, Customer.id == Order.customer_id)
  .group_by(Customer.city)
  .limit(5)
  .all()
)

order_status = (
  session.query(
    Order.order_status,
    func.count(Order.id).label('total_orders')
  )
  .group_by(Order.order_status)
  .all()
)

weight_products = (
  session.query(
    Product.name,
    func.avg(Order.weight).label('average_weight')
  )
  .join(Order, Product.id == Order.product_id)
  .group_by(Product.name)
  .order_by(func.avg(Order.weight).desc())
  .limit(5)
  .all()
)

timestamp = (
  session.query(
    Order.timestamp,
    func.count(Order.id).label('total_orders')
  )
  .group_by(Order.timestamp)
  .order_by(Order.timestamp)
  .all()
)

df_topsell = pd.DataFrame(topsell, columns=['name', 'total_quantity'])
df_topcategory = pd.DataFrame(topcategory, columns=['name', 'total_quantity'])
df_topcustomer = pd.DataFrame(topcustomer, columns=['customer_id', 'total_orders'])
df_topspends = pd.DataFrame(topspends, columns=['customer_id', 'total_spends'])
df_avg_rating = pd.DataFrame(avg_rating, columns=['name', 'average_rating'])
df_payments_methods = pd.DataFrame(dist_payments_methods, columns=['payment_type', 'total_orders'])
df_city_purchases = pd.DataFrame(city_purchases, columns=['city', 'total_purchases'])
df_status = pd.DataFrame(order_status, columns=['status', 'total_orders'])
df_weight_products = pd.DataFrame(weight_products, columns=['name', 'average_weight'])
df_timestamp = pd.DataFrame(timestamp, columns=['timestamp', 'total_orders'])

app = dash.Dash(__name__)
server = app.server
thread = Thread(target=run_schedule)
thread.start()

# Definir el layout de la app
app.layout = html.Div([
    html.H1("Tarea 3"),
    html.Div([
        dcc.Graph(id='bar-chart-products', style={'height': '50vh'}),
        dcc.Graph(id='bar-chart-categories', style={'height': '50vh'}),
        dcc.Graph(id='bar-chart-customer', style={'height': '50vh'}),
        dcc.Graph(id='bar-chart-spends', style={'height': '50vh'}),
        dcc.Graph(id='bar-chart-rating', style={'height': '50vh'}),
        dcc.Graph(id='pie-chart-payments', style={'height': '50vh'}),
        dcc.Graph(id='pie-chart-city', style={'height': '50vh'}),
        dcc.Graph(id='stacked-bar-chart-status', style={'height': '50vh'}),
        dcc.Graph(id='bar-chart-weight', style={'height': '50vh'}),
        dcc.Graph(id='line-chart-timestamp', style={'height': '50vh'})
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px'})
])
# Definir las interacciones
@app.callback(
    [Output('bar-chart-products', 'figure'),
      Output('bar-chart-categories', 'figure'),
      Output('bar-chart-customer', 'figure'),
      Output('bar-chart-spends', 'figure'),
      Output('bar-chart-rating', 'figure'),
      Output('pie-chart-payments', 'figure'),
      Output('pie-chart-city', 'figure'),
      Output('stacked-bar-chart-status', 'figure'),
      Output('bar-chart-weight', 'figure'),
      Output('line-chart-timestamp', 'figure')
     ],
    [Input('bar-chart-products', 'id'),
      Input('bar-chart-categories', 'id'),
      Input('bar-chart-customer', 'id'),
      Input('bar-chart-spends', 'id'),
      Input('bar-chart-rating', 'id'),
      Input('pie-chart-payments', 'id'),
      Input('pie-chart-city', 'id'),
      Input('stacked-bar-chart-status', 'id'),
      Input('bar-chart-weight', 'id'),
      Input('line-chart-timestamp', 'id')
     ]
)

def update_graph(_, __, ___, ____, _____, ______, _______, ________, _________, __________):
    # Gráfico de barras horizontales para productos
    fig_products = go.Figure()

    fig_products.add_trace(go.Bar(
        y=df_topsell['name'],
        x=df_topsell['total_quantity'],
        orientation='h',
        marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
    ))

    fig_products.update_layout(
        title="Top 5 Productos Más Comprados",
        xaxis_title="Cantidad de productos",
        yaxis_title="Producto",
        yaxis=dict(autorange="reversed"),  # Reversing the y-axis to match the order in the example image
        margin=dict(l=150)  # Ajuste del margen izquierdo para espacio de leyenda

    )

    # Gráfico de barras verticales para categorías
    fig_categories = go.Figure()

    fig_categories.add_trace(go.Bar(
        x=df_topcategory['name'],
        y=df_topcategory['total_quantity'],
        marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
    ))

    fig_categories.update_layout(
        title="Top 5 Categorías Más Compradas",
        xaxis_title="Categoría",
        yaxis_title="Cantidad de productos",
        xaxis=dict(tickangle=0, tickmode='array', tickvals=df_topcategory['name'], ticktext=[f'{name[:10]}<br>{name[10:]}' if len(name) > 10 else name for name in df_topcategory['name']]),
        margin=dict(l=50, r=50, t=50, b=50)  # Ajuste de márgenes
    )
    
    fig_customers = go.Figure()

    fig_customers.add_trace(go.Bar(
        y=df_topcustomer['customer_id'],
        x=df_topcustomer['total_orders'],
        orientation='h',
        marker=dict(color='rgba(255, 165, 0, 0.6)', line=dict(color='rgba(255, 165, 0, 1.0)', width=3))
    ))

    fig_customers.update_layout(
        title="Top 5 Clientes Más Compradores",
        xaxis_title="Cantidad de órdenes",
        yaxis_title="ID de Cliente",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=150)  # Ajuste del margen izquierdo para espacio de leyenda
    )
    fig_spends = go.Figure()

    fig_spends.add_trace(go.Bar(
        y=df_topspends['total_spends'],
        x=df_topspends['customer_id'],
        marker=dict(color='rgba(255, 165, 0, 0.6)', line=dict(color='rgba(255, 165, 0, 1.0)', width=3))
    ))

    fig_spends.update_layout(
        title="Top 5 Clientes que más gastan",
        xaxis_title="Total de gastos",
        yaxis_title="ID de Cliente",
        xaxis=dict(tickangle=0, tickmode='array', tickvals=df_topspends['customer_id'], ticktext=[f'{name[:10]}<br>{name[10:20]}<br>{name[20:]}' if len(name) > 10 else name for name in df_topspends['customer_id']]),
    )

    fig_rating = go.Figure()
    fig_rating.add_trace(go.Bar(
        x=df_avg_rating['name'],
        y=df_avg_rating['average_rating'],
        marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
    ))
    fig_rating.update_layout(
        title="Calificación Promedio de los Productos Comprados",
        xaxis_title="Producto",
        yaxis_title="Calificación Promedio",
        xaxis=dict(tickangle=0, tickmode='array', tickvals=df_avg_rating['name'], ticktext=[f'{name[:15]}<br>{name[15:30]}<br>{name[30:45]}<br>{name[45:60]}<br>{name[60:]}' if len(name) > 10 else name for name in df_avg_rating['name']]),
        margin=dict(l=50, r=50, t=50, b=50)  # Ajuste de márgenes
    )


    fig_payments = go.Figure()

    fig_payments.add_trace(go.Pie(
        labels=df_payments_methods['payment_type'],
        values=df_payments_methods['total_orders'],
        hole=0.3,
    ))

    fig_payments.update_layout(
        title="Top 5 Métodos de Pago"
    )

    fig_city = go.Figure()

    fig_city.add_trace(go.Pie(
        labels=df_city_purchases['city'],
        values=df_city_purchases['total_purchases'],
        hole=0.3,
    ))
    fig_city.update_layout(
        title="Top 5 Ciudades con Más Compras Realizadas",
        margin=dict(l=50, r=50, t=50, b=50)  # Ajuste de márgenes
    )


    fig_status = go.Figure()

    fig_status.add_trace(go.Bar(
      x=df_status['status'],
      y=df_status['total_orders'],
      marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
    ))

    fig_status.update_layout(
      title="Estado de las órdenes",
      xaxis_title="Estado",
      yaxis_title="Cantidad de órdenes",
      xaxis=dict(tickangle=0, tickmode='array', tickvals=df_status['status'], ticktext=[f'{name[:10]}<br>{name[10:20]}<br>{name[20:]}' if len(name) > 10 else name for name in df_status['status']]),
      margin=dict(l=50, r=50, t=50, b=50),  # Ajuste de márgenes
      barmode='stack'  # Configuración para grafico de barras apiladas
    )

    fig_weight = go.Figure()
    fig_weight.add_trace(go.Bar(
      x=df_weight_products['name'],
      y=df_weight_products['average_weight'],
      marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
    ))
    fig_weight.update_layout(
      title="Top 5 Productos más pesados",
      xaxis_title="Producto",
      yaxis_title="Peso promedio",
      xaxis=dict(tickangle=0, tickmode='array', tickvals=df_weight_products['name'], ticktext=[f'{name[:15]}<br>{name[15:30]}<br>{name[30:45]}<br>{name[45:60]}<br>{name[60:]}' if len(name) > 10 else name for name in df_weight_products['name']]),
      margin=dict(l=50, r=50, t=50, b=50)  # Ajuste de márgenes
    )

    fig_timestamp = go.Figure()
    fig_timestamp.add_trace(go.Scatter
    (
      x=df_timestamp['timestamp'],
      y=df_timestamp['total_orders'],
      mode='lines+markers'
    ))

    fig_timestamp.update_layout(
      title="Cantidad de órdenes por fecha",
      xaxis_title="Fecha",
      yaxis_title="Cantidad de órdenes",
      margin=dict(l=50, r=50, t=50, b=50)  # Ajuste de márgenes
    )
    
    return (
      fig_products,
      fig_categories, 
      fig_customers,
      fig_spends,
      fig_rating,
      fig_payments,
      fig_city,
      fig_status,
      fig_weight,
      fig_timestamp
    )
# Ejecutar la app
if __name__ == '__main__':
    print('Running app...')
    app.run_server(debug=True)