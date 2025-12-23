require 'open-uri'
require 'nokogiri'
require 'csv'

puts 'TIOBE'
class TiobeNavegador
  def initialize(url_base)
    @url_base = url_base
    @html_main = URI.open(@url_base).read
    @parsed_main = Nokogiri::HTML(@html_main)
  end

  def ejecutar
    extraer_ranking
    extraer_todas_las_series
  end

  def extraer_ranking
    puts "Generando RankingTIOBE2025.csv..."
    CSV.open("RankingTIOBE2025.csv", "w") do |csv|
      csv << ["Rank Dec 2025", "Rank Dec 2024", "Language", "Ratings", "Change"]

      # Tabla Top 20
      @parsed_main.css('table#top20 tbody tr').each do |fila|
        celdas = fila.css('td')
        csv << [celdas[0].text.strip, celdas[1].text.strip, celdas[4].text.strip, celdas[5].text.strip, celdas[6].text.strip]
      end

      # Tabla otros (21-50)
      @parsed_main.css('table#otherPL tbody tr').each do |fila|
        celdas = fila.css('td')
        csv << [celdas[0].text.strip, "n/a", celdas[1].text.strip, celdas[2].text.strip, "n/a"]
      end
    end
  end

  def extraer_todas_las_series
    puts "Navegando por cada lenguaje para extraer series de tiempo..."
    
    CSV.open("Series_de_Tiempo.csv", "w") do |csv|
      csv << ["Language", "Date", "Rating"]

      lenguajes = @parsed_main.css('table#top20 tbody tr td:nth-child(5)').map(&:text)

      lenguajes.each do |nombre|
        begin
          slug = nombre.downcase.gsub(' ', '-').gsub('#', 'sharp').gsub('++', 'plusplus')
          url_individual = "https://www.tiobe.com/tiobe-index/#{slug}/"
          
          puts "Escrapeando detalles de: #{nombre}..."
          
          html_detalle = URI.open(url_individual).read
          parsed_detalle = Nokogiri::HTML(html_detalle)

          # Buscar el script de Highcharts en la página interna
          script_nodo = parsed_detalle.css('script').find { |s| s.text.include?('series: [') }
          next unless script_nodo

          # Extraer datos usando el Regex del ejercicio anterior
          script_data = script_nodo.text
          bloque_datos = script_data.match(/data\s*:\s*\[(.*?)\]\s*\}/m)[1]
          
          puntos = bloque_datos.scan(/Date\.UTC\((\d+),\s*(\d+),\s*(\d+)\),\s*([\d.]+)/)
          
          puntos.each do |anio, mes, dia, valor|
            fecha = "#{anio}-#{(mes.to_i + 1).to_s.rjust(2, '0')}-#{dia.rjust(2, '0')}"
            csv << [nombre, fecha, valor]
          end
        rescue => e
          puts "Error al procesar #{nombre}: #{e.message}"
        end
      end
    end
  end
end

navegador = TiobeNavegador.new('https://www.tiobe.com/tiobe-index/')
navegador.ejecutar

puts "\nArchivos generados con éxito."