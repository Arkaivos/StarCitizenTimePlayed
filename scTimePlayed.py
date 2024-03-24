import os
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Modify this path to point to the directory containing Star Citizen log files.
log_directory = r'C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\logbackups'

def parseTimestamp(timestamp_str):
    timestamp_pattern = r'<(\d{2}:\d{2}:\d{2})>|<(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)>'
    
    # Buscamos el "timestamp" en la cadena que recibimos como parámetro.
    match = re.search(timestamp_pattern, timestamp_str)
    if match:
        # Si el "timestamp" está en el formato ISO lo acortamos, para que nuestro programa trabaje siempre con el mismo formato.
        if match.group(2):
            timestamp_long = match.group(2)
            timestamp_short = timestamp_long[11:19] # Nos quedamos únicamente con la parte donde sale la hora, minuto y segundo.
            return timestamp_short
        else:
            # Si está en formato corto, lo devolvemos sin más.
            return match.group(1)
    else:
        return None

def calculateTimeDifference(start_time, end_time):
    # Convertimos las horas a objetos datetime para trabajar con ellos.
    start_datetime = datetime.strptime(start_time, '%H:%M:%S') if start_time else None
    end_datetime = datetime.strptime(end_time, '%H:%M:%S') if end_time else None
    
    if start_datetime is None or end_datetime is None:
        return None
    
    # Hay que tener en cuenta el cambio de día si la hora de fin es menor que la de inicio (Suponemos que cada sesión no dura varios días).
    if start_datetime > end_datetime:
        end_datetime += timedelta(days=1)
    
    # Calculamos el tiempo jugado en la sesión.
    time_difference = end_datetime - start_datetime
    return time_difference

def readLogFile(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Buscamos los timestamp de inicio y fin de la sesión.
    start_time = None
    end_time = None
    for line in lines:
        timestamp = parseTimestamp(line)
        if timestamp:
            if start_time is None:
                start_time = timestamp
            end_time = timestamp
    
    # Calculamos la diferencia de tiempo entre la hora de inicio y la de fin.
    if start_time and end_time:
        time_difference = calculateTimeDifference(start_time, end_time)
        return time_difference
    else:
        return None

def main():
    total_playtime = 0
    playtimes = []
    dates = []
    
    for filename in os.listdir(log_directory):
        if filename.endswith('.log'):
            file_path = os.path.join(log_directory, filename)
            playtime = readLogFile(file_path)
            if playtime:
                total_playtime += playtime.total_seconds()
                playtimes.append(playtime.total_seconds() / 3600)  # Convertir a horas
                date_str = re.search(r'(\d{2} \w+ \d{2})', filename).group(1)
                date = datetime.strptime(date_str, '%d %b %y').date()
                dates.append(date)
                print(f'Tiempo jugado en {filename}: {playtime}.')
    
    # Resultado final.
    total_playtime_hours = total_playtime // 3600
    total_playtime_minutes = (total_playtime % 3600) // 60
    total_playtime_seconds = total_playtime % 60
    print(f'Tiempo total jugado: {int(total_playtime_hours)} horas, {int(total_playtime_minutes)} minutos, {int(total_playtime_seconds)} segundos.')
    
    # Ordenamos las fechas y los tiempos jugados en función de las fechas, para mostrar en la gráfica.
    sorted_data = sorted(zip(dates, playtimes))
    dates = [x[0] for x in sorted_data]
    playtimes = [x[1] for x in sorted_data]
    
    # Calculamos el tiempo acumulado para la gráfica.
    cumulative_playtime = [sum(playtimes[:i+1]) for i in range(len(playtimes))]
    
    # Dibujamos la gráfica final.
    fig, ax1 = plt.subplots(figsize=(10, 6))

    colorSession = 'c'
    ax1.set_xlabel('Fecha.')
    ax1.set_ylabel('Tiempo jugado (horas).', color=colorSession)
    ax1.bar(dates, playtimes, label='Tiempo jugado por sesión.', color=colorSession)
    ax1.tick_params(axis='y', labelcolor=colorSession)

    ax2 = ax1.twinx()  
    colorCumulative = 'magenta'
    ax2.plot(dates, cumulative_playtime, label='Tiempo acumulado.', linestyle='--', color=colorCumulative)
    ax2.set_ylabel('Tiempo acumulado (horas).', color=colorCumulative)
    ax2.tick_params(axis='y', labelcolor=colorCumulative)

    plt.title('Tiempo jugado por sesión y tiempo acumulado.')
    fig.tight_layout()  
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()
