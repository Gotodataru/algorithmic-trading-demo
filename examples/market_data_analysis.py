"""
Пример анализа рыночных данных
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def generate_sample_data(days: int = 30):
    """Генерация примерных рыночных данных"""
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    
    # Генерируем случайные цены с трендом
    np.random.seed(42)
    base_price = 100
    trend = np.linspace(0, 0.1, len(dates))  # Восходящий тренд
    noise = np.random.randn(len(dates)) * 0.5
    
    prices = base_price + trend * 100 + noise.cumsum()
    
    data = pd.DataFrame({
        'open': prices - np.random.rand(len(dates)) * 0.5,
        'high': prices + np.random.rand(len(dates)) * 0.8,
        'low': prices - np.random.rand(len(dates)) * 0.8,
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    return data

def analyze_data(data: pd.DataFrame):
    """Анализ рыночных данных"""
    print("=== Рыночные данные ===")
    print(f"Период: {data.index[0]} - {data.index[-1]}")
    print(f"Количество записей: {len(data)}")
    print(f"Символов: 1 (демо)")
    print()
    
    print("=== Статистика цен ===")
    print(f"Цена открытия: {data['open'].mean():.2f} ± {data['open'].std():.2f}")
    print(f"Цена закрытия: {data['close'].mean():.2f} ± {data['close'].std():.2f}")
    print(f"Минимальная цена: {data['low'].min():.2f}")
    print(f"Максимальная цена: {data['high'].max():.2f}")
    print()
    
    print("=== Статистика объема ===")
    print(f"Средний объем: {data['volume'].mean():.0f}")
    print(f"Максимальный объем: {data['volume'].max():.0f}")
    print(f"Минимальный объем: {data['volume'].min():.0f}")
    print()
    
    # Простые индикаторы
    data['returns'] = data['close'].pct_change() * 100
    data['volatility'] = data['returns'].rolling(24).std()  # Дневная волатильность
    
    print("=== Доходность и волатильность ===")
    print(f"Средняя дневная доходность: {data['returns'].mean():.4f}%")
    print(f"Волатильность доходности: {data['returns'].std():.4f}%")
    print(f"Максимальная дневная доходность: {data['returns'].max():.4f}%")
    print(f"Минимальная дневная доходность: {data['returns'].min():.4f}%")

def plot_data(data: pd.DataFrame):
    """Визуализация данных"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # График цен
    axes[0, 0].plot(data.index, data['close'], label='Close Price', linewidth=1)
    axes[0, 0].set_title('Цена закрытия')
    axes[0, 0].set_xlabel('Дата')
    axes[0, 0].set_ylabel('Цена')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # График объема
    axes[0, 1].bar(data.index, data['volume'], alpha=0.7, width=0.02)
    axes[0, 1].set_title('Объем торгов')
    axes[0, 1].set_xlabel('Дата')
    axes[0, 1].set_ylabel('Объем')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Гистограмма доходности
    axes[1, 0].hist(data['returns'].dropna(), bins=50, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Распределение доходности')
    axes[1, 0].set_xlabel('Доходность (%)')
    axes[1, 0].set_ylabel('Частота')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Скользящая волатильность
    axes[1, 1].plot(data.index, data['volatility'], label='Волатильность (24ч)', color='red')
    axes[1, 1].set_title('Волатильность')
    axes[1, 1].set_xlabel('Дата')
    axes[1, 1].set_ylabel('Волатильность (%)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('market_analysis.png', dpi=150, bbox_inches='tight')
    print("Графики сохранены в 'market_analysis.png'")

if __name__ == "__main__":
    print("Генерация демонстрационных данных...")
    data = generate_sample_data(days=30)
    
    print("\nАнализ данных...")
    analyze_data(data)
    
    print("\nСоздание графиков...")
    plot_data(data)
    
    print("\nАнализ завершен!")