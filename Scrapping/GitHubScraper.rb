require 'open-uri'
require 'nokogiri'
require 'csv'

puts 'Scraping GitHub'

class GithubScraper
  BASE_URL = "https://github.com"
  TRENDING_URL = "#{BASE_URL}/trending"
  LANGUAGES = ["python", "c", "cpp", "c%23", "java", "javascript", "assembly", "r", "perl", "fortran", "rust", "matlab", "php", "go", "kotlin"]

  def initialize
    @archivo_top_repos = "Datos/TopRepositorios.csv"
    @archivo_top_lenguajes = "Datos/TopReposXLenguajes.csv"
    inicializar_archivos_csv
  end

  def ejecutar
    extraer_top_repositorios
    extraer_top_por_lenguaje
  end

  private

  def inicializar_archivos_csv
    crear_csv(@archivo_top_repos, ["Repository", "User", "URL", "Language", "NumberOfStar", "NumberOfFork"])
    crear_csv(@archivo_top_lenguajes, ["Language", "Repository", "User", "URL", "NumberOfStar", "NumberOfFork"])
  end

  def crear_csv(nombre_archivo, encabezados)
    CSV.open(nombre_archivo, "w") do |csv|
      csv << encabezados
    end
  end

  def extraer_top_repositorios
    puts "\nScrapeando Top Repositorios..."
    parsed_content = obtener_contenido_parseado(TRENDING_URL)
    repositorios = parsed_content.css('div[data-hpc] article.Box-row')

    repositorios.each do |repo|
      datos = extraer_datos_repositorio(repo)
      guardar_en_csv(@archivo_top_repos, [
        datos[:nombre_repo],
        datos[:nombre_user],
        datos[:url],
        datos[:lenguaje],
        datos[:estrellas],
        datos[:forks]
      ])
    end
  end

  def extraer_top_por_lenguaje
    puts "\nScrapeando Top Repositorio por Lenguaje..."

    LANGUAGES.each do |lenguaje|
      url = "#{TRENDING_URL}/#{lenguaje}?since=daily"
      parsed_content = obtener_contenido_parseado(url)
      repositorios = parsed_content.css('div[data-hpc] article.Box-row')
      next if repositorios.empty?
      repositorios.each do |repo|
        datos = extraer_datos_repositorio(repo)
        guardar_en_csv(@archivo_top_lenguajes, [
          datos[:lenguaje],
          datos[:nombre_repo],
          datos[:nombre_user],
          datos[:url],
          datos[:estrellas],
          datos[:forks]
        ])
      end
    end
  end

  def obtener_contenido_parseado(url)
    html = URI.open(url).read
    Nokogiri::HTML(html)
  end

  def extraer_datos_repositorio(elemento)
    link_repo = elemento.css('h2 a').first
    texto_completo = link_repo.text.strip.split(" ")
    features = elemento.css('div').last

    {
      url: "#{BASE_URL}#{link_repo['href']}",
      nombre_repo: texto_completo[-1],
      nombre_user: texto_completo[0],
      lenguaje: features.at_css('span[itemprop="programmingLanguage"]')&.text&.strip || 'n/a',
      estrellas: features.css('a').first.text.strip,
      forks: features.css('a')[1].text.strip
    }
  end

  def guardar_en_csv(archivo, datos)
    CSV.open(archivo, "a+") do |csv|
      csv << datos
    end
  end
end

scraper = GithubScraper.new
scraper.ejecutar
