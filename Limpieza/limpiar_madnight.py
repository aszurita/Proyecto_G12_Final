import pandas as pd
import re

print("LIMPIEZA DE DATOS - MADNIGHT PULL REQUESTS")
df = pd.read_csv('Datos/MadnightPullRequests.csv')

print(f"\nDatos originales: {len(df)} registros")
print(f"Columnas: {list(df.columns)}")

# Función para limpiar porcentajes
def limpiar_porcentaje(valor):
    """
    Extrae solo el porcentaje principal del valor
    Ej: '17.4850.254' -> '17.485'
        '0.107' -> '0.107'
    """
    valor_str = str(valor)
    match = re.match(r'(\d+\.\d+)', valor_str)
    if match:
        return float(match.group(1))
    # Si no tiene punto decimal, devolver como está
    try:
        return float(valor_str)
    except:
        return 0.0

# Aplicar limpieza
print("\nLimpiando columna 'Porcentaje'...")
df['Porcentaje'] = df['Porcentaje'].apply(limpiar_porcentaje)

# Verificar si hay valores nulos o inválidos
print(f"\nValores nulos: {df['Porcentaje'].isnull().sum()}")
print(f"Valores cero: {(df['Porcentaje'] == 0).sum()}")

# Guardar el CSV limpio
output_file = 'Datos_procesados/MadnightPullRequests_cleaned.csv'
df.to_csv(output_file, index=False)
print(f"\nArchivo guardado: {output_file}")

# Mostrar información adicional
print(f"\nInformación general:")
print(f"  • Años únicos: {sorted(df['Año'].unique())}")
print(f"  • Quarters únicos: {sorted(df['Quarter'].unique())}")
print(f"  • Total de lenguajes únicos: {df['Lenguaje'].nunique()}")

