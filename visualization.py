"""
Fonctions de visualisation pour l'application
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List

def create_esg_gauge(score: float, title: str, max_value: float = 12) -> go.Figure:
    """
    Crée une jauge pour les scores ESG avec un style amélioré
    Score ESG : plus le score est bas, meilleure est la performance ESG
    """
    # Définition des couleurs pour les différentes zones
    colors = {
        'good': '#47d147',      # Vert pour les scores bas (bons)
        'medium': '#ffa64d',    # Orange pour les scores moyens
        'poor': '#ff4d4d',      # Rouge pour les scores élevés (mauvais)
        'bar': '#3366ff'        # Bleu pour la barre principale
    }

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': title,
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        number = {
            'font': {'size': 40, 'color': '#2c3e50'},
            'suffix': f"/{max_value}",
            'valueformat': '.1f'
        },
        gauge = {
            'axis': {
                'range': [0, max_value],
                'tickwidth': 2,
                'tickcolor': '#2c3e50',
                'tickfont': {'size': 14}
            },
            'bar': {'color': colors['bar'], 'thickness': 0.6},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#2c3e50',
            'steps': [
                {'range': [0, max_value/3], 'color': colors['good']},
                {'range': [max_value/3, 2*max_value/3], 'color': colors['medium']},
                {'range': [2*max_value/3, max_value], 'color': colors['poor']}
            ],
            'threshold': {
                'line': {'color': '#2c3e50', 'width': 4},
                'thickness': 0.8,
                'value': score
            }
        }
    ))

    # Mise à jour du layout pour un meilleur style
    fig.update_layout(
        paper_bgcolor = 'white',
        plot_bgcolor = 'white',
        margin = dict(t=60, b=20),
        height = 300,
        font = {'color': '#2c3e50'}
    )
    
    return fig

def create_sector_pie(sector_exposure: Dict[str, float]) -> go.Figure:
    """
    Crée un graphique en secteurs pour l'exposition sectorielle
    """
    labels = list(sector_exposure.keys())
    values = [v * 100 for v in sector_exposure.values()]
    
    # Palette de couleurs personnalisée
    colors = [
        '#FF9999', '#66B2FF', '#99FF99', '#FFCC99', 
        '#FF99CC', '#99FFCC', '#FFB366', '#99FF99'
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        textinfo='label+percent',
        textposition='outside',
        textfont={'size': 12, 'color': '#2c3e50'},
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=2)
        ),
        direction='clockwise',
        sort=False,
        showlegend=False
    )])
    
    fig.update_traces(
        hoverinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
    )
    
    fig.update_layout(
        title={
            'text': "Répartition Sectorielle",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=100, b=20, l=20, r=20),
        width=600,
        height=400,
        annotations=[
            dict(
                x=0.5,
                y=1.12,
                text="Exposition par secteur",
                showarrow=False,
                font=dict(size=14, color='#666666')
            )
        ]
    )
    
    return fig

def create_performance_chart(portfolio_values: pd.Series, 
                           benchmark_values: pd.Series = None) -> go.Figure:
    """
    Crée un graphique de performance comparée
    """
    fig = go.Figure()
    
    if not portfolio_values.empty:
        fig.add_trace(go.Scatter(
            x=portfolio_values.index,
            y=portfolio_values.values,
            name="Portefeuille",
            line=dict(color='#3366ff', width=3)
        ))
    
    if benchmark_values is not None and not benchmark_values.empty:
        fig.add_trace(go.Scatter(
            x=benchmark_values.index,
            y=benchmark_values.values,
            name="Benchmark",
            line=dict(color='#2c3e50', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title={
            'text': "Performance du Portefeuille",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        xaxis_title="Date",
        yaxis_title="Valeur (base 100)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=100, b=50, l=50, r=20)
    )
    
    # Grille en arrière-plan
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

def create_esg_radar(scores: Dict[str, float]) -> go.Figure:
    """
    Crée un graphique radar pour les scores ESG
    Note: Plus le score est bas, meilleure est la performance ESG
    Échelle: 0-12 avec zones colorées (vert 0-4, orange 4-8, rouge 8-12)
    """
    categories = ['Environmental', 'Social', 'Governance']
    
    # Utilisation directe des scores sans conversion (ils sont déjà sur ~12)
    values = [
        scores.get('environmental_score', 0),
        scores.get('social_score', 0),
        scores.get('governance_score', 0)
    ]
    
    # Calcul du score total sur 35 (échelle d'origine)
    total_score = scores.get('esg_score', 0)
    
    fig = go.Figure()
    
    # Création des secteurs colorés
    angles = np.linspace(0, 2*np.pi, len(categories)+1)
    for i in range(len(categories)):
        # Secteur rouge (8-12)
        fig.add_trace(go.Scatterpolar(
            r=[12, 12, 0],
            theta=[categories[i], categories[(i+1)%len(categories)], categories[i]],
            fill='toself',
            fillcolor='rgba(255, 77, 77, 0.8)',  # Rouge
            line=dict(width=0),
            showlegend=False
        ))
        
        # Secteur orange (4-8)
        fig.add_trace(go.Scatterpolar(
            r=[8, 8, 0],
            theta=[categories[i], categories[(i+1)%len(categories)], categories[i]],
            fill='toself',
            fillcolor='rgba(255, 166, 77, 0.8)',  # Orange
            line=dict(width=0),
            showlegend=False
        ))
        
        # Secteur vert (0-4)
        fig.add_trace(go.Scatterpolar(
            r=[4, 4, 0],
            theta=[categories[i], categories[(i+1)%len(categories)], categories[i]],
            fill='toself',
            fillcolor='rgba(71, 209, 71, 0.8)',  # Vert
            line=dict(width=0),
            showlegend=False
        ))
    
    # Ligne des données ESG
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  
        theta=categories + [categories[0]],  
        fill='toself',
        fillcolor='rgba(51, 102, 255, 0.7)', 
        line=dict(color='#3366ff', width=2),
        name="Scores ESG"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 12],
                tickfont={'size': 10},
                ticksuffix='',
                gridcolor='#f0f0f0',
                showline=False,
                tickvals=[4, 8, 12],
                ticktext=['4', '8', '12']
            ),
            angularaxis=dict(
                tickfont={'size': 14, 'color': '#2c3e50'},
                rotation=90,
                direction="clockwise"
            ),
            bgcolor='white'
        ),
        showlegend=False,
        title={
            'text': f"Performance ESG<br><sub>Score Total: {total_score:.1f}/35</sub>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        paper_bgcolor='white',
        margin=dict(t=100, b=50, l=50, r=50)
    )
    
    return fig

def create_risk_return_scatter(portfolio_data: List[Dict]) -> go.Figure:
    """
    Crée un nuage de points risque/rendement avec scores ESG
    Note: L'échelle de couleur est inversée car un score ESG bas est meilleur
    """
    df = pd.DataFrame(portfolio_data)
    
    fig = px.scatter(df,
                    x='volatility',
                    y='returns_1y',
                    size='market_cap',
                    color='esg_score',
                    hover_name='name',
                    color_continuous_scale='RdYlGn_r')  # Échelle inversée
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='#2c3e50')
        ),
        hovertemplate="<b>%{hovertext}</b><br>" +
                     "Volatilité: %{x:.1%}<br>" +
                     "Rendement: %{y:.1f}%<br>" +
                     "Score ESG: %{marker.color:.1f}/35<br>" +
                     "<extra></extra>"
    )
    
    fig.update_layout(
        title={
            'text': "Risque / Rendement / ESG<br><sub>(Score ESG plus bas = meilleure performance)</sub>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        xaxis_title="Volatilité",
        yaxis_title="Rendement 1 an",
        coloraxis_colorbar_title="Score ESG (/35)",
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=120, b=50, l=50, r=50)
    )
    
    # Grille en arrière-plan
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

def create_esg_components_table(stock_data: Dict) -> go.Figure:
    """
    Crée un tableau détaillé des composantes ESG
    """
    headers = ['Composante', 'Score', 'Description']
    values = [
        ['Environmental', 'Social', 'Governance', 'Total'],
        [
            f"{stock_data.get('environmental_score', 0):.1f}/35",
            f"{stock_data.get('social_score', 0):.1f}/35",
            f"{stock_data.get('governance_score', 0):.1f}/35",
            f"{stock_data.get('esg_score', 0):.1f}/35"
        ],
        [
            "Impact environnemental (score bas = meilleur)",
            "Impact social et communautaire (score bas = meilleur)",
            "Qualité de la gouvernance (score bas = meilleur)",
            "Score ESG global (score bas = meilleur)"
        ]
    ]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=headers,
            fill_color='#3366ff',
            align='left',
            font=dict(size=14, color='white')
        ),
        cells=dict(
            values=values,
            fill_color=['rgba(51, 102, 255, 0.1)'],
            align='left',
            font=dict(size=12, color='#2c3e50')
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Détail des Scores ESG<br><sub>(Score plus bas = meilleure performance)</sub>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        margin=dict(t=120, b=20, l=20, r=20),
        paper_bgcolor='white'
    )
    
    return fig