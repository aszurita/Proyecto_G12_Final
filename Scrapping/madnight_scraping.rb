require 'selenium-webdriver'
require 'csv'

puts 'MADNIGHT GitHub Scraper'

class MadnightScraper
  def initialize(url_base)
    @url_base = url_base
    @driver = nil
    setup_driver
  end

  def setup_driver
    options = Selenium::WebDriver::Chrome::Options.new
    
    # Configuración para ejecución en modo headless (sin ventana)
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Desactivar logs innecesarios
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    
    # Configurar preferencias
    options.add_preference('profile.default_content_setting_values.notifications', 2)
    
    @driver = Selenium::WebDriver.for :chrome, options: options
    @driver.manage.timeouts.implicit_wait = 10
    
    puts "Navegador Chrome iniciado..."
    @driver.navigate.to @url_base
    sleep(3) # Esperar a que cargue completamente la página
    puts "Página cargada: #{@url_base}"
  rescue => e
    puts "Error al iniciar el navegador: #{e.message}"
    raise
  end

  def ejecutar
    puts "\n" + "="*60
    puts "  MADNIGHT GITHUB SCRAPER - PULL REQUESTS"
    puts "="*60
    puts "Período: 2020-2024 | Quarters: 1-4 | Métrica: Pull Requests"
    puts "="*60 + "\n"
    
    begin
      extraer_datos_completos
      puts "\n" + "="*60
      puts "EXTRACCIÓN COMPLETADA CON ÉXITO"
      puts "="*60 + "\n"
    rescue => e
      puts "\n" + "="*60
      puts "ERROR DURANTE LA EXTRACCIÓN"
      puts "="*60
      puts "Error: #{e.message}"
      puts "Backtrace:"
      puts e.backtrace.first(5).join("\n")
    ensure
      @driver.quit if @driver
      puts "\nNavegador cerrado"
    end
  end

  def extraer_datos_completos
    puts "Generando archivo: MadnightPullRequests.csv\n"
    
    CSV.open("Datos/MadnightPullRequests.csv", "w") do |csv|
      csv << ["Año", "Quarter", "Ranking", "Lenguaje", "Porcentaje"]
      
      # Click en Pull Requests
      click_pull_requests
      
      total_registros = 0
      # Iterar por años (2020-2024)
      (2020..2024).each do |anio|
        puts "\nProcesando año: #{anio}"
        
        # Iterar por quarters (1-4)
        (1..4).each do |quarter|
          puts "Quarter #{quarter}..."
          
          begin
            seleccionar_anio(anio)
            seleccionar_quarter(quarter)
            sleep(3) # Esperar a que se actualice la tabla  
            # Extraer datos de la tabla
            registros = extraer_tabla(csv, anio, quarter)
            total_registros += registros
          rescue => e
            puts "Error en #{anio}-Q#{quarter}: #{e.message}"
            # Continuar con el siguiente quarter
          end
        end
      end
      
      puts "\nTotal de registros extraídos: #{total_registros}"
    end
  end

  def click_pull_requests
    # Buscar el botón de Pull Requests por su texto
    boton = @driver.find_element(:xpath, "//button[contains(text(), 'pull requests')]")
    boton.click
    sleep(2)
    puts "Botón 'Pull Requests' clickeado"
  end

  def seleccionar_anio(anio)
    # Hacer click en el contenedor del selector de año (esto es react-select)
    begin
      year_container = @driver.find_element(:xpath, "//h4[text()='Year']/following-sibling::div")
      # Hacer click en el control (el div clickeable del selector)
      control = year_container.find_element(:css, "div[class*='control']")
      control.click
      sleep(1)
      # Ahora buscar la opción en el menú desplegado
      # Las opciones aparecen en un div con clase que contiene "option"
      option = @driver.find_element(:xpath, "//div[contains(@class, 'option') and text()='#{anio}']")
      option.click
      sleep(1)
      puts "Año seleccionado: #{anio}"
    rescue => e
      puts "Error seleccionando año #{anio}: #{e.message}"
      raise
    end
  end

  def seleccionar_quarter(quarter)
    # Hacer click en el contenedor del selector de quarter
    begin
      quarter_container = @driver.find_element(:xpath, "//h4[text()='Quarter']/following-sibling::div")
      control = quarter_container.find_element(:css, "div[class*='control']")
      control.click
      sleep(1)
      
      option = @driver.find_element(:xpath, "//div[contains(@class, 'option') and text()='#{quarter}']")
      option.click
      sleep(1)
      puts "Quarter seleccionado: #{quarter}"
    end
    rescue => e
      puts "Error seleccionando quarter #{quarter}: #{e.message}"
  end

  def extraer_tabla(csv, anio, quarter)
    filas = @driver.find_elements(:css, "table.table tbody tr")
    contador = 0
    filas.each do |fila|
      begin
        # Extraer las tres celdas: ranking, lenguaje, porcentaje
        celdas = fila.find_elements(:css, "td")
        next if celdas.length < 3
        
        ranking = celdas[0].text.strip
        lenguaje = celdas[1].text.strip
        # El porcentaje está dentro de un div en la tercera celda
        porcentaje_div = celdas[2].find_element(:css, "div")
        porcentaje_raw = porcentaje_div.text.strip
        # Limpiar el porcentaje
        porcentaje = porcentaje_raw.gsub(/[^0-9.]/, '').strip
        
        csv << [anio, quarter, ranking, lenguaje, porcentaje]
        contador += 1
      rescue => e
        # Ignorar filas con errores y continuar
      end
    end
    puts "#{contador} lenguajes extraídos"
    
    return contador
  end
end

# Ejecutar el scraper
begin
  scraper = MadnightScraper.new('https://madnight.github.io/githut/')
  scraper.ejecutar
  puts "\nArchivo generado con éxito: MadnightPullRequests.csv"
rescue => e
  puts "Error: #{e.message}"
  puts e.backtrace
end