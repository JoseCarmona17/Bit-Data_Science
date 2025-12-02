import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Cargar dataset
df = pd.read_csv("Amazon.csv")

# Convertir columna fecha
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")

# Crear columna de ventas
df["Sales"] = df["Quantity"] * df["UnitPrice"]

# Se convierte la fecha a formato datetime
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")

# Crear app Dash
app = Dash(__name__)
server = app.server 

# Layout
app.layout = html.Div([

    html.H1("Dashboard Interactivo - Amazon Orders", 
            style={"textAlign": "center", "color": "#222"}),

    html.Br(),

    # FILTROS
    html.Div([
        html.Div([
            html.Label("Método de Pago:"),
            dcc.Dropdown(
                id="payment-filter",
                options=[{"label": p, "value": p} for p in sorted(df["PaymentMethod"].unique())],
                placeholder="Seleccione método de pago",
                value=None
            )
        ], style={"width": "23%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("País:"),
            dcc.Dropdown(
                id="country-filter",
                options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
                placeholder="Seleccione país",
                value=None
            )
        ], style={"width": "23%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("Estado:"),
            dcc.Dropdown(
                id="state-filter",
                placeholder="Seleccione estado",
                value=None
            )
        ], style={"width": "23%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("Ciudad:"),
            dcc.Dropdown(
                id="city-filter",
                placeholder="Seleccione ciudad",
                value=None
            )
        ], style={"width": "23%", "display": "inline-block"}),
    ]),

    html.Br(),
    
    # Contenedor de graficas
    dcc.Graph(id="sales-by-category"),
    dcc.Graph(id="sales-by-brand"),
    dcc.Graph(id="sales-by-city"),
    dcc.Graph(id="sales-trend"),
    dcc.Graph(id="payment-pie"),

])

# Callbacks para actualizar los estados segun el pais
@app.callback(
    Output("state-filter", "options"),
    Input("country-filter", "value")
)
def update_states(country):
    if country:
        states = sorted(df[df["Country"] == country]["State"].unique())
        return [{"label": s, "value": s} for s in states]
    return []

# Actualizar lista de ciudades según estado
@app.callback(
    Output("city-filter", "options"),
    Input("state-filter", "value")
)
def update_cities(state):
    if state:
        cities = sorted(df[df["State"] == state]["City"].unique())
        return [{"label": c, "value": c} for c in cities]
    return []


# Gráficas principales
@app.callback(
    [
        Output("sales-by-category", "figure"),
        Output("sales-by-brand", "figure"),
        Output("sales-by-city", "figure"),
        Output("sales-trend", "figure"),
        Output("payment-pie", "figure"),
    ],
    [
        Input("payment-filter", "value"),
        Input("country-filter", "value"),
        Input("state-filter", "value"),
        Input("city-filter", "value"),
    ]
)

def update_graphs(payment, country, state, city):

    filtered = df.copy()

    if payment:
        filtered = filtered[filtered["PaymentMethod"] == payment]
    if country:
        filtered = filtered[filtered["Country"] == country]
    if state:
        filtered = filtered[filtered["State"] == state]
    if city:
        filtered = filtered[filtered["City"] == city]

    # 1. Categorías 
    fig1 = px.bar(
        filtered.groupby("Category")["Sales"].sum().reset_index(),
        x="Category",
        y="Sales",
        title="Ventas por Categoría",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # 2. Marcas 
    fig2 = px.bar(
        filtered.groupby("Brand")["Sales"].sum().reset_index(),
        x="Brand",
        y="Sales",
        title="Ventas por Marca",
        color="Brand",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # 3. Ciudades – Top 15
    fig3 = px.bar(
        filtered.groupby("City")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(15),
        x="City",
        y="Sales",
        title="Top 15 Ciudades con Más Ventas",
        color="Sales",
        color_continuous_scale="Blues"
    )

    # 4. Tendencia de ventas
    fig4 = px.line(
        filtered.groupby("OrderDate")["Sales"].sum().reset_index(),
        x="OrderDate",
        y="Sales",
        title="Tendencia de Ventas en el Tiempo",
        markers=True,
        color_discrete_sequence=["#d62728"]
    )

    # 5. Metodos de pago
    fig5 = px.pie(
        filtered,
        names="PaymentMethod",
        title="Distribución de Métodos de Pago",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    return fig1, fig2, fig3, fig4, fig5



# Ejecución local
if __name__ == "__main__":
    app.run(debug=True)
