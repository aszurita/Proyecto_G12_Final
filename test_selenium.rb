require 'selenium-webdriver'

puts "="*60
puts "  TEST DE SELENIUM - VERIFICACIÓN DE INSTALACIÓN"
puts "="*60

begin
  puts "\n1. Iniciando navegador Chrome..."
  options = Selenium::WebDriver::Chrome::Options.new
  options.add_argument('--headless=new')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  
  driver = Selenium::WebDriver.for :chrome, options: options
  puts "   ✓ Navegador Chrome iniciado correctamente"
  
  puts "\n2. Navegando a MADNIGHT GitHub..."
  driver.navigate.to 'https://madnight.github.io/githut/'
  sleep(3)
  puts "   ✓ Página cargada"
  
  puts "\n3. Verificando elementos clave..."
  
  # Verificar botón Pull Requests
  boton_pr = driver.find_element(:xpath, "//button[contains(text(), 'pull requests')]")
  puts "   ✓ Botón 'Pull Requests' encontrado"
  
  # Verificar selector de año
  selector_year = driver.find_element(:xpath, "//h4[text()='Year']")
  puts "   ✓ Selector de 'Year' encontrado"
  
  # Verificar selector de quarter
  selector_quarter = driver.find_element(:xpath, "//h4[text()='Quarter']")
  puts "   ✓ Selector de 'Quarter' encontrado"
  
  # Verificar tabla
  tabla = driver.find_element(:css, "table.table")
  puts "   ✓ Tabla de datos encontrada"
  
  puts "\n4. Extrayendo una muestra de datos..."
  boton_pr.click
  sleep(2)
  
  filas = driver.find_elements(:css, "table.table tbody tr")
  puts "   ✓ Se encontraron #{filas.length} filas en la tabla"
  
  if filas.length > 0
    primera_fila = filas[0]
    celdas = primera_fila.find_elements(:css, "td")
    
    ranking = celdas[0].text.strip
    lenguaje = celdas[1].text.strip
    porcentaje = celdas[2].text.strip
    
    puts "\n   Ejemplo de datos extraídos:"
    puts "   - Ranking: #{ranking}"
    puts "   - Lenguaje: #{lenguaje}"
    puts "   - Porcentaje: #{porcentaje}"
  end
  
  puts "\n" + "="*60
  puts "  ✓ TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE"
  puts "="*60
  puts "\n¡Selenium está funcionando correctamente!"
  puts "Puedes ejecutar ahora: ruby madnight_scraper.rb\n\n"
  
  driver.quit
  
rescue Selenium::WebDriver::Error::WebDriverError => e
  puts "\n✗ Error de Selenium:"
  puts "  #{e.message}"
  puts "\nPosibles soluciones:"
  puts "  1. Instala ChromeDriver: sudo apt-get install chromium-chromedriver"
  puts "  2. Verifica la versión de Chrome: google-chrome --version"
  puts "  3. Instala la gema: gem install selenium-webdriver"
  
rescue => e
  puts "\n✗ Error inesperado:"
  puts "  #{e.message}"
  puts "\nBacktrace:"
  puts e.backtrace.first(5).join("\n")
end